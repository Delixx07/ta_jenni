// Halaman 404 untuk rute yang tidak dikenal.
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
      <div className="text-center">
        <p className="text-6xl font-bold text-slate-300">404</p>
        <p className="text-slate-600 mt-2">Halaman tidak ditemukan.</p>
        <Link
          to="/dashboard"
          className="inline-block mt-4 rounded-lg bg-slate-800 text-white px-5 py-2 text-sm font-medium hover:bg-slate-700"
        >
          Kembali ke Dashboard
        </Link>
      </div>
    </div>
  );
}
