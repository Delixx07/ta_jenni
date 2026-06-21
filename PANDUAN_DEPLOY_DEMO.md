# Panduan Deploy untuk Demo TA (Frontend Online + Backend Lokal)

Strategi **gratis total**, cocok untuk sidang:
- **Frontend** di **Vercel** (online permanen).
- **Backend** jalan di **laptop Anda**, diekspos ke internet lewat **tunnel**
  (cloudflared/ngrok) yang memberi URL publik HTTPS sementara.

```
┌──────────────┐    HTTPS     ┌──────────────┐   tunnel   ┌─────────────────┐
│  Vercel      │ ───────────▶ │  cloudflared │ ─────────▶ │ Backend lokal   │
│  (Frontend)  │              │   (URL publik)│            │ localhost:8000  │
└──────────────┘              └──────────────┘            │ + PostgreSQL    │
                                                          └─────────────────┘
```

> Kelebihan: gratis, backend berat (torch) tetap jalan di laptop yang RAM-nya
> cukup. Kekurangan: backend hanya online saat laptop & tunnel menyala (cukup
> untuk demo, bukan produksi 24/7).

---

## Langkah 1 — Deploy Frontend ke Vercel (sekali saja)

1. Push repo ke GitHub (jika belum):
   ```bash
   git add . && git commit -m "siap deploy" && git push origin main
   ```
2. Buka <https://vercel.com> → **Add New → Project** → impor repo `ta_jenni`.
3. **Root Directory = `frontend`** (Vercel mendeteksi Vite otomatis).
4. **JANGAN deploy dulu** — set Environment Variable lebih dahulu:
   ```
   VITE_API_BASE_URL = (kosongkan dulu, isi setelah punya URL tunnel di Langkah 3)
   ```
   > Atau deploy dulu, lalu set variabel & redeploy setelah dapat URL tunnel.
5. Catat URL Vercel Anda, mis. `https://ta-jenni.vercel.app`.

---

## Langkah 2 — Siapkan Backend Lokal

Pastikan backend lokal jalan (lihat CARA_MENJALANKAN.md). Ringkas:
```powershell
cd C:\Kuliah\jennifer\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```
Cek: <http://localhost:8000/api/health> → `{"status":"ok"}`.

---

## Langkah 3 — Ekspos Backend dengan Tunnel

Pilih salah satu (cloudflared disarankan: gratis, tanpa daftar, URL stabil per sesi).

### Opsi A — Cloudflare Tunnel (disarankan)
1. Unduh `cloudflared` untuk Windows:
   <https://github.com/cloudflare/cloudflared/releases> (file `cloudflared-windows-amd64.exe`),
   atau via winget:
   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
2. Jalankan tunnel ke backend:
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
3. Akan muncul URL publik, mis.
   `https://random-words-1234.trycloudflare.com`. **Salin URL ini.**

### Opsi B — ngrok
1. Daftar gratis di <https://ngrok.com>, pasang & login (authtoken sekali).
2. Jalankan:
   ```powershell
   ngrok http 8000
   ```
3. Salin URL `https://xxxx.ngrok-free.app` dari output.

---

## Langkah 4 — Hubungkan Frontend ↔ Backend

1. **Vercel** → project → **Settings → Environment Variables**:
   ```
   VITE_API_BASE_URL = https://<url-tunnel-anda>
   ```
   (tanpa garis miring di akhir), lalu **Redeploy** (Deployments → ⋯ → Redeploy).

2. **Backend lokal** → edit `backend/.env`, izinkan origin Vercel:
   ```
   CORS_ORIGINS=https://ta-jenni.vercel.app
   ```
   Lalu **restart** uvicorn agar perubahan terbaca.

3. Buka URL Vercel → login akun demo → aplikasi memanggil backend lokal Anda
   lewat tunnel. ✅

---

## Checklist Saat Sidang

Urutan menyalakan (lakukan 10–15 menit sebelum demo):
1. [ ] PostgreSQL aktif (service `postgresql-x64-18`).
2. [ ] Backend jalan: `uvicorn app.main:app --port 8000`.
3. [ ] Tunnel jalan: `cloudflared tunnel --url http://localhost:8000`.
4. [ ] URL tunnel sama dengan `VITE_API_BASE_URL` di Vercel
       (URL cloudflared berubah tiap restart — jika berubah, update di Vercel
       lalu redeploy, ATAU pakai backend langsung — lihat Plan B).
5. [ ] `CORS_ORIGINS` backend memuat URL Vercel.
6. [ ] Buka URL Vercel, tes login.

> ⚠️ URL `trycloudflare.com` gratis BERUBAH tiap kali tunnel di-restart. Agar
> tidak bolak-balik update Vercel, **nyalakan tunnel sekali** dan biarkan hidup
> selama demo. Untuk URL tetap, pakai Cloudflare Tunnel bernama (perlu domain)
> atau ngrok berbayar.

---

## Plan B (paling sederhana, tanpa Vercel)

Jika tunnel ribet saat hari-H, demo **sepenuhnya lokal** juga sah untuk TA:
```powershell
# Terminal 1
cd backend; .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
# Terminal 2
cd frontend; npm run dev
```
Buka <http://localhost:5173>. Semua fitur jalan tanpa internet. Vercel tetap
bisa Anda tunjukkan sebagai "versi online frontend".

---

## Bila Nanti Ingin Online 24/7

Lihat bagian **Deployment** di [README.md](README.md): backend ke Railway/Render
dengan plan berbayar kecil (RAM ≥ 2 GB untuk torch). Kode sudah siap (Procfile,
Dockerfile, env configurable) — tinggal pilih plan yang memadai.
