"""Seed data: 4 akun contoh, satu per peran.

Jalankan setelah migration:
    python -m app.seed

Idempotent: jika email sudah ada, akun dilewati (tidak diduplikasi).
Password semua akun contoh: "password123" (hanya untuk pengembangan/demo).
"""
from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.models.user import User

DEFAULT_PASSWORD = "password123"

SEED_USERS = [
    {"nama": "Dr. Ketua Peneliti", "email": "ketua@rcms.ac.id", "role": UserRole.KETUA, "program_studi": "Teknik Informatika"},
    {"nama": "Anggota Peneliti", "email": "anggota@rcms.ac.id", "role": UserRole.ANGGOTA, "program_studi": "Sistem Informasi"},
    {"nama": "Asisten Mahasiswa", "email": "asisten@rcms.ac.id", "role": UserRole.ASISTEN, "program_studi": "Teknik Informatika"},
    {"nama": "Admin LPPM", "email": "admin@rcms.ac.id", "role": UserRole.ADMIN, "program_studi": None},
]


def run() -> None:
    db = SessionLocal()
    try:
        created = 0
        for data in SEED_USERS:
            exists = db.scalar(select(User).where(User.email == data["email"]))
            if exists:
                print(f"  - lewati (sudah ada): {data['email']}")
                continue
            db.add(
                User(
                    nama=data["nama"],
                    email=data["email"],
                    password_hash=hash_password(DEFAULT_PASSWORD),
                    role=data["role"],
                    program_studi=data["program_studi"],
                )
            )
            created += 1
            print(f"  + dibuat: {data['email']} ({data['role'].value})")
        db.commit()
        print(f"\nSelesai. {created} akun baru dibuat. Password default: '{DEFAULT_PASSWORD}'")
    finally:
        db.close()


if __name__ == "__main__":
    run()
