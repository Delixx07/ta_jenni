"""Model RiwayatUndangan — audit trail penuh perubahan status undangan tim.

Setiap perubahan status (terkirim → diterima/ditolak) dicatat sebagai baris baru
berisi status lama, status baru, aktor yang mengubah, dan waktunya. Memberikan
jejak audit lengkap sesuai kebutuhan (siapa & kapan tiap perubahan terjadi).
"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import InvitationStatus, pg_enum

if TYPE_CHECKING:
    from app.models.anggota import AnggotaProyek
    from app.models.user import User

# Satu instance enum dipakai bersama oleh kolom status_lama & status_baru.
# create_type=False: tipe "invitation_status" sudah dibuat di migration 0001.
_invitation_enum = pg_enum(InvitationStatus, "invitation_status")
_invitation_enum.create_type = False


class RiwayatUndangan(Base, TimestampMixin):
    __tablename__ = "riwayat_undangan"

    id: Mapped[int] = mapped_column(primary_key=True)
    anggota_proyek_id: Mapped[int] = mapped_column(
        ForeignKey("anggota_proyek.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Status sebelum & sesudah perubahan. status_lama NULL = pembuatan undangan.
    # Keduanya REUSE tipe enum "invitation_status" yang sama lewat satu instance
    # bersama (_invitation_enum) agar SQLAlchemy tidak mencoba membuat tipe ganda.
    status_lama: Mapped[InvitationStatus | None] = mapped_column(
        _invitation_enum, nullable=True
    )
    status_baru: Mapped[InvitationStatus] = mapped_column(
        _invitation_enum, nullable=False
    )
    # Aktor yang melakukan perubahan (ketua saat mengundang; kandidat saat respons).
    aktor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # ── Relasi ─────────────────────────────────────────────
    anggota_proyek: Mapped["AnggotaProyek"] = relationship(back_populates="riwayat")
    aktor: Mapped["User"] = relationship(foreign_keys=[aktor_id])
