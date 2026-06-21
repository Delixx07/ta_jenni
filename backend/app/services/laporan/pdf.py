"""Ekspor laporan proyek ke PDF (ReportLab).

Tata letak mengikuti kerangka template LPPM (placeholder yang dapat disesuaikan
pada konstanta KOP_* di bawah). Menghasilkan bytes PDF untuk diunduh.
"""
from __future__ import annotations

import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.laporan.data import LaporanData

# ── Placeholder template LPPM (silakan sesuaikan) ──────────
KOP_INSTITUSI = "LEMBAGA PENELITIAN DAN PENGABDIAN MASYARAKAT (LPPM)"
KOP_UNIVERSITAS = "Universitas [Nama Universitas]"
JUDUL_LAPORAN = "LAPORAN KEMAJUAN PENELITIAN"


def _rupiah(n) -> str:
    return "Rp " + f"{Decimal(n):,.0f}".replace(",", ".")


def buat_pdf_laporan(data: LaporanData) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    elements = []

    # Kop / header template LPPM
    elements.append(Paragraph(f"<b>{KOP_INSTITUSI}</b>", styles["Title"]))
    elements.append(Paragraph(KOP_UNIVERSITAS, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(f"<b>{JUDUL_LAPORAN}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * cm))

    # Identitas proyek
    p = data.proyek
    info = [
        ["Judul Proyek", p.judul],
        ["Ketua Peneliti", data.ketua_nama],
        ["Status", p.status.value],
        ["Periode", f"{p.tanggal_mulai or '-'} s/d {p.tanggal_selesai or '-'}"],
    ]
    t = Table(info, colWidths=[4 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Bagian Logbook ──
    elements.append(Paragraph("<b>A. Catatan Kegiatan (Logbook)</b>", styles["Heading3"]))
    log_rows = [["Tanggal", "Tugas", "Pelaksana", "Kegiatan", "Durasi"]]
    for b in data.logbook:
        log_rows.append([b.tanggal, b.tugas, b.pelaksana, b.kegiatan, b.durasi])
    if len(log_rows) == 1:
        log_rows.append(["-", "-", "-", "Belum ada entri logbook", "-"])
    log_table = Table(log_rows, colWidths=[2.6 * cm, 3 * cm, 2.8 * cm, 5.6 * cm, 2 * cm], repeatRows=1)
    log_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(log_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Bagian Keuangan ──
    elements.append(Paragraph("<b>B. Realisasi Anggaran</b>", styles["Heading3"]))
    rk = data.ringkasan_keuangan
    fin_rows = [["Kategori", "Dialokasikan", "Terpakai", "Sisa", "Sisa %"]]
    for k in rk.kategori:
        fin_rows.append([
            k.kategori, _rupiah(k.dialokasikan), _rupiah(k.terpakai),
            _rupiah(k.sisa), f"{k.persen_sisa}%",
        ])
    fin_rows.append([
        "TOTAL", _rupiah(rk.total_dialokasikan), _rupiah(rk.total_terpakai),
        _rupiah(rk.total_sisa), "",
    ])
    fin_table = Table(fin_rows, colWidths=[4.5 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 2 * cm], repeatRows=1)
    fin_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))
    elements.append(fin_table)

    doc.build(elements)
    return buf.getvalue()
