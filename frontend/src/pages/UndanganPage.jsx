// Halaman Undangan Tim — gaya kampus. Terima/tolak + audit trail.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import Layout from "../components/Layout";
import { Badge, Card, EmptyState, ErrorBanner, Loading, PageHeader } from "../components/ui";

export default function UndanganPage() {
  const [undangan, setUndangan] = useState([]);
  const [riwayat, setRiwayat] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setUndangan(await api.undanganSaya());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function respond(id, terima) {
    setError("");
    try {
      await api.respondUndangan(id, terima);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function lihatRiwayat(id) {
    try {
      const data = await api.riwayatUndangan(id);
      setRiwayat((r) => ({ ...r, [id]: data }));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <Layout title="Undangan Tim">
      <PageHeader title="Undangan Tim" subtitle="Undangan bergabung ke proyek penelitian." />
      <ErrorBanner message={error} />

      {loading && <Loading />}
      {!loading && undangan.length === 0 && (
        <EmptyState icon="✉️" text="Belum ada undangan untuk Anda." />
      )}

      <div className="space-y-3">
        {undangan.map((u) => (
          <Card key={u.id}>
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-navy-900">Undangan ke proyek #{u.proyek_id}</p>
                  <Badge tone={u.status_undangan}>{u.status_undangan}</Badge>
                </div>
                <p className="text-sm text-slate-500 mt-0.5">
                  Peran ditawarkan: {u.peran_dalam_tim || "—"}
                </p>
              </div>
              {u.status_undangan === "terkirim" && (
                <div className="flex gap-2">
                  <button onClick={() => respond(u.id, true)} className="btn-primary">Terima</button>
                  <button onClick={() => respond(u.id, false)} className="btn-outline">Tolak</button>
                </div>
              )}
            </div>

            <button onClick={() => lihatRiwayat(u.id)} className="mt-3 text-xs text-navy-600 hover:underline">
              Lihat audit trail
            </button>
            {riwayat[u.id] && (
              <ul className="mt-2 text-xs text-slate-500 border-t border-slate-100 pt-2 space-y-1">
                {riwayat[u.id].map((r) => (
                  <li key={r.id}>
                    {new Date(r.created_at).toLocaleString("id-ID")} —{" "}
                    {r.status_lama ? `${r.status_lama} → ` : "dibuat: "}
                    <strong>{r.status_baru}</strong> (oleh user #{r.aktor_id})
                  </li>
                ))}
              </ul>
            )}
          </Card>
        ))}
      </div>
    </Layout>
  );
}
