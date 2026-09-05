/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        pink: {
          50: "#fef1f4",
          100: "#fde3e9",
          200: "#fac2cf",
          300: "#f698ae",
          400: "#f26989",
          500: "#ef476f",
          600: "#eb184a",
          700: "#bf113a",
          800: "#900d2c",
          900: "#6b0921",
          950: "#4a0617",
        },
        yellow: {
          50: "#fffaf0",
          100: "#fff6e0",
          200: "#ffebbd",
          300: "#ffdd8f",
          400: "#ffce5c",
          500: "#ffd166",
          600: "#ffc233",
          700: "#ffb200",
          800: "#cc8f00",
          900: "#a37200",
          950: "#7f5900",
        },
        // Warm, restrained neutral scale used for backgrounds, borders, text.
        stone: {
          25: "#fefdfb",
          50: "#faf8f5",
          100: "#f3f0ea",
          200: "#e8e3da",
          300: "#d6cfc2",
          400: "#b3a89a",
          500: "#8c8071",
          600: "#6b6156",
          700: "#4c4640",
          800: "#332f2b",
          900: "#211e1b",
        },
      },
      fontFamily: {
        display: ["Fraunces", "ui-serif", "Georgia", "serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(33, 30, 27, 0.04), 0 8px 24px -12px rgba(33, 30, 27, 0.10)",
      },
    },
  },
  plugins: [],
};
