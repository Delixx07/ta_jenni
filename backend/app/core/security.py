"""Utilitas keamanan: hashing password dan pembuatan/verifikasi JWT.

Dipisahkan dari logika endpoint agar mudah diuji dan dipakai ulang.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def _to_bytes(password: str) -> bytes:
    """Encode password ke bytes, dipotong ke 72 byte (batas keras algoritma bcrypt).

    Memakai library bcrypt langsung (bukan passlib) untuk kompatibilitas dengan
    bcrypt 4/5; passlib lama bergantung pada atribut internal yang sudah dihapus.
    """
    return password.encode("utf-8")[:72]


def hash_password(plain_password: str) -> str:
    """Hash password plaintext menjadi bentuk yang aman disimpan."""
    return bcrypt.hashpw(_to_bytes(plain_password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Bandingkan password input dengan hash tersimpan."""
    return bcrypt.checkpw(_to_bytes(plain_password), hashed_password.encode("utf-8"))


def create_access_token(subject: str | int, role: str) -> str:
    """Buat JWT berisi identitas user (sub) dan perannya (role).

    `role` disertakan dalam token agar middleware RBAC bisa memeriksa hak akses
    tanpa selalu query database, namun keberadaan user tetap divalidasi saat
    request (lihat deps/auth.py).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode & verifikasi JWT. Mengembalikan payload, atau None bila tidak valid."""
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None
