// Primitif UI bergaya kampus, dipakai berulang agar tampilan konsisten.

export function Loading({ text = "Memuat…" }) {
  return (
    <div className="flex items-center gap-3 text-slate-500 py-8">
      <span className="h-4 w-4 rounded-full border-2 border-navy-200 border-t-navy-600 animate-spin" />
      {text}
    </div>
  );
}

export function EmptyState({ icon = "📭", text, action }) {
  return (
    <div className="text-center text-slate-400 py-12 border border-dashed border-slate-300 rounded-xl bg-white">
      <div className="text-4xl mb-2">{icon}</div>
      <p>{text}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-4 flex items-start gap-2">
      <span>⚠</span>
      <span>{message}</span>
    </div>
  );
}

export function SuccessBanner({ message }) {
  if (!message) return null;
  return (
    <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg px-4 py-3 mb-4 flex items-start gap-2">
      <span>✓</span>
      <span>{message}</span>
    </div>
  );
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-start justify-between gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">{title}</h1>
        {subtitle && <p className="text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Card({ children, className = "" }) {
  return <div className={`card p-5 ${className}`}>{children}</div>;
}

// Badge status dengan warna sesuai makna.
const BADGE_STYLES = {
  // status proyek / tugas / undangan
  draft: "bg-slate-100 text-slate-600",
  aktif: "bg-emerald-100 text-emerald-700",
  selesai: "bg-navy-100 text-navy-700",
  dibatalkan: "bg-red-100 text-red-700",
  todo: "bg-slate-100 text-slate-600",
  in_progress: "bg-amber-100 text-amber-700",
  done: "bg-emerald-100 text-emerald-700",
  terkirim: "bg-amber-100 text-amber-700",
  diterima: "bg-emerald-100 text-emerald-700",
  ditolak: "bg-red-100 text-red-700",
};

export function Badge({ children, tone }) {
  const style = BADGE_STYLES[tone] || "bg-slate-100 text-slate-600";
  return <span className={`badge ${style}`}>{children}</span>;
}

// Format rupiah dipakai di banyak halaman keuangan.
export const rupiah = (n) =>
  "Rp " + Number(n).toLocaleString("id-ID", { maximumFractionDigits: 0 });
