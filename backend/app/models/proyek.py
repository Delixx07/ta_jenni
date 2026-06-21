"""Model Proyek — proyek penelitian yang dipimpin seorang Ketua Peneliti."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import ProjectStatus, pg_enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.anggota import AnggotaProyek
    from app.models.tugas import Tugas
    from app.models.keuangan import RAB


class Proyek(Base, TimestampMixin):
    __tablename__ = "proyek"

    id: Mapped[int] = mapped_column(primary_key=True)
    judul: Mapped[str] = mapped_column(String(255), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    ketua_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[ProjectStatus] = mapped_column(
        pg_enum(ProjectStatus, "project_status"),
        default=ProjectStatus.DRAFT,
        nullable=False,
    )
    tanggal_mulai: Mapped[date | None] = mapped_column(Date, nullable=True)
    tanggal_selesai: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── Relasi ─────────────────────────────────────────────
    ketua: Mapped["User"] = relationship(
        back_populates="proyek_dipimpin", foreign_keys=[ketua_id]
    )
    anggota: Mapped[list["AnggotaProyek"]] = relationship(
        back_populates="proyek", cascade="all, delete-orphan"
    )
    tugas: Mapped[list["Tugas"]] = relationship(
        back_populates="proyek", cascade="all, delete-orphan"
    )
    rab: Mapped[list["RAB"]] = relationship(
        back_populates="proyek", cascade="all, delete-orphan"
    )
