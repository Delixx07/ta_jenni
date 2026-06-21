// Dashboard bergaya kampus: sambutan + kartu menu cepat + kapabilitas peran.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import Layout from "../components/Layout";
import { ErrorBanner, Loading } from "../components/ui";

// Kartu menu cepat. `roles` membatasi tampil per peran (null = semua).
const MENU = [
  { to: "/profil", label: "Profil Kepakaran", desc: "Kelola bidang & keahlian Anda", icon: "👤", roles: null },
  { to: "/matchmaking", label: "Smart Matchmaking", desc: "Cari kolaborator riset", icon: "🔍", roles: ["ketua"] },
  { to: "/proyek", label: "Proyek", desc: "Kanban, keuangan, rapat, laporan", icon: "📁", roles: null },
  { to: "/undangan", label: "Undangan Tim", desc: "Terima/tolak undangan proyek", icon: "✉️", roles: null },
  { to: "/hibah", label: "Bursa Hibah", desc: "Informasi pendanaan penelitian", icon: "📢", roles: null },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError(e.message));
  }, []);

  const menu = MENU.filter((m) => !m.roles || m.roles.includes(user?.role));

  return (
    <Layout title="Dashboard">
      <ErrorBanner message={error} />
      {!data && !error && <Loading text="Memuat dashboard…" />}

      {data && (
        <>
          {/* Hero sambutan */}
          <div className="rounded-2xl bg-gradient-to-r from-navy-800 to-navy-700 text-white p-8 mb-8 shadow-elevated">
            <p className="text-navy-200 text-sm">Selamat datang,</p>
            <h1 className="text-3xl font-bold mt-1">{data.nama}</h1>
            <p className="text-navy-200 mt-2">{data.judul}</p>
          </div>

          {/* Menu cepat */}
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Menu Utama
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-10">
            {menu.map((m) => (
              <Link
                key={m.to}
                to={m.to}
                className="card p-5 hover:shadow-elevated hover:-translate-y-0.5 transition group"
              >
                <div className="h-11 w-11 rounded-xl bg-navy-50 text-2xl grid place-items-center mb-3 group-hover:bg-gold-100 transition">
                  {m.icon}
                </div>
                <p className="font-semibold text-navy-900">{m.label}</p>
                <p className="text-sm text-slate-500 mt-0.5">{m.desc}</p>
              </Link>
            ))}
          </div>

          {/* Kapabilitas peran */}
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Kapabilitas Peran Anda
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.kapabilitas.map((cap, i) => (
              <div key={i} className="card p-4 flex items-start gap-3">
                <span className="mt-0.5 h-6 w-6 shrink-0 rounded-full bg-emerald-100 text-emerald-700 grid place-items-center text-xs">
                  ✓
                </span>
                <p className="text-sm text-slate-700">{cap}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </Layout>
  );
}
