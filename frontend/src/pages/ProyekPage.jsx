// Halaman daftar Proyek + buat proyek (Ketua) — gaya kampus.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { Badge, Card, EmptyState, ErrorBanner, Loading, PageHeader } from "../components/ui";

export default function ProyekPage() {
  const { user } = useAuth();
  const [proyek, setProyek] = useState([]);
  const [judul, setJudul] = useState("");
  const [deskripsi, setDeskripsi] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      setProyek(await api.listProyek());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createProyek({ judul, deskripsi });
      setJudul("");
      setDeskripsi("");
      setShowForm(false);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <Layout title="Proyek">
      <PageHeader
        title="Proyek Penelitian"
        subtitle="Kelola proyek, tim, tugas, anggaran, dan laporan."
        action={
          user?.role === "ketua" && (
            <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
              {showForm ? "Tutup" : "+ Proyek Baru"}
            </button>
          )
        }
      />

      <ErrorBanner message={error} />

      {showForm && user?.role === "ketua" && (
        <Card className="mb-6">
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="label">Judul Proyek</label>
              <input required value={judul} onChange={(e) => setJudul(e.target.value)} className="input" />
            </div>
            <div>
              <label className="label">Deskripsi</label>
              <textarea value={deskripsi} onChange={(e) => setDeskripsi(e.target.value)} rows={2} className="input" />
            </div>
            <button className="btn-primary">Simpan Proyek</button>
          </form>
        </Card>
      )}

      {loading && <Loading />}
      {!loading && proyek.length === 0 && (
        <EmptyState icon="📁" text="Belum ada proyek. Mulai dengan membuat proyek baru." />
      )}

      <div className="space-y-3">
        {proyek.map((p) => (
          <Card key={p.id}>
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-navy-900">{p.judul}</p>
                  <Badge tone={p.status}>{p.status}</Badge>
                </div>
                <p className="text-sm text-slate-500 mt-0.5">{p.deskripsi || "Tanpa deskripsi"}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Link to={`/proyek/${p.id}/kanban`} className="btn-outline">📋 Kanban</Link>
                <Link to={`/proyek/${p.id}/keuangan`} className="btn-outline">💰 Keuangan</Link>
                <Link to={`/proyek/${p.id}/rapat`} className="btn-outline">📅 Rapat</Link>
                <button onClick={() => api.unduhLaporan(p.id, "pdf").catch((e) => setError(e.message))} className="btn-ghost" title="Unduh PDF">PDF</button>
                <button onClick={() => api.unduhLaporan(p.id, "excel").catch((e) => setError(e.message))} className="btn-ghost" title="Unduh Excel">Excel</button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </Layout>
  );
}
