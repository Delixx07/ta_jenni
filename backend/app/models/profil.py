"""Model ProfilKepakaran — data kepakaran dosen + vektor embedding SBERT."""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ProfilKepakaran(Base, TimestampMixin):
    __tablename__ = "profil_kepakaran"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    bidang_riset: Mapped[str | None] = mapped_column(Text, nullable=True)
    interest: Mapped[str | None] = mapped_column(Text, nullable=True)
    riwayat_penelitian: Mapped[str | None] = mapped_column(Text, nullable=True)
    publikasi: Mapped[str | None] = mapped_column(Text, nullable=True)
    keahlian_spesifik: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Vektor embedding SBERT (array float, dim 384) disimpan sebagai JSONB.
    # Diisi/diperbarui otomatis saat profil disimpan (lihat Fase 2).
    # Cosine similarity dihitung di Python (scikit-learn), bukan di DB.
    vektor_embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profil")
