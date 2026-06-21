"""Endpoint Bursa Informasi Hibah.

- Membaca: semua user yang login (papan pengumuman read-only).
- Mengelola (buat/ubah/hapus): hanya Admin LPPM.
Tanpa fitur komentar (sesuai spesifikasi).
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user, require_roles
from app.models.enums import UserRole
from app.models.hibah import InfoHibah
from app.models.user import User
from app.schemas.hibah import HibahCreate, HibahOut, HibahUpdate

router = APIRouter(prefix="/api/hibah", tags=["hibah"])


def _get_or_404(db: Session, hibah_id: int) -> InfoHibah:
    h = db.get(InfoHibah, hibah_id)
    if h is None or h.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Info hibah tidak ditemukan.")
    return h


@router.get("", response_model=list[HibahOut])
def list_hibah(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InfoHibah]:
    """Daftar info hibah (terbaru/deadline terdekat). Untuk semua user login."""
    stmt = (
        select(InfoHibah)
        .where(InfoHibah.deleted_at.is_(None))
        .order_by(InfoHibah.deadline.is_(None), InfoHibah.deadline)
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=HibahOut, status_code=status.HTTP_201_CREATED)
def create_hibah(
    payload: HibahCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> InfoHibah:
    """Tambah info hibah. Hanya Admin LPPM."""
    h = InfoHibah(
        admin_id=current_user.id,
        judul=payload.judul,
        penyelenggara=payload.penyelenggara,
        persyaratan=payload.persyaratan,
        deadline=payload.deadline,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@router.patch("/{hibah_id}", response_model=HibahOut)
def update_hibah(
    hibah_id: int,
    payload: HibahUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> InfoHibah:
    """Ubah info hibah. Hanya Admin LPPM."""
    h = _get_or_404(db, hibah_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(h, field, value)
    db.commit()
    db.refresh(h)
    return h


@router.delete("/{hibah_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hibah(
    hibah_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> None:
    """Hapus (soft delete) info hibah. Hanya Admin LPPM."""
    h = _get_or_404(db, hibah_id)
    h.deleted_at = datetime.now(timezone.utc)
    db.commit()
