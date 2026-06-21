"""Model Notifikasi — pesan untuk user (in-app & broadcast WhatsApp satu arah)."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import NotificationStatus, pg_enum

if TYPE_CHECKING:
    from app.models.user import User


class Notifikasi(Base, TimestampMixin):
    __tablename__ = "notifikasi"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Jenis bebas (mis. "deadline", "penugasan", "rapat", "anggaran") agar
    # fleksibel untuk pemicu di Fase 5; bisa dipromosikan ke enum bila stabil.
    jenis: Mapped[str] = mapped_column(String(50), nullable=False)
    pesan: Mapped[str] = mapped_column(Text, nullable=False)
    status_terkirim: Mapped[NotificationStatus] = mapped_column(
        pg_enum(NotificationStatus, "notification_status"),
        default=NotificationStatus.PENDING,
        nullable=False,
    )
    tanggal: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
