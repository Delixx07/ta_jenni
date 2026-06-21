"""Logika pengingat otomatis (dipakai scheduler & endpoint manual).

Dua jenis pengingat:
1. Deadline tugas H-1 → notifikasi ke penanggung jawab tugas.
2. Anggaran kategori menipis (<20%) → notifikasi ke ketua proyek.

Fungsi dibuat idempotent secukupnya untuk demo: pemicu manual aman dipanggil
berulang (akan menghasilkan notifikasi baru tiap dipanggil — cukup untuk skripsi;
deduplikasi penuh bisa ditambah bila perlu).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.proyek import Proyek
from app.models.tugas import Tugas
from app.models.user import User
from app.services.keuangan import ringkasan_keuangan
from app.services.notifikasi.service import kirim_notifikasi


def ingatkan_deadline_h1(db: Session) -> int:
    """Kirim pengingat untuk tugas yang deadline-nya dalam 24 jam ke depan.

    Hanya tugas yang belum selesai & punya penanggung jawab. Return jumlah
    notifikasi yang dikirim.
    """
    sekarang = datetime.now(timezone.utc)
    besok = sekarang + timedelta(days=1)

    stmt = select(Tugas).where(
        Tugas.deleted_at.is_(None),
        Tugas.deadline.isnot(None),
        Tugas.deadline >= sekarang,
        Tugas.deadline <= besok,
        Tugas.status != TaskStatus.DONE,
        Tugas.penanggung_jawab_id.isnot(None),
    )
    terkirim = 0
    for tugas in db.scalars(stmt).all():
        pj = db.get(User, tugas.penanggung_jawab_id)
        if pj is None or pj.deleted_at is not None:
            continue
        kirim_notifikasi(
            db,
            pj,
            jenis="deadline",
            pesan=f"Pengingat: tugas '{tugas.judul}' jatuh tempo dalam 1 hari.",
        )
        terkirim += 1
    return terkirim


def ingatkan_anggaran_menipis(db: Session) -> int:
    """Kirim pengingat ke ketua untuk kategori RAB yang sisanya < 20%."""
    terkirim = 0
    proyek_list = db.scalars(select(Proyek).where(Proyek.deleted_at.is_(None))).all()
    for proyek in proyek_list:
        ringkasan = ringkasan_keuangan(db, proyek.id)
        menipis = [k for k in ringkasan.kategori if k.peringatan_menipis]
        if not menipis:
            continue
        ketua = db.get(User, proyek.ketua_id)
        if ketua is None or ketua.deleted_at is not None:
            continue
        for k in menipis:
            kirim_notifikasi(
                db,
                ketua,
                jenis="anggaran",
                pesan=(
                    f"Anggaran '{k.kategori}' pada proyek '{proyek.judul}' menipis "
                    f"(sisa {k.persen_sisa}%)."
                ),
            )
            terkirim += 1
    return terkirim


def jalankan_semua_pengingat(db: Session) -> dict[str, int]:
    """Jalankan seluruh pengingat sekali. Dipakai scheduler & endpoint manual."""
    return {
        "deadline_h1": ingatkan_deadline_h1(db),
        "anggaran_menipis": ingatkan_anggaran_menipis(db),
    }
