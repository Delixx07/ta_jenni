"""Endpoint RAB (Rencana Anggaran Biaya) & ringkasan keuangan.

Hak akses:
- Hanya Ketua proyek yang menyusun/menghapus alokasi RAB.
- SEMUA bagian tim (ketua + anggota diterima) dapat MELIHAT RAB & ringkasan
  keuangan — visibilitas keuangan sama untuk semua anggota tim.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua, require_project_access
from app.models.keuangan import RAB
from app.models.proyek import Proyek
from app.models.user import User
from app.schemas.keuangan import RABCreate, RABOut, RingkasanKeuangan
from app.services.keuangan import ringkasan_keuangan

router = APIRouter(prefix="/api", tags=["rab"])


@router.get("/proyek/{proyek_id}/rab", response_model=list[RABOut])
def list_rab(
    proyek: Proyek = Depends(require_project_access),
    db: Session = Depends(get_db),
) -> list[RAB]:
    """Daftar kategori RAB proyek. Terbuka untuk semua bagian tim."""
    stmt = select(RAB).where(RAB.proyek_id == proyek.id, RAB.deleted_at.is_(None))
    return list(db.scalars(stmt).all())


@router.get("/proyek/{proyek_id}/keuangan", response_model=RingkasanKeuangan)
def ringkasan(
    proyek: Proyek = Depends(require_project_access),
    db: Session = Depends(get_db),
) -> RingkasanKeuangan:
    """Ringkasan keuangan real-time (saldo per kategori + peringatan menipis)."""
    return ringkasan_keuangan(db, proyek.id)


@router.post(
    "/proyek/{proyek_id}/rab",
    response_model=RABOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rab(
    proyek_id: int,
    payload: RABCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RAB:
    """Tambah kategori alokasi RAB. Hanya ketua proyek."""
    proyek = get_proyek_or_404(proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(status_code=403, detail="Hanya ketua proyek yang menyusun RAB.")

    rab = RAB(
        proyek_id=proyek_id,
        kategori=payload.kategori,
        jumlah_dialokasikan=payload.jumlah_dialokasikan,
    )
    db.add(rab)
    db.commit()
    db.refresh(rab)
    return rab


@router.delete("/rab/{rab_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_rab(
    rab_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Hapus (soft delete) kategori RAB. Hanya ketua proyek."""
    rab = db.get(RAB, rab_id)
    if rab is None or rab.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Kategori RAB tidak ditemukan.")
    proyek = get_proyek_or_404(rab.proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(status_code=403, detail="Hanya ketua proyek yang menghapus RAB.")
    rab.deleted_at = datetime.now(timezone.utc)
    db.commit()
