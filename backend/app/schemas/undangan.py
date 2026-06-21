"""Skema Pydantic untuk Undangan Tim (AnggotaProyek) + audit trail."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import InvitationStatus


class UndanganCreate(BaseModel):
    """Ketua mengundang seorang kandidat ke sebuah proyek."""
    user_id: int                       # kandidat yang diundang
    peran_dalam_tim: str | None = None  # tawaran peran


class UndanganRespond(BaseModel):
    """Kandidat merespons undangan: terima atau tolak."""
    terima: bool


class UndanganOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proyek_id: int
    user_id: int
    peran_dalam_tim: str | None
    status_undangan: InvitationStatus


class RiwayatUndanganOut(BaseModel):
    """Satu baris audit trail perubahan status undangan."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status_lama: InvitationStatus | None
    status_baru: InvitationStatus
    aktor_id: int
    created_at: datetime
