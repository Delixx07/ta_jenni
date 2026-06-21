"""Model RAB & Pengeluaran — manajemen anggaran penelitian.

Nilai uang memakai Numeric(15, 2) (bukan float) demi presisi keuangan.
Integritas saldo dijaga di layer service dengan transaksi DB (lihat Fase 4).
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.proyek import Proyek
    from app.models.user import User


class RAB(Base, TimestampMixin):
    """Rencana Anggaran Biaya — alokasi anggaran per kategori dalam satu proyek."""
    __tablename__ = "rab"

    id: Mapped[int] = mapped_column(primary_key=True)
    proyek_id: Mapped[int] = mapped_column(
        ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kategori: Mapped[str] = mapped_column(String(150), nullable=False)
    jumlah_dialokasikan: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0
    )

    # ── Relasi ─────────────────────────────────────────────
    proyek: Mapped["Proyek"] = relationship(back_populates="rab")
    pengeluaran: Mapped[list["Pengeluaran"]] = relationship(
        back_populates="rab", cascade="all, delete-orphan"
    )


class Pengeluaran(Base, TimestampMixin):
    """Pencatatan pengeluaran riil terhadap sebuah kategori RAB."""
    __tablename__ = "pengeluaran"

    id: Mapped[int] = mapped_column(primary_key=True)
    rab_id: Mapped[int] = mapped_column(
        ForeignKey("rab.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    jumlah: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Path/URL foto bukti transaksi (nota/kuitansi) di disk lokal.
    bukti_transaksi_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tanggal: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relasi ─────────────────────────────────────────────
    rab: Mapped["RAB"] = relationship(back_populates="pengeluaran")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
