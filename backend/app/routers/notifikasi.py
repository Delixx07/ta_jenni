"""Endpoint Notifikasi in-app (lonceng).

Notifikasi dibuat oleh sistem (scheduler/aksi lain) via service notifikasi.
Di sini user hanya melihat notifikasi miliknya.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.notifikasi import Notifikasi
from app.models.user import User
from app.schemas.notifikasi import NotifikasiOut

router = APIRouter(prefix="/api/notifikasi", tags=["notifikasi"])


@router.get("", response_model=list[NotifikasiOut])
def list_notifikasi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notifikasi]:
    """Daftar notifikasi milik user (terbaru dulu)."""
    stmt = (
        select(Notifikasi)
        .where(Notifikasi.user_id == current_user.id, Notifikasi.deleted_at.is_(None))
        .order_by(Notifikasi.tanggal.desc())
    )
    return list(db.scalars(stmt).all())
