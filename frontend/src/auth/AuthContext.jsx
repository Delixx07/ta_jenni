// Context autentikasi: menyimpan user yang login & menyediakan login/logout.
import { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Saat aplikasi dibuka, jika ada token coba pulihkan sesi.
  useEffect(() => {
    async function restore() {
      if (getToken()) {
        try {
          setUser(await api.me());
        } catch {
          setToken(null); // token invalid/kedaluwarsa
        }
      }
      setLoading(false);
    }
    restore();
  }, []);

  // Dengarkan event 401 dari API client → paksa logout (sesi habis).
  useEffect(() => {
    const onUnauthorized = () => setUser(null);
    window.addEventListener("rcms:unauthorized", onUnauthorized);
    return () => window.removeEventListener("rcms:unauthorized", onUnauthorized);
  }, []);

  async function login(email, password) {
    const data = await api.login(email, password);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
