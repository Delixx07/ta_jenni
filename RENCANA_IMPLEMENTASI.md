# Rencana Implementasi — Research Collaboration and Management System (RCMS)

> Dokumen perencanaan teknis. Disusun sebelum coding agar pembangunan bertahap,
> terstruktur, dan dapat dirujuk untuk bab Perancangan Sistem pada laporan Tugas Akhir.

---

## 1. Ringkasan Sistem

RCMS adalah workspace harian bagi dosen peneliti universitas dengan 4 fungsi inti:

1. **Smart Matchmaking** — menemukan kolaborator riset lintas prodi secara semantik (SBERT).
2. **Pengerjaan & Kolaborasi** — Kanban board + logbook terintegrasi.
3. **Manajemen Anggaran (RAB)** — alokasi anggaran & pencatatan pengeluaran + bukti.
4. **Dokumentasi & Laporan** — menghasilkan dokumentasi/laporan penelitian.

Ditambah fitur pendukung: **Bursa Informasi Hibah**, **Notifikasi (termasuk broadcast WhatsApp satu arah)**.

---

## 2. Tech Stack (sudah diputuskan)

| Lapisan          | Teknologi                                                        |
|------------------|-----------------------------------------------------------------|
| Frontend         | React + Tailwind CSS                                             |
| Backend          | Python — **FastAPI**                                             |
| Database         | PostgreSQL                                                       |
| ORM + Migration  | SQLAlchemy + Alembic                                             |
| Model ML         | `sentence-transformers` (SBERT, `paraphrase-multilingual-MiniLM-L12-v2`, dim 384) |
| Kemiripan        | `scikit-learn` `cosine_similarity` (di memori, tanpa vector DB) |
| Auth             | JWT (role-based access control)                                  |
| Notifikasi WA    | Gateway pihak ketiga (Fonnte/Wablas) — **broadcast satu arah**  |

---

## 3. Peran Pengguna & Hak Akses (RBAC)

| Peran               | Hak Utama                                                                   |
|---------------------|-----------------------------------------------------------------------------|
| **Ketua Peneliti**  | Buat proyek, cari & undang kolaborator, susun RAB, bagi tugas, kontrol penuh atas proyeknya |
| **Anggota Peneliti**| Gabung via undangan, kerjakan tugas, isi logbook, catat pengeluaran + unggah bukti |
| **Asisten Mahasiswa**| Kerjakan tugas yang **didelegasikan kepadanya saja**, update progres, isi logbook |
| **Admin LPPM**      | Kelola data master pengguna, kelola Bursa Informasi Hibah                    |

> **Prinsip kunci**: otorisasi berbasis (a) peran global, dan (b) keanggotaan/kepemilikan dalam proyek.
> Asisten hanya dapat mengubah tugas yang `penanggung_jawab_id`-nya = dirinya.

---

## 4. Skema Database (entitas final)

Berdasarkan spesifikasi entitas yang diberikan:

- **User**: id, nama, email, password_hash, role(enum), program_studi, status_ketersediaan(bool)
- **ProfilKepakaran**: id, user_id(FK), bidang_riset, interest, riwayat_penelitian, publikasi, keahlian_spesifik, vektor_embedding
- **Proyek**: id, judul, deskripsi, ketua_id(FK→User), status, tanggal_mulai, tanggal_selesai
- **AnggotaProyek**: id, proyek_id(FK), user_id(FK), peran_dalam_tim, status_undangan(enum: terkirim/diterima/ditolak)
- **Tugas**: id, proyek_id(FK), judul, deskripsi, penanggung_jawab_id(FK→User), status(enum: todo/in_progress/done), deadline
- **Logbook**: id, tugas_id(FK), user_id(FK), deskripsi_kegiatan, durasi, lampiran_url, tanggal
- **RAB**: id, proyek_id(FK), kategori, jumlah_dialokasikan
- **Pengeluaran**: id, rab_id(FK), user_id(FK), jumlah, deskripsi, bukti_transaksi_url, tanggal
- **InfoHibah**: id, admin_id(FK), judul, penyelenggara, persyaratan, deadline
- **Notifikasi**: id, user_id(FK), jenis, pesan, status_terkirim, tanggal

> **Keputusan yang masih terbuka** (lihat §8): cara simpan `vektor_embedding`, kolom audit (`created_at`/`updated_at`/soft delete), dan tabel audit-trail undangan.

---

## 5. Struktur Folder (rencana)

```
jennifer/
├── backend/
│   ├── app/
│   │   ├── main.py                 # entrypoint FastAPI
│   │   ├── core/
│   │   │   ├── config.py           # env, settings (DB URL, JWT secret, dst.)
│   │   │   ├── security.py         # hashing password, JWT
│   │   │   └── embedding.py        # SBERT service (encode profil & query)
│   │   ├── db/
│   │   │   └── session.py          # koneksi SQLAlchemy
│   │   ├── models/                 # SQLAlchemy ORM (1 file per entitas/grup)
│   │   ├── schemas/                # Pydantic (request/response)
│   │   ├── routers/                # endpoint per modul
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── profil.py
│   │   │   ├── matchmaking.py
│   │   │   ├── undangan.py
│   │   │   ├── proyek.py
│   │   │   ├── tugas.py            # Kanban
│   │   │   ├── logbook.py
│   │   │   ├── rab.py
│   │   │   ├── hibah.py
│   │   │   └── notifikasi.py
│   │   └── deps/                   # dependency: get_current_user, RBAC guards
│   ├── alembic/                    # migration
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/                    # klien REST
        ├── components/             # kartu kandidat, Kanban, dst.
        ├── pages/
        └── ...
```

---

## 6. Urutan Pembangunan — 7 Fase (sesuai BAGIAN 8 spesifikasi)

Bangun bertahap, **satu fase per satu**. Tiap fase menghasilkan sesuatu yang bisa dijalankan.

| Fase | Cakupan | Modul terkait |
|------|---------|---------------|
| **1 — Fondasi** | Setup proyek (FastAPI + React/Vite/Tailwind + PostgreSQL), skema DB & migration semua entitas, auth JWT (register/login), middleware RBAC 4 peran, dashboard kosong berbeda per peran | §4, §3 |
| **2 — Profil & Matchmaking** ⭐ | Manajemen Profil Kepakaran + trigger re-encoding SBERT, Smart Matchmaking (cosine_similarity, skor transparan). **Inti TA — prioritas & uji ketelitian.** | §7 Matchmaking |
| **3 — Tim & Tugas** | Undangan Tim (tawaran peran, terima/tolak, audit trail), Kanban Board (drag-drop, RBAC asisten), Logbook terintegrasi | §7 Undangan, Kanban+Logbook |
| **4 — Keuangan** | RAB per kategori, pencatatan pengeluaran + bukti, sisa saldo real-time, peringatan <20%, visibilitas menyeluruh | §7 Pendanaan |
| **5 — Integrasi** | Google Calendar (OAuth2, FreeBusy cari waktu rapat, Events.insert jadwalkan rapat) + WhatsApp gateway (broadcast satu arah, scheduler pengingat) | §7 Integrasi |
| **6 — Pelengkap** | Bursa Informasi Hibah (Admin LPPM, read-only publik), Ekspor Laporan PDF/Excel (template LPPM), finalisasi role management | §7 Hibah, Laporan |
| **7 — Polish** | Perbaikan UI, validasi input, penanganan error, pengujian | NFR |

---

## 7. Catatan per Modul Inti

### Smart Matchmaking (Tahap 4–5)
- **Encoding profil**: gabung `bidang_riset + interest + keahlian_spesifik` → satu string → SBERT encode → simpan `vektor_embedding`. Di-encode **saat profil disimpan/diupdate** (bukan saat matching) demi efisiensi.
- **Matching**: Ketua input "kebutuhan riset" → encode query → `cosine_similarity(query, semua vektor)` → urutkan desc.
- **Output kandidat**: nama, program_studi, **skor kemiripan (%) eksplisit**, status_ketersediaan.
- **Transparansi skor** wajib (basis validasi objektif di laporan).
- *Perlu diputuskan*: filter kandidat (exclude diri sendiri / sudah jadi anggota / hanya `status_ketersediaan=true`), ambang skor minimum, dan apakah matching terikat konteks proyek tertentu.

### Undangan Tim (Tahap 7)
- Kirim undangan ke kandidat: tawaran `peran_dalam_tim` + deskripsi tugas awal.
- Kandidat terima/tolak → update `status_undangan`.
- **Audit trail**: semua perubahan status tercatat (timestamp + aktor).

### Kanban + Logbook (Tahap 8–9)
- Kanban 3 kolom: To-Do / In Progress / Done, drag-and-drop antar kolom (update `status` Tugas).
- Kartu: judul, penanggung jawab, deadline, deskripsi.
- Logbook terhubung ke tugas: deskripsi kegiatan, durasi, lampiran foto/dokumen.
- **RBAC Asisten**: hanya bisa ubah tugas dengan `penanggung_jawab_id = dirinya`.

### Manajemen Pendanaan / RAB (Tahap 10)
- Input RAB **per kategori** oleh Ketua Peneliti (sesuai alokasi yang disetujui LPPM).
- Pencatatan pengeluaran riil oleh **anggota** + unggah foto bukti transaksi (nota/kuitansi).
- **Sisa saldo real-time per kategori** = `jumlah_dialokasikan − Σ pengeluaran` (dihitung saat baca; pertimbangkan view/agregasi).
- **Peringatan otomatis** bila sisa anggaran menipis (mis. < 20% dari alokasi kategori) → memicu Notifikasi.
- **Visibilitas keuangan sama untuk SEMUA anggota tim** — berbeda dari aturan Kanban; di modul ini asisten/anggota tetap dapat *melihat* seluruh keuangan proyek (yang dibatasi hanya hak *mencatat*). Perlu ditegaskan di RBAC.

---

### Integrasi Google Calendar (Fase 5)
- **OAuth 2.0** per user agar tiap dosen menghubungkan akun Google-nya. (Perlu panduan setup Google Cloud Console: buat project, aktifkan Calendar API, buat OAuth credentials.)
- **Cari waktu rapat**: endpoint **FreeBusy** baca rentang sibuk seluruh anggota → rekomendasi irisan waktu kosong. **Hanya status busy/free, JANGAN baca detail agenda** (privasi).
- **Jadwalkan rapat**: endpoint **Events.insert** → buat undangan kalender otomatis ke tiap anggota.
- Tangani **error & token refresh** dengan baik.

### Notifikasi WhatsApp & Scheduler (Fase 5)
- **One-way broadcast saja** (bukan chatbot) via gateway (Fonnte/Wablas/whatsapp-web.js).
- Pemicu: pengingat **H-1 deadline tugas**, penugasan baru, tautan jadwal rapat, peringatan sisa anggaran menipis.
- **Scheduler** (APScheduler/cron) untuk pengingat deadline.

### Bursa Informasi Hibah (Fase 6)
- Papan pengumuman **read-only untuk umum**, dikelola **Admin LPPM**.
- Entri: penyelenggara, persyaratan, deadline. **Tanpa komentar.**

### Ekspor Laporan Terstandarisasi (Fase 6)
- Generate **PDF & Excel** dari data logbook + keuangan.
- Tata letak mengikuti **template baku LPPM** → sediakan **placeholder template** yang bisa disesuaikan.
- **Unggah ke portal kampus tetap manual** (jangan diotomatisasi).

### Kebutuhan Non-Fungsional (Fase 7, diterapkan sepanjang)
- **Keamanan**: JWT + RBAC berjenjang, hash password, validasi input (cegah injeksi).
- **Usability**: antarmuka intuitif untuk pengguna nonteknis.
- **Kinerja**: matchmaking cepat — **pre-compute vektor profil**, jangan encode ulang tiap query.
- **Keandalan**: integritas data keuangan & logbook via **transaksi database**.
- **Kompatibilitas**: browser modern.

## 8. Keputusan Teknis yang Masih Perlu Ditetapkan

Ini akan saya tanyakan saat menyentuh tahap terkait (agar tidak menebak):

1. **Penyimpanan `vektor_embedding`**: pgvector vs JSONB/float-array. *(Rencana awal Anda: tanpa vector DB → cenderung JSONB/array.)*
2. **Kolom audit**: apakah semua tabel pakai `created_at`/`updated_at`, dan apakah perlu `deleted_at` (soft delete) khususnya untuk data keuangan.
3. **Audit trail undangan**: cukup kolom timestamp di `AnggotaProyek`, atau tabel riwayat terpisah.
4. **Penyimpanan file** (lampiran logbook, bukti transaksi): lokal disk vs cloud (S3/dsb).
5. **Gateway WhatsApp**: Fonnte vs Wablas vs `whatsapp-web.js` (memengaruhi modul notifikasi).
6. **Filter & ambang matchmaking** (lihat §7).

---

## 9. Status

- [x] Tech stack diputuskan
- [x] Rencana implementasi disusun (dokumen ini)
- [x] **Fase 1 (Fondasi)** — setup, skema DB (10 entitas), auth JWT, RBAC, seed, dashboard
- [x] **Fase 2 (Profil & Matchmaking)** — re-encoding SBERT, cosine_similarity, skor transparan
- [x] **Fase 3 (Tim & Tugas)** — proyek, undangan + audit trail, Kanban drag-drop, logbook
- [x] **Fase 4 (Keuangan)** — RAB, pengeluaran + bukti, saldo real-time, peringatan <20%
- [x] **Fase 5 (Integrasi)** — Google Calendar + WhatsApp + scheduler (mode simulasi)
- [x] **Fase 6 (Pelengkap)** — Bursa Hibah, ekspor laporan PDF/Excel
- [x] **Fase 7 (Polish)** — layout konsisten, 404, error boundary, 401 auto-logout
- **Semua fase selesai & teruji end-to-end.**
