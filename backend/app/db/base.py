"""Base class ORM + mixin kolom audit yang dipakai semua model.

Memusatkan kolom `created_at`, `updated_at`, dan `deleted_at` (soft delete)
agar konsisten di seluruh entitas dan tidak diulang manual.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base deklaratif untuk seluruh model SQLAlchemy."""
    pass


class TimestampMixin:
    """Kolom audit waktu + soft delete.

    - created_at : diisi otomatis saat row dibuat.
    - updated_at : diperbarui otomatis setiap row diubah.
    - deleted_at : NULL berarti aktif; berisi waktu berarti "terhapus" secara
      logis. Penting untuk integritas jejak audit data keuangan & logbook
      (data tidak benar-benar dihapus dari DB).
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
