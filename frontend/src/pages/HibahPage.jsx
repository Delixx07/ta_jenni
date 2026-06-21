// Bursa Informasi Hibah — gaya kampus. Semua user lihat; Admin LPPM kelola.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { Card, EmptyState, ErrorBanner, Loading, PageHeader } from "../components/ui";

export default function HibahPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ judul: "", penyelenggara: "", persyaratan: "", deadline: "" });

  async function refresh() {
    try {
      setItems(await api.listHibah());
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
      await api.createHibah({
        judul: form.judul,
        penyelenggara: form.penyelenggara || null,
        persyaratan: form.persyaratan || null,
        deadline: form.deadline || null,
      });
      setForm({ judul: "", penyelenggara: "", persyaratan: "", deadline: "" });
      setShowForm(false);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm("Hapus info hibah ini?")) return;
    try {
      await api.deleteHibah(id);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <Layout title="Bursa Hibah">
      <PageHeader
        title="Bursa Informasi Hibah"
        subtitle="Papan pengumuman peluang pendanaan penelitian."
        action={
          isAdmin && (
            <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
              {showForm ? "Tutup" : "+ Tambah Hibah"}
            </button>
          )
        }
      />

      <ErrorBanner message={error} />

      {showForm && isAdmin && (
        <Card className="mb-6">
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="label">Judul Hibah</label>
              <input required value={form.judul} onChange={(e) => setForm({ ...form, judul: e.target.value })} className="input" />
            </div>
            <div>
              <label className="label">Penyelenggara</label>
              <input value={form.penyelenggara} onChange={(e) => setForm({ ...form, penyelenggara: e.target.value })} className="input" />
            </div>
            <div>
              <label className="label">Persyaratan</label>
              <textarea value={form.persyaratan} onChange={(e) => setForm({ ...form, persyaratan: e.target.value })} rows={2} className="input" />
            </div>
            <div>
              <label className="label">Deadline</label>
              <input type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} className="input max-w-xs" />
            </div>
            <button className="btn-primary">Simpan</button>
          </form>
        </Card>
      )}

      {loading && <Loading />}
      {!loading && items.length === 0 && (
        <EmptyState icon="📢" text="Belum ada informasi hibah." />
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((h) => (
          <Card key={h.id}>
            <div className="flex items-start justify-between">
              <p className="font-semibold text-navy-900">{h.judul}</p>
              {isAdmin && (
                <button onClick={() => handleDelete(h.id)} className="text-xs text-red-600 hover:underline">
                  Hapus
                </button>
              )}
            </div>
            {h.penyelenggara && <p className="text-sm text-slate-500 mt-0.5">{h.penyelenggara}</p>}
            {h.persyaratan && <p className="text-sm text-slate-600 mt-2">{h.persyaratan}</p>}
            {h.deadline && (
              <p className="text-xs font-medium text-red-600 mt-3">⏰ Deadline: {h.deadline}</p>
            )}
          </Card>
        ))}
      </div>
    </Layout>
  );
}
