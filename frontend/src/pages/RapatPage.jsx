// Halaman penjadwalan rapat: cari waktu kosong (FreeBusy) + jadwalkan rapat.
// Bekerja di mode simulasi (tanpa kredensial Google) maupun mode asli.
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { PageHeader } from "../components/ui";

// Default rentang pencarian: hari ini s/d 7 hari ke depan.
function defaultRange() {
  const now = new Date();
  const end = new Date(now.getTime() + 7 * 86400000);
  const fmt = (d) => d.toISOString().slice(0, 16); // untuk input datetime-local
  return { mulai: fmt(now), selesai: fmt(end) };
}

export default function RapatPage() {
  const { proyekId } = useParams();
  const { user } = useAuth();
  const [range, setRange] = useState(defaultRange());
  const [durasi, setDurasi] = useState(60);
  const [hasil, setHasil] = useState(null);
  const [mode, setMode] = useState("");
  const [judul, setJudul] = useState("Rapat Koordinasi Tim");
  const [pesan, setPesan] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.calendarStatus().then((s) => setMode(s.mode)).catch(() => {});
  }, []);

  async function cari(e) {
    e.preventDefault();
    setError("");
    setHasil(null);
    try {
      const res = await api.cariWaktu({
        proyek_id: Number(proyekId),
        mulai: new Date(range.mulai).toISOString(),
        selesai: new Date(range.selesai).toISOString(),
        durasi_menit: Number(durasi),
      });
      setHasil(res);
      setMode(res.mode);
    } catch (e) {
      setError(e.message);
    }
  }

  async function jadwalkan(slot) {
    setError("");
    setPesan("");
    try {
      const ev = await api.jadwalkanRapat({
        proyek_id: Number(proyekId),
        judul,
        mulai: slot.mulai,
        selesai: slot.selesai,
      });
      setPesan(
        `Rapat "${ev.judul}" dijadwalkan (${ev.mode}). Notifikasi terkirim ke anggota.`
      );
    } catch (e) {
      setError(e.message);
    }
  }

  const isKetua = user?.role === "ketua";

  return (
    <Layout title="Jadwalkan Rapat">
      <div className="max-w-3xl">
        <PageHeader
          title={`Jadwalkan Rapat — Proyek #${proyekId}`}
          subtitle={`Mode kalender: ${mode || "…"}${mode === "simulasi" ? " (data contoh; isi kredensial Google untuk mode asli)" : ""}`}
          action={<Link to="/proyek" className="btn-ghost">← Proyek</Link>}
        />

        <form onSubmit={cari} className="bg-white rounded-xl shadow-sm p-5 space-y-3 mb-6">
          <h2 className="font-semibold text-slate-700">Cari waktu kosong bersama</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Dari</label>
              <input type="datetime-local" value={range.mulai}
                onChange={(e) => setRange((r) => ({ ...r, mulai: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Sampai</label>
              <input type="datetime-local" value={range.selesai}
                onChange={(e) => setRange((r) => ({ ...r, selesai: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Durasi (menit)</label>
            <input type="number" min="15" step="15" value={durasi}
              onChange={(e) => setDurasi(e.target.value)}
              className="w-32 rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          </div>
          <button className="rounded-lg bg-slate-800 text-white px-4 py-2 text-sm font-medium hover:bg-slate-700">
            Cari Waktu
          </button>
        </form>

        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        {pesan && <p className="text-sm text-emerald-700 mb-3">{pesan}</p>}

        {hasil && (
          <div className="bg-white rounded-xl shadow-sm p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-slate-700">
                {hasil.jumlah_slot} slot kosong ditemukan
              </h2>
            </div>
            {isKetua && (
              <input
                value={judul}
                onChange={(e) => setJudul(e.target.value)}
                placeholder="Judul rapat"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm mb-3"
              />
            )}
            <div className="space-y-2">
              {hasil.slot.length === 0 && (
                <p className="text-sm text-slate-400">Tidak ada slot kosong pada rentang ini.</p>
              )}
              {hasil.slot.map((s, i) => (
                <div key={i} className="flex items-center justify-between border rounded-lg p-3 text-sm">
                  <span>
                    {new Date(s.mulai).toLocaleString("id-ID")} —{" "}
                    {new Date(s.selesai).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })}
                  </span>
                  {isKetua && (
                    <button
                      onClick={() => jadwalkan(s)}
                      className="rounded-lg bg-emerald-600 text-white px-3 py-1.5 text-xs hover:bg-emerald-500"
                    >
                      Jadwalkan
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
