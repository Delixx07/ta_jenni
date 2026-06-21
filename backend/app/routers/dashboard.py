"""Endpoint dashboard ringkas per peran.

Pada Fase 1 isinya masih sederhana (placeholder), namun sudah menegakkan RBAC
di backend: tiap endpoint hanya bisa diakses peran yang berwenang. Frontend
memakai data ini untuk menampilkan dashboard berbeda per peran.
"""
from fastapi import APIRouter, Depends

from app.deps.auth import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Ringkasan menu/kapabilitas per peran — dipakai frontend untuk merender dashboard.
_ROLE_SUMMARY: dict[UserRole, dict] = {
    UserRole.KETUA: {
        "judul": "Dashboard Ketua Peneliti",
        "kapabilitas": [
            "Buat & kelola proyek",
            "Cari & undang kolaborator (Smart Matchmaking)",
            "Susun RAB & bagi tugas",
        ],
    },
    UserRole.ANGGOTA: {
        "judul": "Dashboard Anggota Peneliti",
        "kapabilitas": [
            "Kerjakan tugas & isi logbook",
            "Catat pengeluaran & unggah bukti",
            "Lihat keuangan proyek",
        ],
    },
    UserRole.ASISTEN: {
        "judul": "Dashboard Asisten Mahasiswa",
        "kapabilitas": [
            "Kerjakan tugas yang didelegasikan",
            "Update progres & isi logbook",
        ],
    },
    UserRole.ADMIN: {
        "judul": "Dashboard Admin LPPM",
        "kapabilitas": [
            "Kelola data master pengguna",
            "Kelola Bursa Informasi Hibah",
        ],
    },
}


@router.get("/me")
def dashboard_me(current_user: User = Depends(get_current_user)) -> dict:
    """Ringkasan dashboard sesuai peran user yang login."""
    summary = _ROLE_SUMMARY[current_user.role]
    return {
        "nama": current_user.nama,
        "role": current_user.role.value,
        "judul": summary["judul"],
        "kapabilitas": summary["kapabilitas"],
    }


@router.get(
    "/admin-area",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def admin_only() -> dict:
    """Contoh endpoint khusus Admin LPPM — membuktikan RBAC ditegakkan di backend."""
    return {"pesan": "Area khusus Admin LPPM. Akses diizinkan."}
