// Halaman Manajemen Profil Kepakaran — gaya kampus.
// Menyimpan memicu re-encoding vektor SBERT di backend.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import Layout from "../components/Layout";
import { Card, ErrorBanner, Loading, PageHeader, SuccessBanner } from "../components/ui";

const FIELDS = [
  { name: "bidang_riset", label: "Bidang Riset", rows: 2, matching: true },
  { name: "interest", label: "Interest / Minat Penelitian", rows: 2, matching: true },
  { name: "keahlian_spesifik", label: "Keahlian Spesifik", rows: 2, matching: true },
  { name: "riwayat_penelitian", label: "Riwayat Penelitian", rows: 3, matching: false },
  { name: "publikasi", label: "Publikasi", rows: 3, matching: false },
];

const EMPTY = { bidang_riset: "", interest: "", riwayat_penelitian: "", publikasi: "", keahlian_spesifik: "" };

export default function ProfilPage() {
  const [form, setForm] = useState(EMPTY);
  const [hasEmbedding, setHasEmbedding] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.getProfil()
      .then((p) => {
        if (p) {
          setForm({
            bidang_riset: p.bidang_riset || "",
            interest: p.interest || "",
            riwayat_penelitian: p.riwayat_penelitian || "",
            publikasi: p.publikasi || "",
            keahlian_spesifik: p.keahlian_spesifik || "",
          });
          setHasEmbedding(p.has_embedding);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const saved = await api.saveProfil(form);
      setHasEmbedding(saved.has_embedding);
      setMessage(
        saved.has_embedding
          ? "Profil disimpan & vektor kepakaran berhasil di-encode."
          : "Profil disimpan, namun vektor kosong (isi minimal satu field penanda)."
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading)
    return (
      <Layout title="Profil Kepakaran">
        <Loading text="Memuat profil…" />
      </Layout>
    );

  return (
    <Layout title="Profil Kepakaran">
      <PageHeader
        title="Profil Kepakaran"
        subtitle="Lengkapi profil agar dapat ditemukan oleh Smart Matchmaking."
        action={
          <span className={`badge ${hasEmbedding ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
            {hasEmbedding ? "● Vektor ter-encode" : "○ Vektor belum ada"}
          </span>
        }
      />

      <SuccessBanner message={message} />
      <ErrorBanner message={error} />

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          {FIELDS.map((f) => (
            <div key={f.name}>
              <label className="label">
                {f.label}
                {f.matching && (
                  <span className="ml-2 badge bg-navy-50 text-navy-600">dipakai matchmaking</span>
                )}
              </label>
              <textarea
                rows={f.rows}
                value={form[f.name]}
                onChange={(e) => setForm((s) => ({ ...s, [f.name]: e.target.value }))}
                className="input"
              />
            </div>
          ))}
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? "Menyimpan & meng-encode…" : "Simpan Profil"}
          </button>
        </form>
      </Card>
    </Layout>
  );
}
