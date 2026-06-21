// Modal logbook untuk sebuah tugas: lihat entri + tambah entri (dengan lampiran).
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function LogbookModal({ tugas, onClose }) {
  const [entries, setEntries] = useState([]);
  const [deskripsi, setDeskripsi] = useState("");
  const [durasi, setDurasi] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function refresh() {
    try {
      setEntries(await api.listLogbook(tugas.id));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tugas.id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      // Multipart agar bisa menyertakan file lampiran bukti kerja.
      const fd = new FormData();
      fd.append("deskripsi_kegiatan", deskripsi);
      if (durasi) fd.append("durasi", durasi);
      if (file) fd.append("lampiran", file);
      await api.tambahLogbook(tugas.id, fd);
      setDeskripsi("");
      setDurasi("");
      setFile(null);
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-lg max-h-[85vh] overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-bold text-slate-800">Logbook — {tugas.judul}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 border-b pb-4 mb-4">
          <textarea
            required
            value={deskripsi}
            onChange={(e) => setDeskripsi(e.target.value)}
            placeholder="Deskripsi kegiatan"
            rows={2}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <div className="flex gap-3">
            <input
              type="number"
              min="0"
              value={durasi}
              onChange={(e) => setDurasi(e.target.value)}
              placeholder="Durasi (menit)"
              className="w-36 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="flex-1 text-sm"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            disabled={saving}
            className="rounded-lg bg-slate-800 text-white px-4 py-2 text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {saving ? "Menyimpan…" : "Tambah Entri"}
          </button>
        </form>

        <div className="space-y-2">
          {entries.length === 0 && (
            <p className="text-sm text-slate-400">Belum ada entri logbook.</p>
          )}
          {entries.map((en) => (
            <div key={en.id} className="text-sm border rounded-lg p-3">
              <p className="text-slate-700">{en.deskripsi_kegiatan}</p>
              <div className="text-xs text-slate-400 mt-1 flex gap-3">
                <span>{new Date(en.tanggal).toLocaleString("id-ID")}</span>
                {en.durasi != null && <span>{en.durasi} menit</span>}
                {en.lampiran_url && (
                  <a
                    href={en.lampiran_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-600 hover:underline"
                  >
                    Lihat lampiran
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
