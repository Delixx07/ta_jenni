// Lonceng notifikasi in-app: tampilkan daftar notifikasi user + tombol
// "jalankan pengingat" (demo on-demand) untuk memicu deadline/anggaran.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function NotifikasiBell() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      setItems(await api.listNotifikasi());
    } catch {
      /* abaikan di lonceng */
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function pengingat() {
    setBusy(true);
    try {
      await api.jalankanPengingat();
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => {
          setOpen((o) => !o);
          refresh();
        }}
        className="relative bg-white/20 hover:bg-white/30 rounded-lg px-3 py-1 text-sm"
        title="Notifikasi"
      >
        🔔
        {items.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">
            {items.length > 9 ? "9+" : items.length}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg z-50 text-slate-700">
          <div className="flex items-center justify-between p-3 border-b">
            <span className="font-semibold text-sm">Notifikasi</span>
            <button
              onClick={pengingat}
              disabled={busy}
              className="text-xs bg-slate-800 text-white rounded px-2 py-1 hover:bg-slate-700 disabled:opacity-50"
              title="Jalankan pengingat (demo)"
            >
              {busy ? "…" : "Jalankan pengingat"}
            </button>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {items.length === 0 && (
              <p className="p-4 text-sm text-slate-400">Belum ada notifikasi.</p>
            )}
            {items.map((n) => (
              <div key={n.id} className="p-3 border-b last:border-0">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] uppercase rounded bg-slate-100 px-1.5 py-0.5 text-slate-500">
                    {n.jenis}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {new Date(n.tanggal).toLocaleString("id-ID")}
                  </span>
                </div>
                <p className="text-sm mt-1">{n.pesan}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
