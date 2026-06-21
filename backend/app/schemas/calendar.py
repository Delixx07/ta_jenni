"""Skema Pydantic untuk integrasi Google Calendar."""
from datetime import datetime

from pydantic import BaseModel, Field


class CalendarStatus(BaseModel):
    terhubung: bool
    mode: str  # "simulasi" atau "asli"


class CariWaktuRequest(BaseModel):
    proyek_id: int
    mulai: datetime
    selesai: datetime
    durasi_menit: int = Field(default=60, ge=15, le=480)


class SlotWaktu(BaseModel):
    mulai: str
    selesai: str


class CariWaktuResponse(BaseModel):
    mode: str
    jumlah_slot: int
    slot: list[SlotWaktu]


class JadwalkanRapatRequest(BaseModel):
    proyek_id: int
    judul: str = Field(min_length=1, max_length=255)
    mulai: datetime
    selesai: datetime
