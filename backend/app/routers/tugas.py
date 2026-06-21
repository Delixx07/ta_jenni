"""Endpoint Tugas (Kanban Board).

Aturan RBAC (sesuai keputusan Fase 3):
- Ketua proyek: buat/edit/hapus & pindahkan SEMUA tugas di proyeknya.
- Anggota & Asisten: hanya boleh mengubah/memindahkan tugas yang
  penanggung_jawab_id-nya = dirinya sendiri.

Melihat papan (list tugas) terbuka untuk semua bagian proyek (ketua + anggota).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua, require_project_access
from app.models.proyek import Proyek
from app.models.tugas import Tugas
from app.models.user import User
from app.schemas.tugas import TugasCreate, TugasOut, TugasStatusUpdate, TugasUpdate

router = APIRouter(prefix="/api", tags=["tugas"])


def _get_tugas_or_404(db: Session, tugas_id: int) -> Tugas:
    tugas = db.get(Tugas, tugas_id)
    if tugas is None or tugas.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan.")
    return tugas


def _assert_can_modify(db: Session, tugas: Tugas, user: User) -> None:
    """Ketua proyek boleh ubah semua tugas; selain itu hanya tugas miliknya."""
    proyek = get_proyek_or_404(tugas.proyek_id, db)
    if is_ketua(proyek, user):
        return
    if tugas.penanggung_jawab_id == user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Anda hanya dapat mengubah tugas yang ditugaskan kepada Anda.",
    )


@router.get("/proyek/{proyek_id}/tugas", response_model=list[TugasOut])
def list_tugas(
    proyek: Proyek = Depends(require_project_access),
    db: Session = Depends(get_db),
) -> list[Tugas]:
    """Daftar semua tugas (kartu Kanban) dalam proyek. Untuk bagian proyek."""
    stmt = select(Tugas).where(
        Tugas.proyek_id == proyek.id, Tugas.deleted_at.is_(None)
    )
    return list(db.scalars(stmt).all())


@router.post(
    "/proyek/{proyek_id}/tugas",
    response_model=TugasOut,
    status_code=status.HTTP_201_CREATED,
)
def create_tugas(
    proyek_id: int,
    payload: TugasCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tugas:
    """Buat kartu tugas. Hanya ketua proyek yang membagi tugas."""
    proyek = get_proyek_or_404(proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(status_code=403, detail="Hanya ketua proyek yang membagi tugas.")

    tugas = Tugas(
        proyek_id=proyek_id,
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        penanggung_jawab_id=payload.penanggung_jawab_id,
        deadline=payload.deadline,
    )
    db.add(tugas)
    db.commit()
    db.refresh(tugas)
    return tugas


@router.patch("/tugas/{tugas_id}", response_model=TugasOut)
def update_tugas(
    tugas_id: int,
    payload: TugasUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tugas:
    """Edit detail kartu tugas (judul/deskripsi/PJ/deadline)."""
    tugas = _get_tugas_or_404(db, tugas_id)
    _assert_can_modify(db, tugas, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tugas, field, value)
    db.commit()
    db.refresh(tugas)
    return tugas


@router.patch("/tugas/{tugas_id}/status", response_model=TugasOut)
def ubah_status_tugas(
    tugas_id: int,
    payload: TugasStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tugas:
    """Pindahkan kartu antar kolom Kanban (To-Do/In Progress/Done)."""
    tugas = _get_tugas_or_404(db, tugas_id)
    _assert_can_modify(db, tugas, current_user)
    tugas.status = payload.status
    db.commit()
    db.refresh(tugas)
    return tugas


@router.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(
    tugas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Hapus (soft delete) kartu tugas. Hanya ketua proyek."""
    tugas = _get_tugas_or_404(db, tugas_id)
    proyek = get_proyek_or_404(tugas.proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(status_code=403, detail="Hanya ketua proyek yang menghapus tugas.")
    from datetime import datetime, timezone

    tugas.deleted_at = datetime.now(timezone.utc)
    db.commit()
