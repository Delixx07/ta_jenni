"""Endpoint Proyek.

- Ketua Peneliti membuat & mengelola proyeknya (kontrol penuh).
- Semua user dapat melihat daftar proyek yang melibatkan dirinya
  (sebagai ketua maupun anggota yang undangannya diterima).
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.proyek import require_ketua
from app.models.anggota import AnggotaProyek
from app.models.enums import InvitationStatus, UserRole
from app.models.proyek import Proyek
from app.models.user import User
from app.schemas.proyek import ProyekCreate, ProyekOut, ProyekUpdate

router = APIRouter(prefix="/api/proyek", tags=["proyek"])


@router.get("", response_model=list[ProyekOut])
def list_proyek(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Proyek]:
    """Daftar proyek yang melibatkan user (sebagai ketua atau anggota diterima)."""
    stmt = (
        select(Proyek)
        .outerjoin(AnggotaProyek, AnggotaProyek.proyek_id == Proyek.id)
        .where(
            Proyek.deleted_at.is_(None),
            or_(
                Proyek.ketua_id == current_user.id,
                (AnggotaProyek.user_id == current_user.id)
                & (AnggotaProyek.status_undangan == InvitationStatus.DITERIMA),
            ),
        )
        .distinct()
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=ProyekOut, status_code=status.HTTP_201_CREATED)
def create_proyek(
    payload: ProyekCreate,
    current_user: User = Depends(require_roles(UserRole.KETUA)),
    db: Session = Depends(get_db),
) -> Proyek:
    """Buat proyek baru. Hanya Ketua Peneliti."""
    proyek = Proyek(
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        ketua_id=current_user.id,
        tanggal_mulai=payload.tanggal_mulai,
        tanggal_selesai=payload.tanggal_selesai,
    )
    db.add(proyek)
    db.commit()
    db.refresh(proyek)
    return proyek


@router.patch("/{proyek_id}", response_model=ProyekOut)
def update_proyek(
    payload: ProyekUpdate,
    proyek: Proyek = Depends(require_ketua),
    db: Session = Depends(get_db),
) -> Proyek:
    """Perbarui proyek. Hanya ketua proyek bersangkutan."""
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(proyek, field, value)
    db.commit()
    db.refresh(proyek)
    return proyek
