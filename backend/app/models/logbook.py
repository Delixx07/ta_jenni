"""Model Logbook — catatan kegiatan kerja yang terhubung ke sebuah tugas."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.tugas import Tugas
    from app.models.user import User


class Logbook(Base, TimestampMixin):
    __tablename__ = "logbook"

    id: Mapped[int] = mapped_column(primary_key=True)
    tugas_id: Mapped[int] = mapped_column(
        ForeignKey("tugas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    deskripsi_kegiatan: Mapped[str] = mapped_column(Text, nullable=False)
    # Durasi kerja dalam menit (lebih fleksibel untuk dijumlahkan di laporan).
    durasi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Path/URL lampiran bukti kerja (file disimpan di disk lokal, lihat UPLOAD_DIR).
    lampiran_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tanggal: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relasi ─────────────────────────────────────────────
    tugas: Mapped["Tugas"] = relationship(back_populates="logbook")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
