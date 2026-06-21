"""Helper otorisasi berbasis proyek.

Selain peran global (RBAC), banyak aksi RCMS bergantung pada hubungan user
dengan proyek tertentu: apakah ia ketua proyek, atau anggota yang undangannya
sudah diterima. Helper ini dipakai router proyek/tugas/logbook.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.anggota import AnggotaProyek
from app.models.enums import InvitationStatus
from app.models.proyek import Proyek
from app.models.user import User


def get_proyek_or_404(proyek_id: int, db: Session) -> Proyek:
    proyek = db.get(Proyek, proyek_id)
    if proyek is None or proyek.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyek tidak ditemukan.")
    return proyek


def is_ketua(proyek: Proyek, user: User) -> bool:
    """True bila user adalah ketua (pemilik) proyek."""
    return proyek.ketua_id == user.id


def is_member(db: Session, proyek_id: int, user_id: int) -> bool:
    """True bila user adalah anggota proyek dengan undangan DITERIMA."""
    stmt = select(AnggotaProyek).where(
        AnggotaProyek.proyek_id == proyek_id,
        AnggotaProyek.user_id == user_id,
        AnggotaProyek.status_undangan == InvitationStatus.DITERIMA,
        AnggotaProyek.deleted_at.is_(None),
    )
    return db.scalar(stmt) is not None


def require_project_access(
    proyek_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Proyek:
    """Dependency: pastikan user adalah ketua ATAU anggota proyek (boleh melihat)."""
    proyek = get_proyek_or_404(proyek_id, db)
    if is_ketua(proyek, current_user) or is_member(db, proyek_id, current_user.id):
        return proyek
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Anda bukan bagian dari proyek ini.",
    )


def require_ketua(
    proyek_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Proyek:
    """Dependency: pastikan user adalah ketua proyek (untuk aksi kontrol penuh)."""
    proyek = get_proyek_or_404(proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya ketua proyek yang dapat melakukan aksi ini.",
        )
    return proyek
