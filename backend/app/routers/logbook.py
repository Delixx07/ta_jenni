"""Endpoint Logbook — catatan kegiatan kerja terhubung ke sebuah tugas.

Setiap entri: deskripsi kegiatan, durasi (menit), dan lampiran bukti kerja
(opsional, di-upload sebagai file ke disk lokal).

Hak akses: hanya orang yang berhak atas tugas (ketua proyek atau penanggung
jawab tugas) yang dapat menambah logbook untuk tugas tersebut.
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.storage import save_upload
from app.db.session import get_db
from app.deps.auth import get_current_user
from app.deps.proyek import get_proyek_or_404, is_ketua
from app.models.logbook import Logbook
from app.models.tugas import Tugas
from app.models.user import User
from app.schemas.tugas import LogbookOut

router = APIRouter(prefix="/api", tags=["logbook"])


def _get_tugas_or_404(db: Session, tugas_id: int) -> Tugas:
    tugas = db.get(Tugas, tugas_id)
    if tugas is None or tugas.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan.")
    return tugas


@router.get("/tugas/{tugas_id}/logbook", response_model=list[LogbookOut])
def list_logbook(
    tugas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Logbook]:
    """Daftar entri logbook sebuah tugas. Untuk ketua proyek atau PJ tugas."""
    tugas = _get_tugas_or_404(db, tugas_id)
    proyek = get_proyek_or_404(tugas.proyek_id, db)
    if not (is_ketua(proyek, current_user) or tugas.penanggung_jawab_id == current_user.id):
        raise HTTPException(status_code=403, detail="Tidak berhak melihat logbook tugas ini.")

    stmt = (
        select(Logbook)
        .where(Logbook.tugas_id == tugas_id, Logbook.deleted_at.is_(None))
        .order_by(Logbook.tanggal.desc())
    )
    return list(db.scalars(stmt).all())


@router.post(
    "/tugas/{tugas_id}/logbook",
    response_model=LogbookOut,
    status_code=status.HTTP_201_CREATED,
)
def tambah_logbook(
    tugas_id: int,
    deskripsi_kegiatan: str = Form(...),
    durasi: int | None = Form(None),
    lampiran: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Logbook:
    """Tambah entri logbook (multipart, agar bisa menyertakan file lampiran).

    Hanya ketua proyek atau penanggung jawab tugas yang boleh mengisi.
    """
    tugas = _get_tugas_or_404(db, tugas_id)
    proyek = get_proyek_or_404(tugas.proyek_id, db)
    if not (is_ketua(proyek, current_user) or tugas.penanggung_jawab_id == current_user.id):
        raise HTTPException(status_code=403, detail="Tidak berhak mengisi logbook tugas ini.")

    lampiran_url: str | None = None
    if lampiran is not None and lampiran.filename:
        try:
            lampiran_url = save_upload(lampiran, subdir="logbook")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    entri = Logbook(
        tugas_id=tugas_id,
        user_id=current_user.id,
        deskripsi_kegiatan=deskripsi_kegiatan,
        durasi=durasi,
        lampiran_url=lampiran_url,
    )
    db.add(entri)
    db.commit()
    db.refresh(entri)
    return entri
