# Panduan Pengguna & Tutorial RCMS

Dokumen ini berisi: (A) daftar dokumentasi proyek yang perlu Anda cek, dan
(B) tutorial langkah-demi-langkah semua hal yang bisa dilakukan di web RCMS.
Cocok juga sebagai skenario demo saat sidang Tugas Akhir.

---

## A. Dokumentasi yang Perlu Dicek

Urutkan membaca dari atas ke bawah:

| # | Dokumen | Isi | Kapan dibaca |
|---|---------|-----|--------------|
| 1 | [README.md](README.md) | Ringkasan sistem, tech stack, status fitur, akun demo | Pertama, untuk gambaran umum |
| 2 | [CARA_MENJALANKAN.md](CARA_MENJALANKAN.md) | Langkah menjalankan backend + frontend di lokal, troubleshooting | Saat ingin menjalankan aplikasi |
| 3 | [RENCANA_IMPLEMENTASI.md](RENCANA_IMPLEMENTASI.md) | Arsitektur, 7 fase pembangunan, skema database, keputusan teknis | Untuk bab Perancangan laporan TA |
| 4 | [PANDUAN_INTEGRASI_FASE5.md](PANDUAN_INTEGRASI_FASE5.md) | Cara mengaktifkan Google Calendar & WhatsApp asli (default: simulasi) | Saat ingin integrasi nyata |
| 5 | **PANDUAN_PENGGUNA.md** (dokumen ini) | Tutorial pemakaian per fitur & per peran | Untuk demo & uji coba |

**Dokumentasi API interaktif (Swagger):** saat backend jalan, buka
<http://localhost:8000/docs> — berisi semua endpoint, bisa dicoba langsung.

---

## B. Persiapan Sebelum Tutorial

1. Pastikan **backend** jalan: `http://localhost:8000/api/health` → `{"status":"ok"}`
2. Pastikan **frontend** jalan: buka <http://localhost:5173>
3. Akun demo (password semua: **`password123`**):

| Email | Peran | Fokus |
|-------|-------|-------|
| ketua@rcms.ac.id | Ketua Peneliti | Kontrol penuh proyek |
| anggota@rcms.ac.id | Anggota Peneliti | Mengerjakan & mencatat |
| asisten@rcms.ac.id | Asisten Mahasiswa | Tugas terbatas |
| admin@rcms.ac.id | Admin LPPM | Data master & hibah |

> Tip demo: buka 2 browser berbeda (atau jendela normal + incognito) agar bisa
> login sebagai Ketua dan Anggota bersamaan, memperlihatkan alur undangan.

---

## C. Tutorial per Fitur

### 1. Login & Dashboard
1. Buka <http://localhost:5173> → halaman login portal kampus.
2. Masuk dengan salah satu akun demo.
3. Dashboard tampil **berbeda per peran** (judul, menu, kapabilitas).
4. Perhatikan **sidebar kiri** (navigasi) & **lonceng 🔔** (notifikasi) di kanan atas.

### 2. Profil Kepakaran (semua peran) — fondasi Matchmaking
1. Sidebar → **Profil Kepakaran**.
2. Isi minimal field bertanda **"dipakai matchmaking"**: Bidang Riset, Interest,
   Keahlian Spesifik.
3. Klik **Simpan Profil**. Status berubah jadi **"● Vektor ter-encode"** —
   artinya sistem membuat vektor SBERT dari teks Anda.
4. *Untuk demo matchmaking:* isi profil beberapa akun (mis. anggota = bidang AI,
   asisten = bidang ekonomi).

### 3. Smart Matchmaking (Ketua) — fitur inti TA
1. Login sebagai **Ketua** → sidebar → **Smart Matchmaking**.
2. Ketik kebutuhan riset, contoh:
   *"Deteksi dini penyakit padi menggunakan computer vision dan deep learning"*.
3. Klik **Cari Kolaborator**.
4. Muncul **kartu kandidat berperingkat** dengan **skor kecocokan (%)**.
   - Kandidat bidang relevan (AI) skornya jauh lebih tinggi daripada yang tidak.
   - Skor transparan = dasar validasi objektif di laporan.
5. Tombol **Undang ke Tim** mengarahkan ke alur undangan (lihat #5).

### 4. Proyek (Ketua membuat)
1. Login **Ketua** → sidebar → **Proyek** → **+ Proyek Baru**.
2. Isi judul + deskripsi → **Simpan Proyek**.
3. Kartu proyek punya tombol: **Kanban, Keuangan, Rapat, PDF, Excel**.

### 5. Undangan Tim + Audit Trail
**Sebagai Ketua:**
1. (Saat ini undangan dibuat via API/Swagger atau dari konteks proyek.)
   Endpoint: `POST /api/proyek/{id}/undangan` dengan `user_id` kandidat.
**Sebagai kandidat (Anggota/Asisten):**
2. Login → sidebar → **Undangan Tim**.
3. Lihat undangan masuk → **Terima** atau **Tolak**.
4. Klik **Lihat audit trail** → riwayat lengkap perubahan status (siapa & kapan).

### 6. Kanban Board + Logbook
1. Sidebar → **Proyek** → tombol **Kanban** pada salah satu proyek.
2. Papan 3 kolom: **To-Do / In Progress / Done**.
3. **Ketua:** klik **+ Kartu** untuk membuat tugas (boleh set PJ via user id).
4. **Seret kartu** antar kolom untuk ubah status.
   - **RBAC:** Ketua bisa pindah semua kartu; Anggota/Asisten hanya kartu yang
     ditugaskan ke dirinya (selain itu ditolak).
5. Klik **Logbook** pada kartu → tambah catatan kegiatan + durasi + **unggah
   lampiran** (foto/dokumen bukti kerja).

### 7. Keuangan / RAB
1. Sidebar → **Proyek** → tombol **Keuangan**.
2. Kartu statistik: **Total Alokasi, Terpakai, Sisa**.
3. **Ketua:** **+ Kategori RAB** → isi kategori + alokasi (Rp).
4. Klik **Pengeluaran** pada kategori → catat pengeluaran + **unggah bukti
   transaksi** (nota/kuitansi).
   - Boleh dicatat oleh Ketua/Anggota; semua anggota tim bisa **melihat**.
5. **Sisa saldo** terhitung real-time. Bila sisa **< 20%**, muncul **peringatan
   merah "Anggaran menipis"**.

### 8. Rapat (Google Calendar — mode simulasi)
1. Sidebar → **Proyek** → tombol **Rapat**.
2. Set rentang tanggal + durasi → **Cari Waktu**.
3. Muncul **slot kosong bersama** seluruh anggota (FreeBusy).
4. **Ketua:** isi judul rapat → **Jadwalkan** pada slot pilihan.
   - Sistem membuat event + mengirim **notifikasi** ke semua anggota.
> Mode simulasi memakai data contoh; aktifkan Google asli lewat
> [PANDUAN_INTEGRASI_FASE5.md](PANDUAN_INTEGRASI_FASE5.md).

### 9. Notifikasi & Pengingat
1. Klik **lonceng 🔔** di kanan atas (halaman mana pun).
2. Lihat daftar notifikasi (rapat, deadline, anggaran).
3. Tombol **Jalankan pengingat** (demo on-demand) memicu pengecekan:
   - Tugas deadline **H-1** → notifikasi ke penanggung jawab.
   - Anggaran **< 20%** → notifikasi ke ketua.
> Otomatis juga jalan terjadwal tiap jam (APScheduler).

### 10. Bursa Informasi Hibah
1. Sidebar → **Bursa Hibah** (semua peran bisa melihat).
2. **Admin LPPM:** **+ Tambah Hibah** → judul, penyelenggara, persyaratan,
   deadline. Bisa **Hapus**.
3. Peran lain hanya membaca (papan pengumuman).

### 11. Ekspor Laporan (PDF & Excel)
1. Sidebar → **Proyek** → pada kartu proyek klik **PDF** atau **Excel**.
2. File terunduh otomatis, berisi **logbook + realisasi anggaran** proyek.
3. PDF memakai kerangka template LPPM (dapat disesuaikan di kode).
> Unggah ke portal kampus tetap manual (sesuai ruang lingkup).

---

## D. Skenario Demo Sidang (urutan disarankan)

1. **Login** Ketua → tunjukkan dashboard per peran.
2. **Profil Kepakaran** → isi & tunjukkan "vektor ter-encode".
3. **Smart Matchmaking** → cari kolaborator, soroti **skor kecocokan** (inti TA).
4. **Buat Proyek** → **undang** anggota → (akun anggota) **terima** → tunjukkan
   **audit trail**.
5. **Kanban** → buat tugas, seret antar kolom, tunjukkan **RBAC asisten ditolak**.
6. **Logbook** → tambah entri + lampiran.
7. **Keuangan** → buat RAB, catat pengeluaran, tunjukkan **peringatan <20%**.
8. **Rapat** → cari waktu + jadwalkan → muncul **notifikasi**.
9. **Bursa Hibah** (akun Admin) → tambah info hibah.
10. **Ekspor Laporan** → unduh PDF & Excel.

---

## E. Hal yang Perlu Diingat

- **Keamanan:** otorisasi ditegakkan di **backend** (bukan sekadar sembunyi
  tombol). Token kedaluwarsa otomatis logout.
- **Integrasi (Calendar/WhatsApp):** default **mode simulasi** — bisa di-demo
  tanpa biaya; arsitektur pakai pola adapter agar mudah dialihkan ke asli.
- **Data uang** memakai presisi desimal; pencatatan dalam transaksi DB.
- Jika tampilan aneh setelah update, **refresh** browser (Ctrl+F5).
