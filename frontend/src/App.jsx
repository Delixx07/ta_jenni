import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import RequireAuth from "./auth/RequireAuth";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilPage from "./pages/ProfilPage";
import MatchmakingPage from "./pages/MatchmakingPage";
import ProyekPage from "./pages/ProyekPage";
import UndanganPage from "./pages/UndanganPage";
import KanbanPage from "./pages/KanbanPage";
import KeuanganPage from "./pages/KeuanganPage";
import RapatPage from "./pages/RapatPage";
import HibahPage from "./pages/HibahPage";
import NotFoundPage from "./pages/NotFoundPage";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <DashboardPage />
              </RequireAuth>
            }
          />
          <Route
            path="/profil"
            element={
              <RequireAuth>
                <ProfilPage />
              </RequireAuth>
            }
          />
          <Route
            path="/matchmaking"
            element={
              <RequireAuth>
                <MatchmakingPage />
              </RequireAuth>
            }
          />
          <Route
            path="/proyek"
            element={
              <RequireAuth>
                <ProyekPage />
              </RequireAuth>
            }
          />
          <Route
            path="/undangan"
            element={
              <RequireAuth>
                <UndanganPage />
              </RequireAuth>
            }
          />
          <Route
            path="/proyek/:proyekId/kanban"
            element={
              <RequireAuth>
                <KanbanPage />
              </RequireAuth>
            }
          />
          <Route
            path="/proyek/:proyekId/keuangan"
            element={
              <RequireAuth>
                <KeuanganPage />
              </RequireAuth>
            }
          />
          <Route
            path="/proyek/:proyekId/rapat"
            element={
              <RequireAuth>
                <RapatPage />
              </RequireAuth>
            }
          />
          <Route
            path="/hibah"
            element={
              <RequireAuth>
                <HibahPage />
              </RequireAuth>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </ErrorBoundary>
  );
}
