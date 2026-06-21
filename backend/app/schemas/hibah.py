"""Skema Pydantic untuk Bursa Informasi Hibah."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HibahCreate(BaseModel):
    judul: str = Field(min_length=1, max_length=255)
    penyelenggara: str | None = Field(default=None, max_length=255)
    persyaratan: str | None = None
    deadline: date | None = None


class HibahUpdate(BaseModel):
    judul: str | None = Field(default=None, max_length=255)
    penyelenggara: str | None = Field(default=None, max_length=255)
    persyaratan: str | None = None
    deadline: date | None = None


class HibahOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    judul: str
    penyelenggara: str | None
    persyaratan: str | None
    deadline: date | None
    admin_id: int
