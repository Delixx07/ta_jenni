"""SBERT embedding service untuk Smart Matchmaking.

Bertanggung jawab mengubah teks (profil kepakaran / kueri kebutuhan riset)
menjadi vektor numerik agar kemiripan semantik bisa dihitung.

Strategi performa (sesuai kebutuhan non-fungsional):
- Model dimuat **lazy** (saat pertama dipakai) lalu **di-cache** di memori,
  sehingga startup server cepat dan model hanya diunduh sekali.
- Vektor profil di-encode **saat profil disimpan** (bukan tiap kueri), lihat
  router profil. Saat matching, hanya teks kueri yang di-encode.
"""
from __future__ import annotations

import threading

# Model multilingual yang mendukung Bahasa Indonesia, dimensi 384.
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

# Cache instance model + lock agar aman dari race condition saat lazy-load.
_model = None
_model_lock = threading.Lock()


def get_model():
    """Kembalikan instance SBERT (lazy load + cache, thread-safe).

    Import `sentence_transformers` ditaruh di dalam fungsi agar dependency berat
    (torch) tidak ikut termuat saat modul lain meng-import file ini.
    """
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # double-checked locking
                from sentence_transformers import SentenceTransformer

                _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_profile_text(
    bidang_riset: str | None,
    interest: str | None,
    keahlian_spesifik: str | None,
) -> str:
    """Gabungkan field kepakaran menjadi satu teks untuk di-encode.

    Hanya field yang relevan untuk pencocokan semantik yang digabung
    (bidang riset + interest + keahlian), sesuai spesifikasi.
    """
    parts = [p.strip() for p in (bidang_riset, interest, keahlian_spesifik) if p and p.strip()]
    return ". ".join(parts)


def encode_text(text: str) -> list[float] | None:
    """Encode satu teks menjadi vektor (list float). None bila teks kosong."""
    if not text or not text.strip():
        return None
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    # Kembalikan list Python agar mudah disimpan sebagai JSONB di PostgreSQL.
    return vector.tolist()
