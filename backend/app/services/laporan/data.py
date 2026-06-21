"""Pengumpulan data laporan per proyek (dipakai ekspor PDF & Excel).

Memusatkan query agar kedua format ekspor memakai sumber data yang sama.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.logbook import Logbook
from app.models.proyek import Proyek
from app.models.tugas import Tugas
from app.models.user import User
from app.services.keuangan import ringkasan_keuangan


@dataclass
class BarisLogbook:
    tanggal: str
    tugas: str
    pelaksana: str
    kegiatan: str
    durasi: str


@dataclass
class LaporanData:
    proyek: Proyek
    ketua_nama: str
    logbook: list[BarisLogbook] = field(default_factory=list)
    ringkasan_keuangan: object = None  # RingkasanKeuangan


def kumpulkan_data_laporan(db: Session, proyek: Proyek) -> LaporanData:
    """Kumpulkan data laporan (logbook + keuangan) untuk satu proyek."""
    ketua = db.get(User, proyek.ketua_id)

    # Logbook seluruh tugas dalam proyek (join tugas → logbook → user pelaksana).
    stmt = (
        select(Logbook, Tugas.judul, User.nama)
        .join(Tugas, Tugas.id == Logbook.tugas_id)
        .join(User, User.id == Logbook.user_id)
        .where(Tugas.proyek_id == proyek.id, Logbook.deleted_at.is_(None))
        .order_by(Logbook.tanggal)
    )
    baris = []
    for log, judul_tugas, nama_pelaksana in db.execute(stmt).all():
        baris.append(
            BarisLogbook(
                tanggal=log.tanggal.strftime("%d-%m-%Y %H:%M"),
                tugas=judul_tugas,
                pelaksana=nama_pelaksana,
                kegiatan=log.deskripsi_kegiatan,
                durasi=f"{log.durasi} menit" if log.durasi is not None else "-",
            )
        )

    return LaporanData(
        proyek=proyek,
        ketua_nama=ketua.nama if ketua else "-",
        logbook=baris,
        ringkasan_keuangan=ringkasan_keuangan(db, proyek.id),
    )
