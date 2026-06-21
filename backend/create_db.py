"""Helper sekali pakai: buat database `rcms` bila belum ada.

Dipakai karena `psql` tidak tersedia di PATH. Membaca kredensial dari
DATABASE_URL pada konfigurasi agar konsisten dengan aplikasi.
Jalankan: python create_db.py
"""
from urllib.parse import urlparse

import psycopg2
from psycopg2 import sql

from app.core.config import settings

# Pecah DATABASE_URL untuk ambil host/port/user/password/nama-db.
url = urlparse(settings.DATABASE_URL.replace("postgresql+psycopg2", "postgresql"))
target_db = url.path.lstrip("/")

# Koneksi ke db 'postgres' (selalu ada) untuk membuat db target.
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port or 5432,
    user=url.username,
    password=url.password,
    dbname="postgres",
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
if cur.fetchone():
    print(f"Database '{target_db}' sudah ada.")
else:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
    print(f"Database '{target_db}' dibuat.")
cur.close()
conn.close()
