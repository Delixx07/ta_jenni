"""Endpoint autentikasi: registrasi & login (JWT)."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserOut, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    return db.scalar(stmt)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    """Daftarkan user baru. Email harus unik."""
    if _get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email sudah terdaftar.",
        )

    user = User(
        nama=payload.nama,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        program_studi=payload.program_studi,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Login dengan email (field `username`) + password, mengembalikan JWT.

    Memakai OAuth2PasswordRequestForm agar kompatibel dengan tombol Authorize
    di Swagger UI; field `username` diisi dengan email.
    """
    user = _get_user_by_email(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
        )

    token = create_access_token(subject=user.id, role=user.role.value)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Profil user yang sedang login (untuk verifikasi token & info dashboard)."""
    return current_user
