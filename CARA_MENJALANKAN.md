# Panduan Menjalankan RCMS (Lokal, Windows)

Dokumen ini memandu menjalankan **RCMS — Fase 1** dari nol di Windows, lengkap
dengan troubleshooting yang umum (termasuk reset password PostgreSQL).

> Ringkas: jalankan **backend** (FastAPI, port 8000) dan **frontend** (React/Vite,
> port 5173). Backend butuh **PostgreSQL** aktif.

---

## 0. Prasyarat

| Kebutuhan   | Versi      | Cek                          |
|-------------|------------|------------------------------|
| Python      | 3.11+      | `python --version`           |
| Node.js     | 18+        | `node --version`             |
| PostgreSQL  | 14+ (Anda: 17) | service `postgresql-x64-17` Running |

> Status di mesin Anda saat dokumen ini dibuat: Python 3.12 ✅, Node 24 ✅,
> PostgreSQL 17 ✅ (service berjalan). Yang tersisa: kredensial DB & migration.

---

## 1. Backend

Semua perintah dijalankan dari folder `backend/`.

### 1a. Virtual environment + dependency
> Sudah dilakukan jika Anda mengikuti sesi sebelumnya. Ulangi bila perlu.

```powershell
cd C:\Kuliah\jennifer\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Catatan: kita memanggil `.\.venv\Scripts\python.exe` secara langsung agar tidak
bergantung pada aktivasi venv (yang bisa diblokir execution policy PowerShell).
Jika ingin mengaktifkan venv:
```powershell
.\.venv\Scripts\Activate.ps1
# bila error policy:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 1b. Konfigurasi `.env`

```powershell
Copy-Item .env.example .env   # jika .env belum ada
```

Buka `backend\.env`, sesuaikan:
- `DATABASE_URL` — ganti `USER:PASSWORD` dengan kredensial PostgreSQL Anda.
  Format: `postgresql+psycopg2://postgres:PASSWORD@localhost:5432/rcms`
- `JWT_SECRET_KEY` — isi string acak. Generate cepat:
  ```powershell
  .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
  ```

### 1c. Buat database `rcms`

`psql` tidak ada di PATH Anda, jadi gunakan helper yang disediakan:
```powershell
.\.venv\Scripts\python.exe create_db.py
```
> Membaca kredensial dari `.env`, membuat database `rcms` bila belum ada.
> Jika muncul `password authentication failed`, lihat **Bagian Troubleshooting**.

### 1d. Migration (membuat semua tabel)

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```
Membuat 10 tabel + 5 enum, lengkap dengan kolom audit `created_at`,
`updated_at`, `deleted_at`.

### 1e. Seed 4 akun contoh

```powershell
.\.venv\Scripts\python.exe -m app.seed
```

### 1f. Jalankan server

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Dokumentasi interaktif (Swagger): <http://localhost:8000/docs>
- Cek kesehatan: <http://localhost:8000/api/health> → `{"status":"ok"}`

Biarkan jendela ini tetap terbuka (server berjalan di sini).

---

## 2. Frontend

Buka **jendela terminal baru** (biarkan backend tetap jalan).

```powershell
cd C:\Kuliah\jennifer\frontend
npm install
npm run dev
```

Buka <http://localhost:5173>. Vite mem-proxy `/api` ke backend (port 8000),
jadi tidak perlu konfigurasi URL tambahan.

---

## 3. Login & Uji per Peran

Akun demo (password semua: **`password123`**):

| Email              | Peran             | Yang terlihat di dashboard           |
|--------------------|-------------------|--------------------------------------|
| ketua@rcms.ac.id    | Ketua Peneliti    | Buat proyek, matchmaking, RAB, tugas |
| anggota@rcms.ac.id  | Anggota Peneliti  | Kerjakan tugas, logbook, keuangan    |
| asisten@rcms.ac.id  | Asisten Mahasiswa | Tugas didelegasikan, logbook         |
| admin@rcms.ac.id    | Admin LPPM        | Kelola pengguna, Bursa Hibah         |

Login dengan akun berbeda → dashboard berubah judul, kapabilitas, dan warna.

**Bukti RBAC ditegakkan di backend (bukan sekadar UI):**
buka <http://localhost:8000/docs> → Authorize dengan akun non-admin → panggil
`GET /api/dashboard/admin-area` → harus **403 Forbidden**. Dengan akun admin →
**200 OK**.

---

## 4. Urutan Singkat (Cheat Sheet)

```powershell
# Terminal 1 — Backend
cd C:\Kuliah\jennifer\backend
.\.venv\Scripts\python.exe create_db.py
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd C:\Kuliah\jennifer\frontend
npm install
npm run dev
```

---

## 5. Troubleshooting

### `password authentication failed for user "postgres"`
Password user `postgres` di mesin Anda berbeda dari isi `.env`.

**Cara termudah — pgAdmin 4:**
1. Buka pgAdmin 4 → Servers → PostgreSQL 17.
2. Login/Group Roles → `postgres` → Properties → tab Definition.
3. Isi Password baru → Save.
4. Samakan password tsb di `backend\.env` (bagian `DATABASE_URL`).

**Jika lupa password (reset via `pg_hba.conf`)** — jalankan di
**PowerShell sebagai Administrator**:
```powershell
$hba = "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
Copy-Item $hba "$hba.backup" -Force
(Get-Content $hba) `
  -replace '(^host\s+all\s+all\s+127\.0\.0\.1/32\s+)\S+', '$1trust' `
  -replace '(^host\s+all\s+all\s+::1/128\s+)\S+', '$1trust' |
  Set-Content $hba
Restart-Service postgresql-x64-17

# Set password baru (contoh: 'postgres')
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h 127.0.0.1 -d postgres `
  -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Kembalikan keamanan
Copy-Item "$hba.backup" $hba -Force
Restart-Service postgresql-x64-17
```
Lalu pastikan `.env` memakai password yang sama.

### `Connection refused` / `could not connect to server`
Service PostgreSQL mati. Hidupkan:
```powershell
Start-Service postgresql-x64-17
```

### `Activate.ps1 cannot be loaded ... execution policy`
Aktivasi venv diblokir. Lewati saja dengan memanggil
`.\.venv\Scripts\python.exe` langsung (seperti di panduan ini), atau:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### `alembic: target database is not up to date` / ingin mulai bersih
Rollback semua lalu migrasi ulang:
```powershell
.\.venv\Scripts\python.exe -m alembic downgrade base
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Port sudah dipakai
- Backend: `... uvicorn app.main:app --reload --port 8001`
  (lalu sesuaikan proxy di `frontend/vite.config.js`).
- Frontend: `npm run dev -- --port 5174`.

### Frontend tampil tapi login gagal / Network error
Pastikan backend berjalan di port 8000 dan `CORS_ORIGINS` di `.env`
memuat `http://localhost:5173`.

---

## 6. Menghentikan
Tekan `Ctrl + C` di masing-masing terminal (backend & frontend).
