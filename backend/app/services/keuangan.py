"""Logika perhitungan keuangan (saldo real-time per kategori RAB).

Saldo dihitung saat dibaca (bukan disimpan) agar selalu akurat:
    sisa = jumlah_dialokasikan - SUM(pengeluaran pada kategori tsb)

Total pengeluaran per kategori diambil via agregasi SQL (SUM) agar efisien
walau jumlah transaksi banyak.
"""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.keuangan import RAB, Pengeluaran
from app.schemas.keuangan import KategoriRingkasan, RingkasanKeuangan

# Ambang peringatan: sisa anggaran di bawah 20% alokasi dianggap menipis.
AMBANG_PERINGATAN = Decimal("0.20")


def _total_terpakai_per_rab(db: Session, rab_ids: list[int]) -> dict[int, Decimal]:
    """Map rab_id -> total pengeluaran (0 bila belum ada)."""
    if not rab_ids:
        return {}
    stmt = (
        select(Pengeluaran.rab_id, func.coalesce(func.sum(Pengeluaran.jumlah), 0))
        .where(
            Pengeluaran.rab_id.in_(rab_ids),
            Pengeluaran.deleted_at.is_(None),
        )
        .group_by(Pengeluaran.rab_id)
    )
    return {rab_id: Decimal(total) for rab_id, total in db.execute(stmt).all()}


def ringkasan_keuangan(db: Session, proyek_id: int) -> RingkasanKeuangan:
    """Hitung ringkasan keuangan proyek: per kategori + total, dengan flag peringatan."""
    rabs = list(
        db.scalars(
            select(RAB).where(RAB.proyek_id == proyek_id, RAB.deleted_at.is_(None))
        ).all()
    )
    terpakai_map = _total_terpakai_per_rab(db, [r.id for r in rabs])

    kategori_list: list[KategoriRingkasan] = []
    total_alokasi = Decimal(0)
    total_terpakai = Decimal(0)

    for rab in rabs:
        dialokasikan = Decimal(rab.jumlah_dialokasikan)
        terpakai = terpakai_map.get(rab.id, Decimal(0))
        sisa = dialokasikan - terpakai

        # Persen sisa & flag menipis (hindari pembagian nol bila alokasi 0).
        if dialokasikan > 0:
            rasio_sisa = sisa / dialokasikan
            persen_sisa = round(float(rasio_sisa) * 100, 2)
            menipis = rasio_sisa < AMBANG_PERINGATAN
        else:
            persen_sisa = 0.0
            menipis = False

        kategori_list.append(
            KategoriRingkasan(
                rab_id=rab.id,
                kategori=rab.kategori,
                dialokasikan=dialokasikan,
                terpakai=terpakai,
                sisa=sisa,
                persen_sisa=persen_sisa,
                peringatan_menipis=menipis,
            )
        )
        total_alokasi += dialokasikan
        total_terpakai += terpakai

    return RingkasanKeuangan(
        proyek_id=proyek_id,
        total_dialokasikan=total_alokasi,
        total_terpakai=total_terpakai,
        total_sisa=total_alokasi - total_terpakai,
        kategori=kategori_list,
    )
