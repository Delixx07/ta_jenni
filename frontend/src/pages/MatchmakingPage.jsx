// Halaman Smart Matchmaking (khusus Ketua Peneliti) — gaya kampus.
import { useState } from "react";
import { api } from "../api/client";
import Layout from "../components/Layout";
import { Card, EmptyState, ErrorBanner, PageHeader } from "../components/ui";

function scoreColor(skor) {
  if (skor >= 70) return "bg-emerald-500";
  if (skor >= 40) return "bg-gold-400";
  return "bg-slate-300";
}

export default function MatchmakingPage() {
  const [kebutuhan, setKebutuhan] = useState("");
  const [hasil, setHasil] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setHasil(null);
    try {
      setHasil(await api.cariKolaborator(kebutuhan));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleInvite(k) {
    alert(
      `Untuk mengundang ${k.nama}, buka menu Proyek → pilih proyek → Undangan.\n(Skor kecocokan: ${k.skor_kemiripan}%)`
    );
  }

  return (
    <Layout title="Smart Matchmaking">
      <PageHeader
        title="Smart Matchmaking"
        subtitle="Temukan kolaborator paling relevan secara semantik (SBERT + cosine similarity)."
      />

      <Card className="mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="label">Kebutuhan Riset (abstrak / ide)</label>
            <textarea
              rows={4}
              required
              value={kebutuhan}
              onChange={(e) => setKebutuhan(e.target.value)}
              placeholder="Contoh: Penelitian deteksi dini penyakit padi menggunakan computer vision dan deep learning…"
              className="input"
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Mencari kandidat…" : "🔍 Cari Kolaborator"}
          </button>
        </form>
      </Card>

      <ErrorBanner message={error} />

      {hasil && (
        <>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-navy-900">
              {hasil.jumlah_kandidat} kandidat ditemukan
            </h2>
            <span className="text-xs text-slate-400">diurutkan dari skor tertinggi</span>
          </div>

          {hasil.jumlah_kandidat === 0 ? (
            <EmptyState
              icon="🧑‍🔬"
              text="Belum ada kandidat cocok. Pastikan ada dosen lain yang sudah mengisi profil kepakaran & berstatus tersedia."
            />
          ) : (
            <div className="space-y-3">
              {hasil.kandidat.map((k, idx) => (
                <Card key={k.user_id} className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-navy-100 text-navy-700 grid place-items-center font-bold">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-navy-900">{k.nama}</p>
                    <p className="text-sm text-slate-500">
                      {k.program_studi || "Program studi tidak diisi"}
                    </p>
                    <div className="mt-2 flex items-center gap-3">
                      <div className="w-48 h-2.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${scoreColor(k.skor_kemiripan)} transition-all`}
                          style={{ width: `${k.skor_kemiripan}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold text-navy-900">
                        {k.skor_kemiripan}%
                      </span>
                      <span className="text-xs text-slate-400">kecocokan</span>
                    </div>
                  </div>
                  <button onClick={() => handleInvite(k)} className="btn-gold">
                    Undang ke Tim
                  </button>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </Layout>
  );
}
