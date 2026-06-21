"""Agregasi semua model agar mudah di-import (mis. oleh Alembic & seed).

Mengimpor seluruh model di sini memastikan tabel-tabelnya terdaftar pada
metadata Base sebelum autogenerate migration dijalankan.
"""
from app.models.enums import (
    InvitationStatus,
    NotificationStatus,
    ProjectStatus,
    TaskStatus,
    UserRole,
)
from app.models.user import User
from app.models.profil import ProfilKepakaran
from app.models.proyek import Proyek
from app.models.anggota import AnggotaProyek
from app.models.riwayat_undangan import RiwayatUndangan
from app.models.tugas import Tugas
from app.models.logbook import Logbook
from app.models.keuangan import RAB, Pengeluaran
from app.models.hibah import InfoHibah
from app.models.notifikasi import Notifikasi

__all__ = [
    "UserRole",
    "ProjectStatus",
    "TaskStatus",
    "InvitationStatus",
    "NotificationStatus",
    "User",
    "ProfilKepakaran",
    "Proyek",
    "AnggotaProyek",
    "RiwayatUndangan",
    "Tugas",
    "Logbook",
    "RAB",
    "Pengeluaran",
    "InfoHibah",
    "Notifikasi",
]
