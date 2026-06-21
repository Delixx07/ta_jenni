"""Skema Pydantic untuk Tugas (Kanban) & Logbook."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskStatus


class TugasCreate(BaseModel):
    judul: str = Field(min_length=1, max_length=255)
    deskripsi: str | None = None
    penanggung_jawab_id: int | None = None
    deadline: datetime | None = None


class TugasUpdate(BaseModel):
    judul: str | None = Field(default=None, max_length=255)
    deskripsi: str | None = None
    penanggung_jawab_id: int | None = None
    deadline: datetime | None = None


class TugasStatusUpdate(BaseModel):
    """Perubahan kolom Kanban (drag-and-drop antar To-Do/In Progress/Done)."""
    status: TaskStatus


class TugasOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proyek_id: int
    judul: str
    deskripsi: str | None
    penanggung_jawab_id: int | None
    status: TaskStatus
    deadline: datetime | None


class LogbookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tugas_id: int
    user_id: int
    deskripsi_kegiatan: str
    durasi: int | None
    lampiran_url: str | None
    tanggal: datetime
