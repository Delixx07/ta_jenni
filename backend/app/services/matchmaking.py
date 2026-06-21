"""Logika Smart Matchmaking (terpisah dari endpoint agar mudah diuji).

Alur:
1. Encode teks "kebutuhan riset" menjadi vektor kueri (SBERT).
2. Ambil kandidat dosen yang valid (punya vektor profil) sesuai filter.
3. Hitung cosine similarity antara vektor kueri dan SEMUA vektor kandidat
   sekaligus (sklearn), lalu ubah ke persentase.
4. Urutkan dari skor tertinggi ke terendah.

Vektor profil sudah di-precompute saat profil disimpan, sehingga di sini tidak
ada encoding ulang profil — hanya kueri yang di-encode (efisien).
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.embedding import encode_text
from app.models.enums import UserRole
from app.models.profil import ProfilKepakaran
from app.models.user import User
from app.schemas.matchmaking import CandidateOut


def _eligible_candidates(db: Session, requester_id: int) -> list[tuple[User, ProfilKepakaran]]:
    """Ambil pasangan (user, profil) kandidat yang memenuhi filter:

    - bukan diri sendiri (requester)
    - status_ketersediaan = True
    - bukan Admin LPPM (bukan peneliti)
    - punya profil dengan vektor embedding (bisa dihitung kemiripannya)
    - tidak terhapus (soft delete)
    """
    stmt = (
        select(User, ProfilKepakaran)
        .join(ProfilKepakaran, ProfilKepakaran.user_id == User.id)
        .where(
            User.id != requester_id,
            User.status_ketersediaan.is_(True),
            User.role != UserRole.ADMIN,
            User.deleted_at.is_(None),
            ProfilKepakaran.deleted_at.is_(None),
            ProfilKepakaran.vektor_embedding.isnot(None),
        )
    )
    return list(db.execute(stmt).all())


def find_collaborators(db: Session, requester_id: int, kebutuhan_riset: str) -> list[CandidateOut]:
    """Kembalikan daftar kandidat kolaborator terurut berdasarkan kemiripan."""
    query_vector = encode_text(kebutuhan_riset)
    if query_vector is None:
        return []

    candidates = _eligible_candidates(db, requester_id)
    if not candidates:
        return []

    # Susun matriks vektor profil (N x dim) untuk perhitungan sekaligus.
    profile_matrix = np.array([profil.vektor_embedding for _, profil in candidates])
    query_matrix = np.array(query_vector).reshape(1, -1)

    # cosine_similarity → array (1 x N); ambil baris pertama.
    scores = cosine_similarity(query_matrix, profile_matrix)[0]

    results: list[CandidateOut] = []
    for (user, _profil), score in zip(candidates, scores):
        # Cosine similarity pada embedding ternormalisasi berada di [-1, 1];
        # clamp ke [0, 1] lalu ubah ke persentase agar transparan & terukur.
        persen = round(float(max(0.0, score)) * 100, 2)
        results.append(
            CandidateOut(
                user_id=user.id,
                nama=user.nama,
                program_studi=user.program_studi,
                status_ketersediaan=user.status_ketersediaan,
                skor_kemiripan=persen,
            )
        )

    # Urutkan skor tertinggi → terendah.
    results.sort(key=lambda c: c.skor_kemiripan, reverse=True)
    return results
