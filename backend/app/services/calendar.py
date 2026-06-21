"""Integrasi Google Calendar.

Mendukung dua mode:
- SIMULASI (default, bila GOOGLE_CLIENT_ID kosong): mengembalikan data dummy yang
  realistis sehingga fitur "cari waktu rapat" & "jadwalkan rapat" bisa di-demo
  tanpa kredensial/biaya.
- ASLI (bila kredensial terisi): memakai OAuth2 + FreeBusy + Events.insert.

Privasi: untuk cari waktu rapat hanya dipakai endpoint FreeBusy (status sibuk/
luang), TIDAK membaca detail isi agenda.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.core.config import settings

# Scope minimal: baca FreeBusy + buat event. Tidak meminta baca detail acara.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]


def is_simulasi() -> bool:
    """True bila berjalan di mode simulasi (kredensial belum diisi)."""
    return not settings.GOOGLE_CLIENT_ID


# ── Mode ASLI: util kredensial ─────────────────────────────
def _build_credentials(token: dict):
    """Bangun objek Credentials Google dari token tersimpan (mode asli)."""
    from google.oauth2.credentials import Credentials

    return Credentials(
        token=token.get("token"),
        refresh_token=token.get("refresh_token"),
        token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


def _refresh_if_needed(creds, on_refresh) -> None:
    """Refresh token bila kedaluwarsa, lalu persist via callback on_refresh."""
    from google.auth.transport.requests import Request

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        on_refresh(_creds_to_dict(creds))


def _creds_to_dict(creds) -> dict:
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
    }


# ── OAuth flow (mode asli) ─────────────────────────────────
def build_authorization_url(state: str) -> str:
    """URL persetujuan OAuth untuk menghubungkan akun Google user (mode asli)."""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent", state=state
    )
    return url


def exchange_code_for_token(code: str) -> dict:
    """Tukar authorization code menjadi token (mode asli)."""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    return _creds_to_dict(flow.credentials)


# ── Cari waktu rapat (FreeBusy) ────────────────────────────
def cari_waktu_kosong(
    tokens: list[dict],
    mulai: datetime,
    selesai: datetime,
    durasi_menit: int = 60,
) -> list[dict]:
    """Cari irisan waktu kosong bersama seluruh anggota dalam rentang [mulai, selesai].

    Mode simulasi: hasilkan beberapa slot kosong dummy berbasis jam kerja.
    Mode asli: gabungkan interval 'busy' semua anggota via FreeBusy lalu cari
    celah selebar durasi_menit.
    """
    if is_simulasi():
        return _simulasi_slot(mulai, selesai, durasi_menit)

    # ── Mode asli ──
    from googleapiclient.discovery import build

    busy_intervals: list[tuple[datetime, datetime]] = []
    for token in tokens:
        creds = _build_credentials(token)
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        body = {
            "timeMin": mulai.isoformat(),
            "timeMax": selesai.isoformat(),
            "items": [{"id": "primary"}],
        }
        resp = service.freebusy().query(body=body).execute()
        for cal in resp.get("calendars", {}).values():
            for b in cal.get("busy", []):
                busy_intervals.append(
                    (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
                )

    return _celah_kosong(busy_intervals, mulai, selesai, durasi_menit)


def _simulasi_slot(mulai: datetime, selesai: datetime, durasi_menit: int) -> list[dict]:
    """Hasilkan slot kosong dummy (jam 09:00 & 13:00 tiap hari kerja)."""
    slots: list[dict] = []
    hari = mulai
    while hari.date() <= selesai.date() and len(slots) < 5:
        if hari.weekday() < 5:  # Senin–Jumat
            for jam in (9, 13):
                s = hari.replace(hour=jam, minute=0, second=0, microsecond=0)
                e = s + timedelta(minutes=durasi_menit)
                if s >= mulai and e <= selesai:
                    slots.append({"mulai": s.isoformat(), "selesai": e.isoformat()})
        hari += timedelta(days=1)
    return slots[:5]


def _celah_kosong(busy, mulai, selesai, durasi_menit):
    """Cari celah ≥ durasi di antara interval sibuk yang sudah digabung."""
    if not busy:
        return [{"mulai": mulai.isoformat(), "selesai": (mulai + timedelta(minutes=durasi_menit)).isoformat()}]
    busy.sort()
    merged = [busy[0]]
    for s, e in busy[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    slots = []
    kursor = mulai
    durasi = timedelta(minutes=durasi_menit)
    for s, e in merged:
        if s - kursor >= durasi:
            slots.append({"mulai": kursor.isoformat(), "selesai": (kursor + durasi).isoformat()})
        kursor = max(kursor, e)
    if selesai - kursor >= durasi:
        slots.append({"mulai": kursor.isoformat(), "selesai": (kursor + durasi).isoformat()})
    return slots[:5]


# ── Jadwalkan rapat (Events.insert) ────────────────────────
def buat_event(
    token: dict,
    judul: str,
    mulai: datetime,
    selesai: datetime,
    emails_peserta: list[str],
) -> dict:
    """Buat event di kalender + undang peserta. Return info event.

    Mode simulasi: kembalikan event dummy dengan link palsu.
    """
    if is_simulasi():
        return {
            "id": "sim-" + mulai.strftime("%Y%m%d%H%M"),
            "judul": judul,
            "mulai": mulai.isoformat(),
            "selesai": selesai.isoformat(),
            "peserta": emails_peserta,
            "html_link": "https://calendar.google.com/(simulasi)",
            "mode": "simulasi",
        }

    from googleapiclient.discovery import build

    creds = _build_credentials(token)
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    event = {
        "summary": judul,
        "start": {"dateTime": mulai.isoformat()},
        "end": {"dateTime": selesai.isoformat()},
        "attendees": [{"email": e} for e in emails_peserta],
    }
    created = service.events().insert(
        calendarId="primary", body=event, sendUpdates="all"
    ).execute()
    return {
        "id": created["id"],
        "judul": judul,
        "mulai": mulai.isoformat(),
        "selesai": selesai.isoformat(),
        "peserta": emails_peserta,
        "html_link": created.get("htmlLink"),
        "mode": "asli",
    }
