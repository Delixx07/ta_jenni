"""Model InfoHibah — entri Bursa Informasi Hibah (dikelola Admin LPPM)."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class InfoHibah(Base, TimestampMixin):
    __tablename__ = "info_hibah"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Admin LPPM yang membuat entri (untuk jejak pengelola).
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    judul: Mapped[str] = mapped_column(String(255), nullable=False)
    penyelenggara: Mapped[str | None] = mapped_column(String(255), nullable=True)
    persyaratan: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    admin: Mapped["User"] = relationship(foreign_keys=[admin_id])
