"""Endpoint Ekspor Laporan per proyek (PDF & Excel).

Akses: bagian dari proyek (ketua atau anggota diterima) — lihat
require_project_access. Unggah ke portal kampus tetap manual (tidak otomatis).
"""
import re

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.proyek import require_project_access
from app.models.proyek import Proyek
from app.services.laporan.data import kumpulkan_data_laporan
from app.services.laporan.excel import buat_excel_laporan
from app.services.laporan.pdf import buat_pdf_laporan

router = APIRouter(prefix="/api", tags=["laporan"])


def _slug(text: str) -> str:
    """Nama file aman dari judul proyek."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")[:40] or "proyek"


@router.get("/proyek/{proyek_id}/laporan/pdf")
def ekspor_pdf(
    proyek: Proyek = Depends(require_project_access),
    db: Session = Depends(get_db),
) -> Response:
    """Unduh laporan proyek (logbook + keuangan) dalam format PDF."""
    data = kumpulkan_data_laporan(db, proyek)
    pdf = buat_pdf_laporan(data)
    nama = f"laporan_{_slug(proyek.judul)}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nama}"'},
    )


@router.get("/proyek/{proyek_id}/laporan/excel")
def ekspor_excel(
    proyek: Proyek = Depends(require_project_access),
    db: Session = Depends(get_db),
) -> Response:
    """Unduh laporan proyek (logbook + keuangan) dalam format Excel (.xlsx)."""
    data = kumpulkan_data_laporan(db, proyek)
    xlsx = buat_excel_laporan(data)
    nama = f"laporan_{_slug(proyek.judul)}.xlsx"
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nama}"'},
    )
