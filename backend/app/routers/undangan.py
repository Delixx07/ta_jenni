"""Endpoint Undangan Tim (AnggotaProyek) dengan audit trail penuh.

Alur:
- Ketua mengundang kandidat ke proyeknya (status: terkirim).
- Kandidat melihat undangan masuk, lalu menerima/menolak.
- Setiap perubahan status dicatat di tabel RiwayatUndangan
  (status_lama, status_baru, aktor, waktu).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua
from app.models.anggota import AnggotaProyek
from app.models.enums import InvitationStatus, UserRole
from app.models.riwayat_undangan import RiwayatUndangan
from app.models.user import User
from app.schemas.undangan import (
    RiwayatUndanganOut,
    UndanganCreate,
    UndanganOut,
    UndanganRespond,
)

router = APIRouter(prefix="/api", tags=["undangan"])


def _catat_riwayat(
    db: Session,
    anggota: AnggotaProyek,
    status_lama: InvitationStatus | None,
    status_baru: InvitationStatus,
    aktor_id: int,
) -> None:
    """Tambahkan satu baris audit trail untuk perubahan status undangan."""
    db.add(
        RiwayatUndangan(
            anggota_proyek_id=anggota.id,
            status_lama=status_lama,
            status_baru=status_baru,
            aktor_id=aktor_id,
        )
    )


@router.post(
    "/proyek/{proyek_id}/undangan",
    response_model=UndanganOut,
    status_code=status.HTTP_201_CREATED,
)
def undang_kandidat(
    proyek_id: int,
    payload: UndanganCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnggotaProyek:
    """Ketua mengundang seorang kandidat ke proyek (status awal: terkirim)."""
    proyek = get_proyek_or_404(proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya ketua proyek yang dapat mengundang.",
        )

    # Tidak boleh mengundang diri sendiri atau kandidat yang sudah diundang.
    if payload.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak dapat mengundang diri sendiri.")
    kandidat = db.get(User, payload.user_id)
    if kandidat is None or kandidat.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Kandidat tidak ditemukan.")

    existing = db.scalar(
        select(AnggotaProyek).where(
            AnggotaProyek.proyek_id == proyek_id,
            AnggotaProyek.user_id == payload.user_id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Kandidat sudah diundang ke proyek ini.")

    anggota = AnggotaProyek(
        proyek_id=proyek_id,
        user_id=payload.user_id,
        peran_dalam_tim=payload.peran_dalam_tim,
        status_undangan=InvitationStatus.TERKIRIM,
    )
    db.add(anggota)
    db.flush()  # agar anggota.id terisi sebelum mencatat riwayat

    _catat_riwayat(db, anggota, None, InvitationStatus.TERKIRIM, current_user.id)
    db.commit()
    db.refresh(anggota)
    return anggota


@router.get("/undangan/saya", response_model=list[UndanganOut])
def undangan_saya(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnggotaProyek]:
    """Daftar undangan yang ditujukan ke user yang login."""
    stmt = select(AnggotaProyek).where(
        AnggotaProyek.user_id == current_user.id,
        AnggotaProyek.deleted_at.is_(None),
    )
    return list(db.scalars(stmt).all())


@router.post("/undangan/{anggota_id}/respond", response_model=UndanganOut)
def respond_undangan(
    anggota_id: int,
    payload: UndanganRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnggotaProyek:
    """Kandidat menerima/menolak undangan. Tercatat di audit trail."""
    anggota = db.get(AnggotaProyek, anggota_id)
    if anggota is None or anggota.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Undangan tidak ditemukan.")
    # Hanya kandidat yang bersangkutan yang boleh merespons undangannya.
    if anggota.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ini bukan undangan Anda.")
    if anggota.status_undangan != InvitationStatus.TERKIRIM:
        raise HTTPException(status_code=409, detail="Undangan sudah direspons sebelumnya.")

    status_lama = anggota.status_undangan
    anggota.status_undangan = (
        InvitationStatus.DITERIMA if payload.terima else InvitationStatus.DITOLAK
    )
    _catat_riwayat(db, anggota, status_lama, anggota.status_undangan, current_user.id)
    db.commit()
    db.refresh(anggota)
    return anggota


@router.get("/undangan/{anggota_id}/riwayat", response_model=list[RiwayatUndanganOut])
def riwayat_undangan(
    anggota_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RiwayatUndangan]:
    """Audit trail sebuah undangan. Boleh dilihat ketua proyek atau kandidatnya."""
    anggota = db.get(AnggotaProyek, anggota_id)
    if anggota is None or anggota.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Undangan tidak ditemukan.")

    proyek = get_proyek_or_404(anggota.proyek_id, db)
    if not (is_ketua(proyek, current_user) or anggota.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Tidak berhak melihat riwayat ini.")

    stmt = (
        select(RiwayatUndangan)
        .where(RiwayatUndangan.anggota_proyek_id == anggota_id)
        .order_by(RiwayatUndangan.created_at)
    )
    return list(db.scalars(stmt).all())
