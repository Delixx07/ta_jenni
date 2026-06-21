"""Skema Pydantic untuk RAB & Pengeluaran + ringkasan keuangan."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ── RAB ────────────────────────────────────────────────────
class RABCreate(BaseModel):
    kategori: str = Field(min_length=1, max_length=150)
    jumlah_dialokasikan: Decimal = Field(ge=0)


class RABOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proyek_id: int
    kategori: str
    jumlah_dialokasikan: Decimal


# ── Pengeluaran ────────────────────────────────────────────
class PengeluaranOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rab_id: int
    user_id: int
    jumlah: Decimal
    deskripsi: str | None
    bukti_transaksi_url: str | None
    tanggal: datetime


# ── Ringkasan saldo per kategori ───────────────────────────
class KategoriRingkasan(BaseModel):
    """Ringkasan satu kategori RAB dengan saldo real-time & status peringatan."""
    rab_id: int
    kategori: str
    dialokasikan: Decimal
    terpakai: Decimal
    sisa: Decimal
    persen_sisa: float = Field(description="Persentase sisa terhadap alokasi (0–100)")
    peringatan_menipis: bool = Field(description="True bila sisa < 20% dari alokasi")


class RingkasanKeuangan(BaseModel):
    """Ringkasan keuangan seluruh proyek."""
    proyek_id: int
    total_dialokasikan: Decimal
    total_terpakai: Decimal
    total_sisa: Decimal
    kategori: list[KategoriRingkasan]
