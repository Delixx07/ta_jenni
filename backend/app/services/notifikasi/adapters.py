"""Adapter pengirim notifikasi (pola Strategy/Adapter).

Tujuannya: logika bisnis cukup memanggil `adapter.send(...)` tanpa tahu kanal
sebenarnya. Mengganti dari mode simulasi ke gateway WhatsApp asli cukup dengan
menukar adapter aktif (lihat get_adapter), tanpa mengubah service/router.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("rcms.notifikasi")


class NotificationAdapter(ABC):
    """Kontrak adapter pengirim notifikasi."""

    @abstractmethod
    def send(self, *, tujuan: str, pesan: str) -> bool:
        """Kirim pesan ke `tujuan` (mis. nomor WA). Return True bila sukses."""
        ...


class SimulasiAdapter(NotificationAdapter):
    """Mode simulasi (default): tidak memanggil layanan eksternal.

    'Mengirim' berarti mencatat ke log. Pemanggil (service) tetap menyimpan
    notifikasi ke tabel DB sehingga terlihat di UI in-app. Cocok untuk demo
    skripsi tanpa biaya/kredensial.
    """

    def send(self, *, tujuan: str, pesan: str) -> bool:
        logger.info("[SIMULASI WA] ke=%s :: %s", tujuan, pesan)
        return True


class WhatsAppGatewayAdapter(NotificationAdapter):
    """Adapter gateway WhatsApp asli (mis. Fonnte/Wablas).

    Stub: implementasi pemanggilan HTTP diisi saat kredensial tersedia.
    Disediakan agar peralihan dari simulasi ke produksi jelas & terdokumentasi.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def send(self, *, tujuan: str, pesan: str) -> bool:
        # TODO: implementasi nyata saat punya akun gateway. Contoh (Fonnte):
        #   import requests
        #   r = requests.post(self.base_url,
        #       headers={"Authorization": self.api_key},
        #       data={"target": tujuan, "message": pesan})
        #   return r.ok
        raise NotImplementedError(
            "WhatsAppGatewayAdapter belum aktif. Isi WA_API_KEY di .env "
            "dan lengkapi implementasi send() saat siap pakai gateway asli."
        )
