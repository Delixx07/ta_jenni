"""Konfigurasi aplikasi.

Semua setting dibaca dari environment variable / file `.env` menggunakan
pydantic-settings, sehingga kredensial tidak di-hardcode dalam kode sumber.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ───────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/rcms"

    # ── JWT ────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 jam

    # ── Aplikasi ───────────────────────────────────────────
    # Disimpan sebagai string dipisah koma, diekspos sebagai list lewat property.
    CORS_ORIGINS: str = "http://localhost:5173"
    UPLOAD_DIR: str = "uploads"

    # ── Notifikasi (Fase 5) ────────────────────────────────
    # NOTIF_MODE: "simulasi" (default, gratis) atau "whatsapp" (butuh gateway).
    NOTIF_MODE: str = "simulasi"
    WA_API_KEY: str = ""
    WA_BASE_URL: str = "https://api.fonnte.com/send"

    # ── Google Calendar (Fase 5) ───────────────────────────
    # Kosongkan untuk mode simulasi (tanpa OAuth). Isi saat siap pakai API asli.
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/calendar/oauth/callback"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Daftar origin yang diizinkan untuk CORS."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cache instance Settings agar `.env` hanya dibaca sekali."""
    return Settings()


settings = get_settings()
