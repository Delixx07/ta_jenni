"""Scheduler in-app (APScheduler) untuk pengingat otomatis.

Dijalankan di dalam proses FastAPI saat startup. Membuka session DB sendiri
tiap job (di luar siklus request) lalu menutupnya.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.reminder import jalankan_semua_pengingat

logger = logging.getLogger("rcms.scheduler")

scheduler = BackgroundScheduler(timezone="Asia/Jakarta")


def _job_pengingat() -> None:
    """Job berkala: jalankan semua pengingat dengan session DB tersendiri."""
    db = SessionLocal()
    try:
        hasil = jalankan_semua_pengingat(db)
        logger.info("Pengingat dijalankan: %s", hasil)
    except Exception:  # jangan biarkan error menjatuhkan scheduler
        logger.exception("Gagal menjalankan pengingat terjadwal")
    finally:
        db.close()


def start_scheduler() -> None:
    """Daftarkan job & mulai scheduler (dipanggil saat startup app)."""
    if scheduler.running:
        return
    # Cek tiap jam. Untuk skripsi cukup; bisa disesuaikan via cron bila perlu.
    scheduler.add_job(_job_pengingat, "interval", hours=1, id="pengingat_rcms")
    scheduler.start()
    logger.info("Scheduler RCMS dimulai (pengingat tiap 1 jam).")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
