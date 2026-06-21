// Halaman login bergaya portal kampus: panel branding + form.
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ErrorBanner } from "../components/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Panel branding (kiri) */}
      <div className="hidden lg:flex flex-col justify-between bg-navy-900 text-white p-12 relative overflow-hidden">
        <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-navy-700/40" />
        <div className="absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-navy-800/50" />
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-xl bg-gold-400 text-navy-900 grid place-items-center font-bold text-xl">
              R
            </div>
            <div>
              <p className="font-bold text-lg leading-tight">RCMS</p>
              <p className="text-xs text-navy-300">Lembaga Penelitian & Pengabdian Masyarakat</p>
            </div>
          </div>
        </div>
        <div className="relative">
          <h1 className="text-4xl font-bold leading-tight">
            Research Collaboration<br />& Management System
          </h1>
          <p className="text-navy-200 mt-4 max-w-md">
            Temukan kolaborator riset lintas program studi, kelola tim & anggaran,
            dan hasilkan laporan penelitian dalam satu workspace.
          </p>
          <div className="flex gap-6 mt-8 text-sm text-navy-200">
            <span>🔍 Smart Matchmaking</span>
            <span>📋 Manajemen Tim</span>
            <span>💰 Anggaran</span>
          </div>
        </div>
        <div className="relative text-xs text-navy-400">
          © {new Date().getFullYear()} Universitas · RCMS
        </div>
      </div>

      {/* Form (kanan) */}
      <div className="flex items-center justify-center p-6 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-6">
            <div className="h-10 w-10 rounded-lg bg-navy-900 text-gold-400 grid place-items-center font-bold">
              R
            </div>
            <span className="font-bold text-navy-900 text-lg">RCMS</span>
          </div>

          <h2 className="text-2xl font-bold text-navy-900">Masuk ke Akun Anda</h2>
          <p className="text-slate-500 mb-6">Silakan masuk untuk melanjutkan.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="nama@rcms.ac.id"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
              />
            </div>

            <ErrorBanner message={error} />

            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting ? "Memproses…" : "Masuk"}
            </button>
          </form>

          <div className="mt-6 text-xs text-slate-400 border-t border-slate-200 pt-4">
            <p className="font-medium text-slate-500 mb-1">Akun demo (password: password123):</p>
            <div className="grid grid-cols-2 gap-1">
              <span>ketua@rcms.ac.id</span>
              <span>anggota@rcms.ac.id</span>
              <span>asisten@rcms.ac.id</span>
              <span>admin@rcms.ac.id</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
