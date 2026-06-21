"""Skema Pydantic untuk Proyek."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProjectStatus


class ProyekCreate(BaseModel):
    judul: str = Field(min_length=1, max_length=255)
    deskripsi: str | None = None
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None


class ProyekUpdate(BaseModel):
    judul: str | None = Field(default=None, max_length=255)
    deskripsi: str | None = None
    status: ProjectStatus | None = None
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None


class ProyekOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    judul: str
    deskripsi: str | None
    ketua_id: int
    status: ProjectStatus
    tanggal_mulai: date | None
    tanggal_selesai: date | None
