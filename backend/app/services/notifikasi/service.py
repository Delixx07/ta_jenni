"""Service notifikasi: buat notifikasi, simpan ke DB, dan kirim via adapter aktif.

Setiap notifikasi SELALU disimpan ke tabel Notifikasi (terlihat di UI in-app),
lalu dikirim lewat adapter (simulasi/WA). Status_terkirim mencerminkan hasil
pengiriman kanal eksternal.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import NotificationStatus
from app.models.notifikasi import Notifikasi
from app.models.user import User
from app.services.notifikasi.adapters import (
    NotificationAdapter,
    SimulasiAdapter,
    WhatsAppGatewayAdapter,
)


def get_adapter() -> NotificationAdapter:
    """Pilih adapter aktif berdasarkan konfigurasi.

    Default: simulasi. Bila NOTIF_MODE=whatsapp dan WA_API_KEY terisi, pakai
    gateway WhatsApp asli.
    """
    if settings.NOTIF_MODE == "whatsapp" and settings.WA_API_KEY:
        return WhatsAppGatewayAdapter(settings.WA_API_KEY, settings.WA_BASE_URL)
    return SimulasiAdapter()


def kirim_notifikasi(
    db: Session,
    user: User,
    jenis: str,
    pesan: str,
    *,
    tujuan: str | None = None,
) -> Notifikasi:
    """Buat + simpan + kirim satu notifikasi untuk seorang user.

    `tujuan` (mis. nomor WA) opsional; bila kosong dipakai placeholder agar
    simulasi tetap berjalan. Status disetel sesuai hasil adapter.send().
    """
    notif = Notifikasi(
        user_id=user.id,
        jenis=jenis,
        pesan=pesan,
        status_terkirim=NotificationStatus.PENDING,
    )
    db.add(notif)
    db.flush()  # dapatkan id

    try:
        ok = get_adapter().send(tujuan=tujuan or f"user:{user.id}", pesan=pesan)
        notif.status_terkirim = (
            NotificationStatus.TERKIRIM if ok else NotificationStatus.GAGAL
        )
    except Exception:
        # Kegagalan kanal eksternal tidak boleh menggagalkan transaksi utama;
        # notifikasi tetap tersimpan dengan status GAGAL.
        notif.status_terkirim = NotificationStatus.GAGAL

    db.commit()
    db.refresh(notif)
    return notif
