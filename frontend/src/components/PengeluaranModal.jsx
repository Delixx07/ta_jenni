// Modal pencatatan pengeluaran untuk satu kategori RAB + daftar pengeluaran.
import { useEffect, useState } from "react";
import { api } from "../api/client";

const rupiah = (n) =>
  "Rp " + Number(n).toLocaleString("id-ID", { maximumFractionDigits: 0 });

export default function PengeluaranModal({ kategori, onClose, onSaved }) {
  const [items, setItems] = useState([]);
  const [jumlah, setJumlah] = useState("");
  const [deskripsi, setDeskripsi] = useState("");
  const [bukti, setBukti] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function refresh() {
    try {
      setItems(await api.listPengeluaran(kategori.rab_id));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kategori.rab_id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("jumlah", jumlah);
      if (deskripsi) fd.append("deskripsi", deskripsi);
      if (bukti) fd.append("bukti", bukti);
      await api.catatPengeluaran(kategori.rab_id, fd);
      setJumlah("");
      setDeskripsi("");
      setBukti(null);
      await refresh();
      onSaved?.(); // perbarui ringkasan di halaman induk
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-lg max-h-[85vh] overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-bold text-slate-800">Pengeluaran — {kategori.kategori}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl">×</button>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          Sisa: {rupiah(kategori.sisa)} dari {rupiah(kategori.dialokasikan)}
        </p>

        <form onSubmit={handleSubmit} className="space-y-3 border-b pb-4 mb-4">
          <input
            type="number" min="1" required
            value={jumlah}
            onChange={(e) => setJumlah(e.target.value)}
            placeholder="Jumlah (Rp)"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            value={deskripsi}
            onChange={(e) => setDeskripsi(e.target.value)}
            placeholder="Deskripsi (mis. beli reagen)"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
          <div>
            <label className="block text-xs text-slate-500 mb-1">Bukti transaksi (nota/kuitansi)</label>
            <input type="file" onChange={(e) => setBukti(e.target.files?.[0] || null)} className="text-sm" />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            disabled={saving}
            className="rounded-lg bg-slate-800 text-white px-4 py-2 text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {saving ? "Menyimpan…" : "Catat Pengeluaran"}
          </button>
        </form>

        <div className="space-y-2">
          {items.length === 0 && <p className="text-sm text-slate-400">Belum ada pengeluaran.</p>}
          {items.map((p) => (
            <div key={p.id} className="text-sm border rounded-lg p-3 flex justify-between">
              <div>
                <p className="text-slate-700 font-medium">{rupiah(p.jumlah)}</p>
                <p className="text-xs text-slate-500">{p.deskripsi || "—"}</p>
                <p className="text-xs text-slate-400">
                  {new Date(p.tanggal).toLocaleDateString("id-ID")} · oleh user #{p.user_id}
                </p>
              </div>
              {p.bukti_transaksi_url && (
                <a href={p.bukti_transaksi_url} target="_blank" rel="noreferrer"
                   className="text-xs text-slate-600 hover:underline self-start">
                  Bukti
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
