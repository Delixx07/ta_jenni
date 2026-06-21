"""Model Tugas — kartu pekerjaan pada Kanban board."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import TaskStatus, pg_enum

if TYPE_CHECKING:
    from app.models.proyek import Proyek
    from app.models.user import User
    from app.models.logbook import Logbook


class Tugas(Base, TimestampMixin):
    __tablename__ = "tugas"

    id: Mapped[int] = mapped_column(primary_key=True)
    proyek_id: Mapped[int] = mapped_column(
        ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False, index=True
    )
    judul: Mapped[str] = mapped_column(String(255), nullable=False)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Penanggung jawab boleh kosong (tugas belum di-assign).
    penanggung_jawab_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        pg_enum(TaskStatus, "task_status"),
        default=TaskStatus.TODO,
        nullable=False,
    )
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relasi ─────────────────────────────────────────────
    proyek: Mapped["Proyek"] = relationship(back_populates="tugas")
    penanggung_jawab: Mapped["User | None"] = relationship(
        foreign_keys=[penanggung_jawab_id]
    )
    logbook: Mapped[list["Logbook"]] = relationship(
        back_populates="tugas", cascade="all, delete-orphan"
    )
