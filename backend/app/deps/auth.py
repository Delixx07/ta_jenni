"""Dependency autentikasi & otorisasi (RBAC).

Otorisasi diterapkan di level backend (bukan sekadar menyembunyikan tombol di
frontend), sesuai kebutuhan non-fungsional keamanan.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

# tokenUrl menunjuk ke endpoint login (dipakai Swagger UI untuk "Authorize").
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Kredensial tidak valid atau token kedaluwarsa.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Ambil user dari JWT, dan pastikan user masih ada & belum dihapus (soft delete)."""
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise _credentials_exc

    user = db.get(User, int(payload["sub"]))
    if user is None or user.deleted_at is not None:
        raise _credentials_exc
    return user


def require_roles(*allowed_roles: UserRole):
    """Factory dependency: batasi akses endpoint ke peran tertentu.

    Contoh:
        @router.post(..., dependencies=[Depends(require_roles(UserRole.ADMIN))])
    """
    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki hak akses untuk aksi ini.",
            )
        return current_user

    return _checker
