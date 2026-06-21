"""Model AnggotaProyek — keanggotaan + undangan tim (dengan status untuk audit)."""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import InvitationStatus, pg_enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.proyek import Proyek
    from app.models.riwayat_undangan import RiwayatUndangan


class AnggotaProyek(Base, TimestampMixin):
    __tablename__ = "anggota_proyek"
    # Satu user tidak diundang dua kali ke proyek yang sama.
    __table_args__ = (
        UniqueConstraint("proyek_id", "user_id", name="uq_anggota_proyek_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    proyek_id: Mapped[int] = mapped_column(
        ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    peran_dalam_tim: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status_undangan: Mapped[InvitationStatus] = mapped_column(
        pg_enum(InvitationStatus, "invitation_status"),
        default=InvitationStatus.TERKIRIM,
        nullable=False,
    )

    # Perubahan status (terkirim → diterima/ditolak) terekam lewat `updated_at`
    # dari TimestampMixin sebagai audit trail dasar. Bila diperlukan riwayat
    # penuh, dapat ditambah tabel log terpisah pada Fase 3.

    # ── Relasi ─────────────────────────────────────────────
    proyek: Mapped["Proyek"] = relationship(back_populates="anggota")
    user: Mapped["User"] = relationship(
        back_populates="keanggotaan", foreign_keys=[user_id]
    )
    riwayat: Mapped[list["RiwayatUndangan"]] = relationship(
        back_populates="anggota_proyek", cascade="all, delete-orphan"
    )
