// Klien REST minimal untuk berkomunikasi dengan backend RCMS.
// Menyisipkan JWT secara otomatis dari localStorage bila tersedia.

const TOKEN_KEY = "rcms_token";

// Base URL backend. Saat dev dibiarkan kosong → pakai path relatif "/api/..."
// yang di-proxy Vite. Di produksi (Vercel) diisi via VITE_API_BASE_URL ke URL
// backend (mis. https://rcms-backend.up.railway.app).
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const url = (path) => `${API_BASE}${path}`;

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body, form, multipart } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let payload;
  if (multipart) {
    // FormData: biarkan browser menyetel Content-Type + boundary sendiri.
    payload = multipart;
  } else if (form) {
    // OAuth2PasswordRequestForm mengharapkan x-www-form-urlencoded.
    payload = new URLSearchParams(form).toString();
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else if (body) {
    payload = JSON.stringify(body);
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url(path), { method, headers, body: payload });
  if (!res.ok) {
    // Token kedaluwarsa/invalid: bersihkan sesi & beri tahu app untuk logout.
    // Kecualikan endpoint login agar pesan "email/password salah" tetap tampil.
    if (res.status === 401 && !path.endsWith("/auth/login")) {
      setToken(null);
      window.dispatchEvent(new Event("rcms:unauthorized"));
    }
    let detail = `Error ${res.status}`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* abaikan body non-JSON */
    }
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  // Login memakai form-urlencoded (username = email).
  login: (email, password) =>
    request("/api/auth/login", { method: "POST", form: { username: email, password } }),
  me: () => request("/api/auth/me"),
  dashboard: () => request("/api/dashboard/me"),

  // Profil kepakaran
  getProfil: () => request("/api/profil/me"),
  saveProfil: (data) => request("/api/profil/me", { method: "PUT", body: data }),

  // Smart Matchmaking
  cariKolaborator: (kebutuhan_riset) =>
    request("/api/matchmaking/cari", { method: "POST", body: { kebutuhan_riset } }),

  // Proyek
  listProyek: () => request("/api/proyek"),
  createProyek: (data) => request("/api/proyek", { method: "POST", body: data }),

  // Undangan tim
  undangKandidat: (proyekId, data) =>
    request(`/api/proyek/${proyekId}/undangan`, { method: "POST", body: data }),
  undanganSaya: () => request("/api/undangan/saya"),
  respondUndangan: (anggotaId, terima) =>
    request(`/api/undangan/${anggotaId}/respond`, { method: "POST", body: { terima } }),
  riwayatUndangan: (anggotaId) => request(`/api/undangan/${anggotaId}/riwayat`),

  // Tugas / Kanban
  listTugas: (proyekId) => request(`/api/proyek/${proyekId}/tugas`),
  createTugas: (proyekId, data) =>
    request(`/api/proyek/${proyekId}/tugas`, { method: "POST", body: data }),
  ubahStatusTugas: (tugasId, status) =>
    request(`/api/tugas/${tugasId}/status`, { method: "PATCH", body: { status } }),

  // Logbook (pakai multipart untuk mendukung lampiran)
  listLogbook: (tugasId) => request(`/api/tugas/${tugasId}/logbook`),
  tambahLogbook: (tugasId, formData) =>
    request(`/api/tugas/${tugasId}/logbook`, { method: "POST", multipart: formData }),

  // Keuangan (RAB & Pengeluaran)
  listRab: (proyekId) => request(`/api/proyek/${proyekId}/rab`),
  createRab: (proyekId, data) =>
    request(`/api/proyek/${proyekId}/rab`, { method: "POST", body: data }),
  ringkasanKeuangan: (proyekId) => request(`/api/proyek/${proyekId}/keuangan`),
  listPengeluaran: (rabId) => request(`/api/rab/${rabId}/pengeluaran`),
  catatPengeluaran: (rabId, formData) =>
    request(`/api/rab/${rabId}/pengeluaran`, { method: "POST", multipart: formData }),

  // Notifikasi (Fase 5)
  listNotifikasi: () => request("/api/notifikasi"),
  jalankanPengingat: () =>
    request("/api/calendar/jalankan-pengingat", { method: "POST" }),

  // Google Calendar (Fase 5)
  calendarStatus: () => request("/api/calendar/status"),
  cariWaktu: (data) => request("/api/calendar/cari-waktu", { method: "POST", body: data }),
  jadwalkanRapat: (data) =>
    request("/api/calendar/jadwalkan", { method: "POST", body: data }),

  // Bursa Hibah (Fase 6)
  listHibah: () => request("/api/hibah"),
  createHibah: (data) => request("/api/hibah", { method: "POST", body: data }),
  deleteHibah: (id) => request(`/api/hibah/${id}`, { method: "DELETE" }),

  // Ekspor laporan (Fase 6) — unduh file
  unduhLaporan: (proyekId, format) =>
    downloadFile(`/api/proyek/${proyekId}/laporan/${format}`),
};

// Unduh file biner (PDF/Excel) dengan menyertakan token, lalu trigger save.
async function downloadFile(path) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(url(path), { headers });
  if (!res.ok) throw new Error(`Gagal mengunduh (${res.status})`);

  const blob = await res.blob();
  // Ambil nama file dari header Content-Disposition bila ada.
  const cd = res.headers.get("Content-Disposition") || "";
  const match = cd.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : "laporan";

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
