/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Identitas kampus: navy (utama) + emas (aksen).
        navy: {
          50: "#f0f4f9",
          100: "#d9e2ef",
          200: "#b3c5df",
          300: "#8aa6cd",
          400: "#5d80b5",
          500: "#3d6098",
          600: "#2f4b7a",
          700: "#1f3a63",
          800: "#142a4d",
          900: "#0c1d38",
        },
        gold: {
          50: "#fdf8ec",
          100: "#f8ecc6",
          200: "#f0d98a",
          300: "#e7c14d",
          400: "#dba91f",
          500: "#c2900f",
          600: "#9c6f0c",
        },
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
        serif: ["Georgia", "Cambria", "serif"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(12,29,56,0.06), 0 1px 2px rgba(12,29,56,0.04)",
        elevated: "0 4px 16px rgba(12,29,56,0.10)",
      },
    },
  },
  plugins: [],
};
