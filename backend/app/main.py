"""Entrypoint aplikasi FastAPI untuk RCMS."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.routers import (
    auth,
    calendar,
    dashboard,
    hibah,
    laporan,
    logbook,
    matchmaking,
    notifikasi,
    pengeluaran,
    profil,
    proyek,
    rab,
    tugas,
    undangan,
)

app = FastAPI(
    title="RCMS API",
    description="Research Collaboration and Management System",
    version="0.1.0",
)


@app.on_event("startup")
def _on_startup() -> None:
    """Mulai scheduler pengingat saat aplikasi nyala."""
    start_scheduler()


@app.on_event("shutdown")
def _on_shutdown() -> None:
    shutdown_scheduler()

# CORS agar frontend (React/Vite) dapat memanggil API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder upload lokal (lampiran logbook & bukti transaksi) diekspos sebagai static.
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# ── Registrasi router ──────────────────────────────────────
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(profil.router)
app.include_router(matchmaking.router)
app.include_router(proyek.router)
app.include_router(undangan.router)
app.include_router(tugas.router)
app.include_router(logbook.router)
app.include_router(rab.router)
app.include_router(pengeluaran.router)
app.include_router(notifikasi.router)
app.include_router(calendar.router)
app.include_router(hibah.router)
app.include_router(laporan.router)


@app.get("/api/health", tags=["health"])
def health_check() -> dict:
    """Cek sederhana bahwa API hidup."""
    return {"status": "ok"}
