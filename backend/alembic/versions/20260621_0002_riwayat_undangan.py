"""Tambah tabel riwayat_undangan (audit trail undangan tim) — Fase 3.

Revision ID: 0002_riwayat_undangan
Revises: 0001_initial
Create Date: 2026-06-21

Catatan enum: tipe enum `invitation_status` sudah dibuat di migration 0001.
Di sini kita REUSE tipe tersebut (create_type=False) untuk kedua kolom status,
agar tidak menduplikasi tipe enum di PostgreSQL.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_riwayat_undangan"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Reuse tipe enum yang sudah ada (jangan buat ulang).
invitation_status = postgresql.ENUM(
    "terkirim", "diterima", "ditolak", name="invitation_status", create_type=False
)


def upgrade() -> None:
    op.create_table(
        "riwayat_undangan",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "anggota_proyek_id",
            sa.Integer(),
            sa.ForeignKey("anggota_proyek.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status_lama", invitation_status, nullable=True),
        sa.Column("status_baru", invitation_status, nullable=False),
        sa.Column(
            "aktor_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_riwayat_undangan_anggota_proyek_id", "riwayat_undangan", ["anggota_proyek_id"])
    op.create_index("ix_riwayat_undangan_aktor_id", "riwayat_undangan", ["aktor_id"])


def downgrade() -> None:
    op.drop_table("riwayat_undangan")
