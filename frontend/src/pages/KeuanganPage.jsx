// Halaman Keuangan proyek — gaya kampus: ringkasan saldo + peringatan <20%.
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { Card, EmptyState, ErrorBanner, PageHeader, rupiah } from "../components/ui";
import PengeluaranModal from "../components/PengeluaranModal";

function barColor(persen, menipis) {
  if (menipis) return "bg-red-500";
  if (persen <= 50) return "bg-gold-400";
  return "bg-emerald-500";
}

export default function KeuanganPage() {
  const { proyekId } = useParams();
  const { user } = useAuth();
  const [ringkasan, setRingkasan] = useState(null);
  const [error, setError] = useState("");
  const [kategori, setKategori] = useState("");
  const [alokasi, setAlokasi] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [modalKategori, setModalKategori] = useState(null);

  const isKetua = user?.role === "ketua";

  async function refresh() {
    try {
      setRingkasan(await api.ringkasanKeuangan(proyekId));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [proyekId]);

  async function handleAddRab(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createRab(proyekId, { kategori, jumlah_dialokasikan: alokasi });
      setKategori("");
      setAlokasi("");
      setShowForm(false);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  const stat = [
    { label: "Total Alokasi", value: ringkasan?.total_dialokasikan, color: "text-navy-900" },
    { label: "Terpakai", value: ringkasan?.total_terpakai, color: "text-amber-600" },
    { label: "Sisa", value: ringkasan?.total_sisa, color: "text-emerald-600" },
  ];

  return (
    <Layout title="Keuangan">
      <PageHeader
        title={`Keuangan Proyek #${proyekId}`}
        subtitle="Rencana Anggaran Biaya & realisasi pengeluaran real-time."
        action={
          <Link to="/proyek" className="btn-ghost">← Daftar proyek</Link>
        }
      />
      <ErrorBanner message={error} />

      {ringkasan && (
        <>
          {/* Kartu statistik total */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            {stat.map((s) => (
              <Card key={s.label}>
                <p className="text-xs text-slate-400 uppercase tracking-wide">{s.label}</p>
                <p className={`text-xl font-bold mt-1 ${s.color}`}>{rupiah(s.value || 0)}</p>
              </Card>
            ))}
          </div>

          {isKetua && (
            <div className="mb-6">
              <button onClick={() => setShowForm((v) => !v)} className="btn-primary mb-3">
                {showForm ? "Tutup" : "+ Kategori RAB"}
              </button>
              {showForm && (
                <Card>
                  <form onSubmit={handleAddRab} className="flex flex-wrap gap-3 items-end">
                    <div className="flex-1 min-w-[180px]">
                      <label className="label">Kategori</label>
                      <input required value={kategori} onChange={(e) => setKategori(e.target.value)}
                        placeholder="mis. Bahan habis pakai" className="input" />
                    </div>
                    <div>
                      <label className="label">Alokasi (Rp)</label>
                      <input type="number" min="0" required value={alokasi}
                        onChange={(e) => setAlokasi(e.target.value)} className="input w-44" />
                    </div>
                    <button className="btn-primary">Simpan</button>
                  </form>
                </Card>
              )}
            </div>
          )}

          {ringkasan.kategori.length === 0 ? (
            <EmptyState icon="💰" text="Belum ada kategori RAB." />
          ) : (
            <div className="space-y-3">
              {ringkasan.kategori.map((k) => (
                <Card key={k.rab_id}>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-semibold text-navy-900">{k.kategori}</p>
                      <p className="text-xs text-slate-500">
                        Terpakai {rupiah(k.terpakai)} / {rupiah(k.dialokasikan)} · Sisa {rupiah(k.sisa)}
                      </p>
                    </div>
                    <button onClick={() => setModalKategori(k)} className="btn-outline">
                      Pengeluaran
                    </button>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${barColor(k.persen_sisa, k.peringatan_menipis)}`}
                      style={{ width: `${Math.max(0, Math.min(100, k.persen_sisa))}%` }} />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Sisa {k.persen_sisa}%</p>
                  {k.peringatan_menipis && (
                    <div className="mt-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-1.5">
                      ⚠ Anggaran menipis (sisa di bawah 20%)
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </>
      )}

      {modalKategori && (
        <PengeluaranModal kategori={modalKategori} onClose={() => setModalKategori(null)} onSaved={refresh} />
      )}
    </Layout>
  );
}
