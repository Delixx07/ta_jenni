"""Skema Pydantic untuk User & autentikasi (request/response)."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class UserRegister(BaseModel):
    """Payload registrasi user baru."""
    nama: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole
    program_studi: str | None = Field(default=None, max_length=150)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Representasi user yang aman dikembalikan ke klien (tanpa password_hash)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama: str
    email: EmailStr
    role: UserRole
    program_studi: str | None
    status_ketersediaan: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
