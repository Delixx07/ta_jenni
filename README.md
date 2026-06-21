# RCMS — Research Collaboration and Management System

Workspace harian bagi dosen peneliti untuk menemukan kolaborator (Smart Matchmaking
SBERT), mengelola tugas & progres tim (Kanban + logbook), mengelola anggaran (RAB),
dan menghasilkan dokumentasi laporan.

> Status: **Fase 1–7 selesai & teruji end-to-end.** Seluruh fitur inti berfungsi.
> Lihat [RENCANA_IMPLEMENTASI.md](RENCANA_IMPLEMENTASI.md) untuk roadmap 7 fase,
> dan [PANDUAN_INTEGRASI_FASE5.md](PANDUAN_INTEGRASI_FASE5.md) untuk mengaktifkan
> Google Calendar / WhatsApp asli.

## Fitur (status)

| Fase | Modul | Status |
|------|-------|--------|
| 1 | Auth JWT, RBAC 4 peran, dashboard per peran | ✅ |
| 2 | Profil Kepakaran + **Smart Matchmaking (SBERT)** | ✅ |
| 3 | Proyek, **Undangan Tim** (audit trail), **Kanban** (drag-drop), Logbook | ✅ |
| 4 | **RAB & Pengeluaran** (saldo real-time, peringatan <20%, bukti) | ✅ |
| 5 | **Google Calendar** (FreeBusy/Events) + **WhatsApp** + scheduler — mode simulasi | ✅ |
| 6 | **Bursa Hibah** + **Ekspor Laporan PDF/Excel** | ✅ |
| 7 | Polish: layout konsisten, 404, error boundary, 401 auto-logout | ✅ |

## Tech Stack

| Lapisan   | Teknologi                                              |
|-----------|--------------------------------------------------------|
| Frontend  | React + Vite + Tailwind CSS                            |
| Backend   | FastAPI (Python)                                       |
| Database  | PostgreSQL                                             |
| ORM       | SQLAlchemy 2.0 + Alembic (migration)                   |
| Auth      | JWT (RBAC 4 peran: ketua / anggota / asisten / admin)  |
| ML (Fase 2) | sentence-transformers (SBERT) + scikit-learn        |

## Struktur Proyek

```
jennifer/
├── backend/        # API FastAPI
│   ├── app/
│   │   ├── core/       # config, security (hash + JWT)
│   │   ├── db/         # session + base (audit/soft-delete mixin)
│   │   ├── models/     # 10 entitas SQLAlchemy
│   │   ├── schemas/    # Pydantic
│   │   ├── deps/       # dependency auth + RBAC
│   │   ├── routers/    # auth, dashboard
│   │   ├── seed.py     # 4 akun contoh
│   │   └── main.py     # entrypoint
│   └── alembic/        # migration
└── frontend/       # React + Vite + Tailwind
```

---

## Cara Menjalankan (Lokal)

### Prasyarat
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** berjalan secara lokal

### 1) Siapkan database
Buat database kosong bernama `rcms` (sesuaikan bila perlu):
```sql
CREATE DATABASE rcms;
```

### 2) Backend

```bash
cd backend

# Buat & aktifkan virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# (Linux/macOS: source .venv/bin/activate)

# Install dependency
pip install -r requirements.txt

# Konfigurasi environment
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/macOS
# → edit .env: sesuaikan DATABASE_URL & isi JWT_SECRET_KEY dengan string acak

# Jalankan migration (membuat semua tabel)
alembic upgrade head

# Isi 4 akun contoh
python -m app.seed

# Jalankan server (http://localhost:8000)
uvicorn app.main:app --reload
```

Dokumentasi API interaktif: **http://localhost:8000/docs**

### 3) Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka **http://localhost:5173**. Vite mem-proxy `/api` ke backend di port 8000.

---

## Akun Demo

Semua memakai password **`password123`**:

| Email              | Peran             |
|--------------------|-------------------|
| ketua@rcms.ac.id    | Ketua Peneliti    |
| anggota@rcms.ac.id  | Anggota Peneliti  |
| asisten@rcms.ac.id  | Asisten Mahasiswa |
| admin@rcms.ac.id    | Admin LPPM        |

Login dengan akun berbeda untuk melihat dashboard yang berbeda per peran.

---

## Verifikasi Cepat Fase 1
- [ ] `GET /api/health` → `{"status":"ok"}`
- [ ] Login tiap akun demo berhasil & mengembalikan token + data user.
- [ ] Dashboard menampilkan judul & kapabilitas berbeda per peran.
- [ ] `GET /api/dashboard/admin-area` hanya bisa diakses akun **admin** (peran lain → 403).

---

## Push ke GitHub

Repo sudah terhubung ke `origin`. Untuk mengunggah perubahan:

```bash
git add .
git commit -m "RCMS: aplikasi lengkap + konfigurasi deploy"
git push origin main
```

> Pastikan file `.env` (berisi rahasia) TIDAK ikut ter-push — sudah diabaikan
> lewat `.gitignore`. Yang ter-push hanya `.env.example`.

---

## Deployment

Arsitektur deploy (monorepo, dua layanan):

```
┌──────────────┐      HTTPS      ┌─────────────────────┐
│  Vercel      │ ──────────────▶ │  Railway / Render   │
│  (Frontend)  │   /api/...      │  (Backend FastAPI)  │
└──────────────┘                 │  + PostgreSQL       │
                                 └─────────────────────┘
```

### Bagian 1 — Backend (Railway atau Render)

> ⚠️ Backend memuat **SBERT/torch** yang berat (~2 GB dependency + ~470 MB model).
> Pilih plan dengan **RAM memadai** (idealnya ≥ 2 GB). Tier gratis yang sangat
> kecil bisa gagal saat memuat model.

#### Opsi A — Railway (disarankan, paling mudah)
1. Buka <https://railway.app> → **New Project** → **Deploy from GitHub repo** →
   pilih repo `ta_jenni`.
2. Saat diminta root direktori service, set **Root Directory = `backend`**.
3. Tambahkan database: **New → Database → PostgreSQL**. Railway membuat variabel
   `DATABASE_URL` otomatis.
   - Jika format URL-nya `postgresql://...`, ubah `DATABASE_URL` menjadi
     `postgresql+psycopg2://...` (driver psycopg2).
4. Set **Environment Variables** lain:
   ```
   JWT_SECRET_KEY=<string acak panjang>
   CORS_ORIGINS=https://<frontend-anda>.vercel.app
   ```
   (opsional Fase 5: `NOTIF_MODE`, `GOOGLE_CLIENT_ID`, dst.)
5. Railway membaca `Procfile` → menjalankan `alembic upgrade head` lalu
   `uvicorn`. Tunggu build, salin URL publiknya
   (mis. `https://ta-jenni-backend.up.railway.app`).
6. Seed akun demo (sekali): buka **Shell** service → `python -m app.seed`.

#### Opsi B — Render
1. <https://render.com> → **New → Web Service** → connect repo.
2. **Root Directory = `backend`**, Runtime **Docker** (memakai `Dockerfile`),
   atau Python dengan start command:
   `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. **New → PostgreSQL** → salin **Internal Database URL** ke env `DATABASE_URL`
   (ubah skema ke `postgresql+psycopg2://`).
4. Set env `JWT_SECRET_KEY` & `CORS_ORIGINS` seperti di atas.
5. Setelah live, jalankan seed via **Shell**: `python -m app.seed`.

### Bagian 2 — Frontend (Vercel)

1. <https://vercel.com> → **Add New → Project** → impor repo `ta_jenni`.
2. **Root Directory = `frontend`** (Vercel mendeteksi Vite otomatis).
3. Tambahkan **Environment Variable**:
   ```
   VITE_API_BASE_URL=https://<url-backend-anda>
   ```
   (URL backend dari Railway/Render, tanpa garis miring di akhir).
4. **Deploy**, lalu salin URL Vercel (mis. `https://ta-jenni.vercel.app`).

### Bagian 3 — Hubungkan keduanya

1. Kembali ke backend → set `CORS_ORIGINS` = URL Vercel Anda → redeploy.
   Wajib, agar browser mengizinkan frontend memanggil API.
2. Buka URL Vercel → login akun demo → selesai.

### Catatan deploy
- **Upload file** (lampiran logbook, bukti transaksi) disimpan ke disk server.
  Di platform dengan filesystem *ephemeral* (tier gratis), file bisa hilang saat
  redeploy — untuk produksi gunakan object storage (S3/Cloudinary). Untuk demo
  TA, disk lokal cukup.
- **Google Calendar OAuth**: tambahkan redirect URI produksi
  (`https://<backend>/api/calendar/oauth/callback`) di Google Cloud Console bila
  mengaktifkan mode asli — lihat [PANDUAN_INTEGRASI_FASE5.md](PANDUAN_INTEGRASI_FASE5.md).
- Variabel rahasia selalu di-set lewat dashboard platform, jangan di-commit.
# ta_jenni
