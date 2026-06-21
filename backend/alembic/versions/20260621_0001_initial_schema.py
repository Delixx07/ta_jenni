"""Initial schema — seluruh entitas RCMS (Fase 1).

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-21

Membuat 5 enum + 10 tabel dengan kolom audit (created_at, updated_at, deleted_at).
Ditulis manual agar tidak bergantung pada koneksi DB saat autogenerate.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── Definisi enum (create_type=False; dibuat eksplisit di upgrade) ──────────
user_role = postgresql.ENUM(
    "ketua", "anggota", "asisten", "admin", name="user_role", create_type=False
)
project_status = postgresql.ENUM(
    "draft", "aktif", "selesai", "dibatalkan", name="project_status", create_type=False
)
task_status = postgresql.ENUM(
    "todo", "in_progress", "done", name="task_status", create_type=False
)
invitation_status = postgresql.ENUM(
    "terkirim", "diterima", "ditolak", name="invitation_status", create_type=False
)
notification_status = postgresql.ENUM(
    "pending", "terkirim", "gagal", name="notification_status", create_type=False
)


def _audit_columns() -> list[sa.Column]:
    """Kolom audit standar dipakai semua tabel."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    bind = op.get_bind()

    # 1) Buat semua tipe enum lebih dulu.
    for enum_type in (user_role, project_status, task_status, invitation_status, notification_status):
        enum_type.create(bind, checkfirst=True)

    # 2) users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nama", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("program_studi", sa.String(150), nullable=True),
        sa.Column("status_ketersediaan", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_audit_columns(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 3) profil_kepakaran
    op.create_table(
        "profil_kepakaran",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("bidang_riset", sa.Text(), nullable=True),
        sa.Column("interest", sa.Text(), nullable=True),
        sa.Column("riwayat_penelitian", sa.Text(), nullable=True),
        sa.Column("publikasi", sa.Text(), nullable=True),
        sa.Column("keahlian_spesifik", sa.Text(), nullable=True),
        sa.Column("vektor_embedding", postgresql.JSONB(), nullable=True),
        *_audit_columns(),
    )

    # 4) proyek
    op.create_table(
        "proyek",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("judul", sa.String(255), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("ketua_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", project_status, nullable=False, server_default="draft"),
        sa.Column("tanggal_mulai", sa.Date(), nullable=True),
        sa.Column("tanggal_selesai", sa.Date(), nullable=True),
        *_audit_columns(),
    )
    op.create_index("ix_proyek_ketua_id", "proyek", ["ketua_id"])

    # 5) anggota_proyek
    op.create_table(
        "anggota_proyek",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proyek_id", sa.Integer(), sa.ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("peran_dalam_tim", sa.String(150), nullable=True),
        sa.Column("status_undangan", invitation_status, nullable=False, server_default="terkirim"),
        *_audit_columns(),
        sa.UniqueConstraint("proyek_id", "user_id", name="uq_anggota_proyek_user"),
    )
    op.create_index("ix_anggota_proyek_proyek_id", "anggota_proyek", ["proyek_id"])
    op.create_index("ix_anggota_proyek_user_id", "anggota_proyek", ["user_id"])

    # 6) tugas
    op.create_table(
        "tugas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proyek_id", sa.Integer(), sa.ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False),
        sa.Column("judul", sa.String(255), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("penanggung_jawab_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="todo"),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        *_audit_columns(),
    )
    op.create_index("ix_tugas_proyek_id", "tugas", ["proyek_id"])
    op.create_index("ix_tugas_penanggung_jawab_id", "tugas", ["penanggung_jawab_id"])

    # 7) logbook
    op.create_table(
        "logbook",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tugas_id", sa.Integer(), sa.ForeignKey("tugas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("deskripsi_kegiatan", sa.Text(), nullable=False),
        sa.Column("durasi", sa.Integer(), nullable=True),
        sa.Column("lampiran_url", sa.String(512), nullable=True),
        sa.Column("tanggal", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_logbook_tugas_id", "logbook", ["tugas_id"])
    op.create_index("ix_logbook_user_id", "logbook", ["user_id"])

    # 8) rab
    op.create_table(
        "rab",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proyek_id", sa.Integer(), sa.ForeignKey("proyek.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kategori", sa.String(150), nullable=False),
        sa.Column("jumlah_dialokasikan", sa.Numeric(15, 2), nullable=False, server_default="0"),
        *_audit_columns(),
    )
    op.create_index("ix_rab_proyek_id", "rab", ["proyek_id"])

    # 9) pengeluaran
    op.create_table(
        "pengeluaran",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rab_id", sa.Integer(), sa.ForeignKey("rab.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("jumlah", sa.Numeric(15, 2), nullable=False),
        sa.Column("deskripsi", sa.Text(), nullable=True),
        sa.Column("bukti_transaksi_url", sa.String(512), nullable=True),
        sa.Column("tanggal", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_pengeluaran_rab_id", "pengeluaran", ["rab_id"])
    op.create_index("ix_pengeluaran_user_id", "pengeluaran", ["user_id"])

    # 10) info_hibah
    op.create_table(
        "info_hibah",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("judul", sa.String(255), nullable=False),
        sa.Column("penyelenggara", sa.String(255), nullable=True),
        sa.Column("persyaratan", sa.Text(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        *_audit_columns(),
    )
    op.create_index("ix_info_hibah_admin_id", "info_hibah", ["admin_id"])

    # 11) notifikasi
    op.create_table(
        "notifikasi",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jenis", sa.String(50), nullable=False),
        sa.Column("pesan", sa.Text(), nullable=False),
        sa.Column("status_terkirim", notification_status, nullable=False, server_default="pending"),
        sa.Column("tanggal", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        *_audit_columns(),
    )
    op.create_index("ix_notifikasi_user_id", "notifikasi", ["user_id"])


def downgrade() -> None:
    # Urutan drop terbalik agar FK tidak melanggar.
    for table in (
        "notifikasi", "info_hibah", "pengeluaran", "rab",
        "logbook", "tugas", "anggota_proyek", "proyek",
        "profil_kepakaran", "users",
    ):
        op.drop_table(table)

    bind = op.get_bind()
    for enum_type in (notification_status, invitation_status, task_status, project_status, user_role):
        enum_type.drop(bind, checkfirst=True)
