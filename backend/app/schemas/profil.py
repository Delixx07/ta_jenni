"""Skema Pydantic untuk Profil Kepakaran."""
from pydantic import BaseModel, ConfigDict


class ProfilUpsert(BaseModel):
    """Payload membuat/memperbarui profil kepakaran.

    Semua field opsional agar profil bisa diisi bertahap. Penyimpanan akan
    memicu re-encoding vektor dari gabungan bidang_riset + interest + keahlian.
    """
    bidang_riset: str | None = None
    interest: str | None = None
    riwayat_penelitian: str | None = None
    publikasi: str | None = None
    keahlian_spesifik: str | None = None


class ProfilOut(BaseModel):
    """Representasi profil yang dikembalikan ke klien.

    `vektor_embedding` sengaja TIDAK diekspos (data internal, besar, tak berguna
    bagi klien). Field `has_embedding` cukup untuk menandai profil sudah ter-encode.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bidang_riset: str | None
    interest: str | None
    riwayat_penelitian: str | None
    publikasi: str | None
    keahlian_spesifik: str | None
    has_embedding: bool
