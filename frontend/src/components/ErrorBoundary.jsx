// Error boundary: menangkap error render tak terduga agar aplikasi tidak
// menampilkan layar putih, melainkan pesan ramah + tombol muat ulang.
import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // Untuk skripsi cukup log ke konsol; bisa dikirim ke layanan monitoring.
    console.error("Render error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
          <div className="text-center">
            <p className="text-xl font-semibold text-slate-700">Terjadi kesalahan.</p>
            <p className="text-slate-500 mt-1">Silakan muat ulang halaman.</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded-lg bg-slate-800 text-white px-5 py-2 text-sm font-medium hover:bg-slate-700"
            >
              Muat Ulang
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
