"""Endpoint Manajemen Profil Kepakaran.

Setiap kali profil disimpan/diperbarui, vektor embedding di-encode ulang dari
gabungan (bidang_riset + interest + keahlian_spesifik) agar data matchmaking
selalu sinkron dengan isi profil terbaru.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.embedding import build_profile_text, encode_text
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.profil import ProfilKepakaran
from app.models.user import User
from app.schemas.profil import ProfilOut, ProfilUpsert

router = APIRouter(prefix="/api/profil", tags=["profil"])


def _to_out(profil: ProfilKepakaran) -> ProfilOut:
    """Bentuk respons + tandai apakah vektor sudah ada (tanpa mengekspos vektornya)."""
    return ProfilOut(
        id=profil.id,
        user_id=profil.user_id,
        bidang_riset=profil.bidang_riset,
        interest=profil.interest,
        riwayat_penelitian=profil.riwayat_penelitian,
        publikasi=profil.publikasi,
        keahlian_spesifik=profil.keahlian_spesifik,
        has_embedding=profil.vektor_embedding is not None,
    )


@router.get("/me", response_model=ProfilOut | None)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfilOut | None:
    """Ambil profil kepakaran milik user yang login (None bila belum ada)."""
    profil = db.scalar(
        select(ProfilKepakaran).where(ProfilKepakaran.user_id == current_user.id)
    )
    return _to_out(profil) if profil else None


@router.put("/me", response_model=ProfilOut)
def upsert_my_profile(
    payload: ProfilUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfilOut:
    """Buat atau perbarui profil kepakaran user yang login.

    Memicu re-encoding vektor embedding dari teks kepakaran terbaru.
    """
    profil = db.scalar(
        select(ProfilKepakaran).where(ProfilKepakaran.user_id == current_user.id)
    )
    if profil is None:
        profil = ProfilKepakaran(user_id=current_user.id)
        db.add(profil)

    # Perbarui field teks.
    profil.bidang_riset = payload.bidang_riset
    profil.interest = payload.interest
    profil.riwayat_penelitian = payload.riwayat_penelitian
    profil.publikasi = payload.publikasi
    profil.keahlian_spesifik = payload.keahlian_spesifik

    # Trigger re-encoding: gabung teks relevan → encode → simpan vektor.
    teks = build_profile_text(
        payload.bidang_riset, payload.interest, payload.keahlian_spesifik
    )
    profil.vektor_embedding = encode_text(teks)  # None bila teks kosong

    db.commit()
    db.refresh(profil)
    return _to_out(profil)
