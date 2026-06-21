"""Endpoint integrasi Google Calendar + pemicu pengingat manual.

Fitur:
- Status koneksi + alur OAuth (connect/callback) — mode asli.
- Cari waktu rapat (FreeBusy) untuk seluruh anggota proyek.
- Jadwalkan rapat (Events.insert) + notifikasi ke anggota.
- Endpoint manual untuk menjalankan pengingat (demo on-demand).

Di mode simulasi (kredensial Google kosong) endpoint tetap berfungsi dengan
data dummy sehingga bisa di-demo tanpa biaya.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua, require_project_access
from app.models.anggota import AnggotaProyek
from app.models.enums import InvitationStatus
from app.models.proyek import Proyek
from app.models.user import User
from app.schemas.calendar import (
    CalendarStatus,
    CariWaktuRequest,
    CariWaktuResponse,
    JadwalkanRapatRequest,
)
from app.services import calendar as cal
from app.services.notifikasi.service import kirim_notifikasi
from app.services.reminder import jalankan_semua_pengingat

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


def _anggota_proyek_users(db: Session, proyek: Proyek) -> list[User]:
    """Kumpulkan user yang terlibat proyek: ketua + anggota diterima."""
    users: list[User] = []
    ketua = db.get(User, proyek.ketua_id)
    if ketua:
        users.append(ketua)
    stmt = (
        select(User)
        .join(AnggotaProyek, AnggotaProyek.user_id == User.id)
        .where(
            AnggotaProyek.proyek_id == proyek.id,
            AnggotaProyek.status_undangan == InvitationStatus.DITERIMA,
            User.deleted_at.is_(None),
        )
    )
    users.extend(db.scalars(stmt).all())
    return users


@router.get("/status", response_model=CalendarStatus)
def status_koneksi(current_user: User = Depends(get_current_user)) -> CalendarStatus:
    """Apakah akun user terhubung ke Google Calendar, & mode aktif."""
    return CalendarStatus(
        terhubung=current_user.google_token is not None,
        mode="simulasi" if cal.is_simulasi() else "asli",
    )


@router.get("/connect")
def connect(current_user: User = Depends(get_current_user)):
    """Mulai alur OAuth Google (mode asli). Di simulasi, beri info."""
    if cal.is_simulasi():
        raise HTTPException(
            status_code=400,
            detail="Mode simulasi aktif. Isi GOOGLE_CLIENT_ID/SECRET di .env untuk OAuth asli.",
        )
    url = cal.build_authorization_url(state=str(current_user.id))
    return {"authorization_url": url}


@router.get("/oauth/callback")
def oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Callback OAuth: tukar code → token, simpan ke user (mode asli)."""
    user = db.get(User, int(state))
    if user is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    user.google_token = cal.exchange_code_for_token(code)
    db.commit()
    # Arahkan kembali ke frontend.
    return RedirectResponse(url="http://localhost:5173/dashboard")


@router.post("/cari-waktu", response_model=CariWaktuResponse)
def cari_waktu(
    payload: CariWaktuRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CariWaktuResponse:
    """Cari irisan waktu kosong seluruh anggota proyek (FreeBusy)."""
    proyek = get_proyek_or_404(payload.proyek_id, db)
    # Pastikan user bagian dari proyek.
    if not (is_ketua(proyek, current_user) or any(
        u.id == current_user.id for u in _anggota_proyek_users(db, proyek)
    )):
        raise HTTPException(status_code=403, detail="Anda bukan bagian dari proyek ini.")

    users = _anggota_proyek_users(db, proyek)
    tokens = [u.google_token for u in users if u.google_token]
    slot = cal.cari_waktu_kosong(tokens, payload.mulai, payload.selesai, payload.durasi_menit)
    return CariWaktuResponse(
        mode="simulasi" if cal.is_simulasi() else "asli",
        jumlah_slot=len(slot),
        slot=slot,
    )


@router.post("/jadwalkan")
def jadwalkan_rapat(
    payload: JadwalkanRapatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Jadwalkan rapat (Events.insert) + kirim notifikasi ke anggota proyek."""
    proyek = get_proyek_or_404(payload.proyek_id, db)
    if not is_ketua(proyek, current_user):
        raise HTTPException(status_code=403, detail="Hanya ketua proyek yang menjadwalkan rapat.")

    users = _anggota_proyek_users(db, proyek)
    emails = [u.email for u in users]
    # Pakai token ketua sebagai penyelenggara (di simulasi tidak dipakai).
    token = current_user.google_token or {}

    event = cal.buat_event(token, payload.judul, payload.mulai, payload.selesai, emails)

    # Notifikasi tautan jadwal rapat ke seluruh anggota.
    for u in users:
        kirim_notifikasi(
            db, u, jenis="rapat",
            pesan=f"Rapat '{payload.judul}' dijadwalkan: {payload.mulai:%d %b %Y %H:%M}. "
                  f"Link: {event.get('html_link')}",
        )
    return event


@router.post("/jalankan-pengingat")
def jalankan_pengingat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pemicu manual semua pengingat (deadline H-1 + anggaran menipis).

    Berguna untuk demo on-demand saat sidang tanpa menunggu scheduler.
    """
    hasil = jalankan_semua_pengingat(db)
    return {"status": "selesai", "dikirim": hasil}
