// Layout aplikasi bergaya portal kampus: sidebar navigasi + topbar.
// Dipakai semua halaman utama agar konsisten & profesional.
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import NotifikasiBell from "./NotifikasiBell";

// Item navigasi sidebar. `roles` membatasi tampil per peran (null = semua).
const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: "🏠", roles: null },
  { to: "/profil", label: "Profil Kepakaran", icon: "👤", roles: null },
  { to: "/matchmaking", label: "Smart Matchmaking", icon: "🔍", roles: ["ketua"] },
  { to: "/proyek", label: "Proyek", icon: "📁", roles: null },
  { to: "/undangan", label: "Undangan Tim", icon: "✉️", roles: null },
  { to: "/hibah", label: "Bursa Hibah", icon: "📢", roles: null },
];

const ROLE_LABEL = {
  ketua: "Ketua Peneliti",
  anggota: "Anggota Peneliti",
  asisten: "Asisten Mahasiswa",
  admin: "Admin LPPM",
};

export default function Layout({ children, title }) {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  const nav = NAV.filter((n) => !n.roles || n.roles.includes(user?.role));

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* ── Sidebar ── */}
      <aside className="hidden md:flex w-64 flex-col bg-navy-900 text-navy-100 fixed inset-y-0">
        <div className="px-6 py-5 border-b border-navy-800">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-gold-400 text-navy-900 grid place-items-center font-bold">
              R
            </div>
            <div>
              <p className="font-bold text-white leading-tight">RCMS</p>
              <p className="text-[10px] text-navy-300 leading-tight">
                Research Collaboration
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {nav.map((n) => {
            const active = pathname === n.to || pathname.startsWith(n.to + "/");
            return (
              <Link
                key={n.to}
                to={n.to}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active
                    ? "bg-navy-700 text-white"
                    : "text-navy-200 hover:bg-navy-800 hover:text-white"
                }`}
              >
                <span className="text-base">{n.icon}</span>
                {n.label}
              </Link>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t border-navy-800 text-[11px] text-navy-400">
          © {new Date().getFullYear()} LPPM · RCMS
        </div>
      </aside>

      {/* ── Konten ── */}
      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200">
          <div className="px-6 py-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-500">{title}</h2>
            <div className="flex items-center gap-4">
              <NotifikasiBell />
              <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-semibold text-navy-900 leading-tight">
                    {user?.nama}
                  </p>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    {ROLE_LABEL[user?.role] || user?.role}
                  </p>
                </div>
                <div className="h-9 w-9 rounded-full bg-navy-100 text-navy-700 grid place-items-center font-bold text-sm">
                  {(user?.nama || "?").charAt(0).toUpperCase()}
                </div>
                <button onClick={logout} className="btn-ghost text-sm" title="Keluar">
                  Keluar
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 px-6 py-8 max-w-6xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
}
