# Panduan Integrasi Fase 5 (Google Calendar & WhatsApp)

Fase 5 berjalan **mode simulasi** secara default — semua fitur bisa di-demo
tanpa kredensial/biaya. Dokumen ini menjelaskan cara mengaktifkan integrasi
**asli** saat Anda siap.

---

## A. Mode Simulasi (default — tanpa setup)

Tanpa mengisi kredensial apa pun:
- **Google Calendar**: "cari waktu rapat" menghasilkan slot contoh (jam kerja),
  "jadwalkan rapat" membuat event dummy. Status mode = `simulasi`.
- **WhatsApp**: notifikasi "dikirim" dicatat ke log server + disimpan ke tabel
  Notifikasi (tampil di lonceng 🔔 in-app). Status = `terkirim`.

Cocok untuk demo skripsi. Di laporan, sebutkan bahwa arsitektur memakai pola
**adapter**, sehingga peralihan ke layanan asli tidak mengubah logika bisnis.

---

## B. Mengaktifkan Google Calendar (gratis)

### 1. Buat project & aktifkan API
1. Buka <https://console.cloud.google.com>.
2. Buat **Project** baru (mis. "RCMS-TA").
3. Menu **APIs & Services → Library** → cari **Google Calendar API** → **Enable**.

### 2. Konfigurasi OAuth consent screen
1. **APIs & Services → OAuth consent screen**.
2. User type: **External** → isi nama app, email, dll.
3. **Scopes**: tambahkan `calendar.events` dan `calendar.freebusy`.
4. **Test users**: tambahkan email akun Google yang dipakai demo
   (di mode "Testing" hanya akun ini yang bisa login — cukup untuk skripsi).

### 3. Buat OAuth Client ID
1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
2. Application type: **Web application**.
3. **Authorized redirect URIs**: tambahkan
   `http://localhost:8000/api/calendar/oauth/callback`
4. Salin **Client ID** & **Client secret**.

### 4. Isi `.env` backend
```
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth/callback
```
Restart backend. Status kalender otomatis berubah menjadi `asli`.

### 5. Alur pemakaian
- Tiap user menghubungkan akunnya: panggil `GET /api/calendar/connect` →
  buka `authorization_url` → setujui → token tersimpan di `users.google_token`.
- "Cari waktu" kini memakai **FreeBusy** nyata (hanya status sibuk/luang,
  tidak membaca detail agenda).
- "Jadwalkan rapat" memakai **Events.insert** + undangan ke email peserta.

> Privasi: scope sengaja dibatasi pada FreeBusy + events; isi detail acara
> pengguna lain tidak pernah dibaca.

---

## C. Mengaktifkan WhatsApp (berbayar/registrasi)

Contoh memakai **Fonnte** (gateway populer di Indonesia):

1. Daftar di <https://fonnte.com>, sambungkan perangkat WhatsApp, dapatkan
   **API token**.
2. Isi `.env`:
   ```
   NOTIF_MODE=whatsapp
   WA_API_KEY=token-fonnte-anda
   WA_BASE_URL=https://api.fonnte.com/send
   ```
3. Lengkapi implementasi `WhatsAppGatewayAdapter.send()` di
   [backend/app/services/notifikasi/adapters.py](backend/app/services/notifikasi/adapters.py)
   (sudah ada contoh kode di komentar).
4. Pastikan tiap user punya nomor WA tersimpan (perlu menambah kolom — saat ini
   tujuan memakai placeholder; bisa ditambah pada iterasi berikutnya).

> Catatan laporan: WhatsApp di sini **one-way broadcast** (pengingat/pengumuman),
> bukan chatbot dua arah, sesuai ruang lingkup proposal.

---

## D. Scheduler pengingat

- Berjalan otomatis di dalam aplikasi (APScheduler) tiap **1 jam**, memeriksa:
  - Tugas dengan deadline **H-1** → notifikasi ke penanggung jawab.
  - Kategori RAB dengan sisa **< 20%** → notifikasi ke ketua proyek.
- Untuk **demo on-demand** (tanpa menunggu), panggil:
  `POST /api/calendar/jalankan-pengingat` (atau tombol "Jalankan pengingat" di
  lonceng 🔔 dashboard).
