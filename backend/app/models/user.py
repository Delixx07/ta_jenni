"""Model User — akun pengguna RCMS dengan 4 peran berjenjang."""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import UserRole, pg_enum

if TYPE_CHECKING:
    from app.models.profil import ProfilKepakaran
    from app.models.proyek import Proyek
    from app.models.anggota import AnggotaProyek


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nama: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        pg_enum(UserRole, "user_role"), nullable=False
    )
    program_studi: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # Penanda apakah dosen sedang terbuka untuk kolaborasi baru (dipakai matchmaking).
    status_ketersediaan: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    # Token OAuth Google (Calendar) per user. NULL = belum terhubung. (Fase 5)
    google_token: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Relasi ─────────────────────────────────────────────
    profil: Mapped["ProfilKepakaran | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    proyek_dipimpin: Mapped[list["Proyek"]] = relationship(
        back_populates="ketua", foreign_keys="Proyek.ketua_id"
    )
    keanggotaan: Mapped[list["AnggotaProyek"]] = relationship(
        back_populates="user", foreign_keys="AnggotaProyek.user_id"
    )
