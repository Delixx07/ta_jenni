"""Utilitas penyimpanan file upload ke disk lokal.

File disimpan di folder UPLOAD_DIR dengan nama unik (UUID) agar tidak bentrok,
dan dikembalikan path relatif (mis. "/uploads/<sub>/<file>") untuk disimpan di DB
dan diakses lewat static mount di main.py.
"""
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

# Ekstensi yang diizinkan untuk bukti kerja / transaksi (gambar & dokumen umum).
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def save_upload(file: UploadFile, subdir: str) -> str:
    """Simpan file ke UPLOAD_DIR/subdir, kembalikan URL relatif untuk DB.

    Raises ValueError bila ekstensi tidak diizinkan atau ukuran melebihi batas.
    """
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Tipe file '{ext}' tidak diizinkan.")

    content = file.file.read()
    if len(content) > MAX_BYTES:
        raise ValueError("Ukuran file melebihi 5 MB.")

    target_dir = Path(settings.UPLOAD_DIR) / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    (target_dir / filename).write_bytes(content)

    # URL relatif sesuai static mount "/uploads".
    return f"/uploads/{subdir}/{filename}"
