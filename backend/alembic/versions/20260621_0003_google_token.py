"""Tambah kolom users.google_token (OAuth Google Calendar) — Fase 5.

Revision ID: 0003_google_token
Revises: 0002_riwayat_undangan
Create Date: 2026-06-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_google_token"
down_revision: Union[str, None] = "0002_riwayat_undangan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_token", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "google_token")
