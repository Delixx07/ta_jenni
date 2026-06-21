// Kanban Board — gaya kampus. 3 kolom drag-and-drop + logbook per kartu.
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { Card, ErrorBanner, PageHeader } from "../components/ui";
import LogbookModal from "../components/LogbookModal";

const KOLOM = [
  { key: "todo", label: "To-Do", dot: "bg-slate-400" },
  { key: "in_progress", label: "In Progress", dot: "bg-gold-400" },
  { key: "done", label: "Done", dot: "bg-emerald-500" },
];

export default function KanbanPage() {
  const { proyekId } = useParams();
  const { user } = useAuth();
  const [tugas, setTugas] = useState([]);
  const [error, setError] = useState("");
  const [judul, setJudul] = useState("");
  const [pjId, setPjId] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [logbookTugas, setLogbookTugas] = useState(null);

  async function refresh() {
    try {
      setTugas(await api.listTugas(proyekId));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [proyekId]);

  const isKetua = user?.role === "ketua";

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createTugas(proyekId, { judul, penanggung_jawab_id: pjId ? Number(pjId) : null });
      setJudul("");
      setPjId("");
      setShowForm(false);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  function onDragStart(e, id) {
    e.dataTransfer.setData("text/plain", String(id));
  }
  async function onDrop(e, status) {
    e.preventDefault();
    const id = Number(e.dataTransfer.getData("text/plain"));
    const t = tugas.find((x) => x.id === id);
    if (!t || t.status === status) return;
    setTugas((prev) => prev.map((x) => (x.id === id ? { ...x, status } : x)));
    try {
      await api.ubahStatusTugas(id, status);
    } catch (e) {
      setError(e.message);
      refresh();
    }
  }

  return (
    <Layout title="Kanban">
      <PageHeader
        title={`Kanban — Proyek #${proyekId}`}
        subtitle="Seret kartu antar kolom untuk memperbarui status."
        action={
          <div className="flex gap-2">
            <Link to="/proyek" className="btn-ghost">← Proyek</Link>
            {isKetua && (
              <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
                {showForm ? "Tutup" : "+ Kartu"}
              </button>
            )}
          </div>
        }
      />

      <ErrorBanner message={error} />

      {showForm && isKetua && (
        <Card className="mb-6">
          <form onSubmit={handleCreate} className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="label">Judul tugas</label>
              <input required value={judul} onChange={(e) => setJudul(e.target.value)} className="input" />
            </div>
            <div>
              <label className="label">PJ (user id)</label>
              <input value={pjId} onChange={(e) => setPjId(e.target.value)} placeholder="mis. 6" className="input w-28" />
            </div>
            <button className="btn-primary">Tambah</button>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {KOLOM.map((kol) => (
          <div
            key={kol.key}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => onDrop(e, kol.key)}
            className="bg-slate-100 rounded-xl p-3 min-h-[320px]"
          >
            <div className="flex items-center gap-2 mb-3 px-1">
              <span className={`h-2.5 w-2.5 rounded-full ${kol.dot}`} />
              <h2 className="font-semibold text-navy-900 text-sm">{kol.label}</h2>
              <span className="text-xs text-slate-400">
                {tugas.filter((t) => t.status === kol.key).length}
              </span>
            </div>
            <div className="space-y-2">
              {tugas.filter((t) => t.status === kol.key).map((t) => (
                <div
                  key={t.id}
                  draggable
                  onDragStart={(e) => onDragStart(e, t.id)}
                  className="bg-white rounded-lg shadow-card border border-slate-100 p-3 cursor-grab active:cursor-grabbing hover:shadow-elevated transition"
                >
                  <p className="font-medium text-navy-900 text-sm">{t.judul}</p>
                  {t.deskripsi && <p className="text-xs text-slate-500 mt-1">{t.deskripsi}</p>}
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-slate-400">
                      {t.penanggung_jawab_id ? `PJ #${t.penanggung_jawab_id}` : "Belum di-assign"}
                    </span>
                    <button onClick={() => setLogbookTugas(t)} className="text-xs text-navy-600 hover:underline">
                      Logbook
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {logbookTugas && <LogbookModal tugas={logbookTugas} onClose={() => setLogbookTugas(null)} />}
    </Layout>
  );
}
