"""Enum terpusat untuk seluruh model.

Memakai `str, enum.Enum` agar nilainya berupa string yang mudah dibaca di DB
maupun di JSON API.
"""
import enum

from sqlalchemy import Enum as SAEnum


def pg_enum(enum_cls, name: str) -> SAEnum:
    """Bangun kolom Enum SQLAlchemy yang menyimpan NILAI enum (mis. 'ketua'),
    bukan NAMA anggota ('KETUA').

    Tanpa `values_callable`, SQLAlchemy mengirim nama anggota ke PostgreSQL
    sehingga tidak cocok dengan tipe enum yang dibuat dari nilai-nilainya.
    """
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda e: [member.value for member in e],
    )


class UserRole(str, enum.Enum):
    KETUA = "ketua"        # Ketua Peneliti
    ANGGOTA = "anggota"    # Anggota Peneliti
    ASISTEN = "asisten"    # Asisten Mahasiswa
    ADMIN = "admin"        # Admin LPPM


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    AKTIF = "aktif"
    SELESAI = "selesai"
    DIBATALKAN = "dibatalkan"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class InvitationStatus(str, enum.Enum):
    TERKIRIM = "terkirim"
    DITERIMA = "diterima"
    DITOLAK = "ditolak"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    TERKIRIM = "terkirim"
    GAGAL = "gagal"
