// Route guard: alihkan ke /login bila belum terautentikasi.
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8 text-slate-500">Memuat…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
