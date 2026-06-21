"""Skema Pydantic untuk Notifikasi."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationStatus


class NotifikasiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    jenis: str
    pesan: str
    status_terkirim: NotificationStatus
    tanggal: datetime
