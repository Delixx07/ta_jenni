"""Endpoint Pengeluaran — pencatatan pengeluaran riil terhadap kategori RAB.

Hak akses:
- Pencatatan: ketua atau anggota proyek (yang undangannya diterima).
- Melihat daftar pengeluaran: semua bagian tim (visibilitas keuangan menyeluruh).

Integritas data keuangan dijaga: pencatatan + simpan bukti dilakukan dalam satu
transaksi DB (commit di akhir; rollback otomatis bila terjadi error).
"""
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.storage import save_upload
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua, is_member
from app.models.keuangan import RAB, Pengeluaran
from app.models.user import User
from app.schemas.keuangan import PengeluaranOut

router = APIRouter(prefix="/api", tags=["pengeluaran"])


def _get_rab_or_404(db: Session, rab_id: int) -> RAB:
    rab = db.get(RAB, rab_id)
    if rab is None or rab.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Kategori RAB tidak ditemukan.")
    return rab


@router.get("/rab/{rab_id}/pengeluaran", response_model=list[PengeluaranOut])
def list_pengeluaran(
    rab_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Pengeluaran]:
    """Daftar pengeluaran sebuah kategori RAB. Terbuka untuk semua bagian tim."""
    rab = _get_rab_or_404(db, rab_id)
    proyek = get_proyek_or_404(rab.proyek_id, db)
    if not (is_ketua(proyek, current_user) or is_member(db, proyek.id, current_user.id)):
        raise HTTPException(status_code=403, detail="Anda bukan bagian dari proyek ini.")

    stmt = (
        select(Pengeluaran)
        .where(Pengeluaran.rab_id == rab_id, Pengeluaran.deleted_at.is_(None))
        .order_by(Pengeluaran.tanggal.desc())
    )
    return list(db.scalars(stmt).all())


@router.post(
    "/rab/{rab_id}/pengeluaran",
    response_model=PengeluaranOut,
    status_code=status.HTTP_201_CREATED,
)
def catat_pengeluaran(
    rab_id: int,
    jumlah: str = Form(...),
    deskripsi: str | None = Form(None),
    bukti: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Pengeluaran:
    """Catat pengeluaran + unggah bukti transaksi (multipart).

    Hak: ketua atau anggota proyek. Disimpan dalam satu transaksi DB.
    """
    rab = _get_rab_or_404(db, rab_id)
    proyek = get_proyek_or_404(rab.proyek_id, db)
    if not (is_ketua(proyek, current_user) or is_member(db, proyek.id, current_user.id)):
        raise HTTPException(status_code=403, detail="Anda bukan bagian dari proyek ini.")

    # Validasi nominal (dikirim sebagai string via form-data).
    try:
        nilai = Decimal(jumlah)
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=400, detail="Jumlah tidak valid.")
    if nilai <= 0:
        raise HTTPException(status_code=400, detail="Jumlah harus lebih dari 0.")

    bukti_url: str | None = None
    if bukti is not None and bukti.filename:
        try:
            bukti_url = save_upload(bukti, subdir="bukti_transaksi")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    pengeluaran = Pengeluaran(
        rab_id=rab_id,
        user_id=current_user.id,
        jumlah=nilai,
        deskripsi=deskripsi,
        bukti_transaksi_url=bukti_url,
    )
    db.add(pengeluaran)
    db.commit()  # satu transaksi: integritas data keuangan terjaga
    db.refresh(pengeluaran)
    return pengeluaran
