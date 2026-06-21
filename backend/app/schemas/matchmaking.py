"""Skema Pydantic untuk Smart Matchmaking."""
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    """Kueri kebutuhan riset dari Ketua Peneliti (abstrak/ide)."""
    kebutuhan_riset: str = Field(min_length=3, description="Teks abstrak/ide kebutuhan riset")


class CandidateOut(BaseModel):
    """Satu kandidat kolaborator beserta skor kemiripannya.

    `skor_kemiripan` ditampilkan eksplisit (0–100%) sebagai dasar validasi
    objektif di laporan tugas akhir.
    """
    user_id: int
    nama: str
    program_studi: str | None
    status_ketersediaan: bool
    skor_kemiripan: float = Field(description="Persentase kemiripan 0–100")


class MatchResponse(BaseModel):
    """Hasil matchmaking: daftar kandidat terurut skor tertinggi → terendah."""
    jumlah_kandidat: int
    kandidat: list[CandidateOut]
