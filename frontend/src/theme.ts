import { definePreset } from "@primevue/themes";
import Aura from "@primevue/themes/aura";

export const MementoPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#eff6ff",
      100: "#dbeafe",
      200: "#bfdbfe",
      300: "#93c5fd",
      400: "#60a5fa",
      500: "#0066cc",
      600: "#005bb8",
      700: "#004f9e",
      800: "#003f80",
      900: "#003366",
      950: "#00234d",
    },
    colorScheme: {
      dark: {
        surface: {
          0: "rgb(var(--color-on-primary))",
          50: "rgb(var(--color-heading))",
          100: "rgb(var(--color-body))",
          200: "rgb(var(--color-copy))",
          300: "rgb(var(--color-secondary))",
          400: "rgb(var(--color-quiet))",
          500: "rgb(var(--color-chart-neutral))",
          600: "rgb(var(--color-line-strong))",
          700: "rgb(var(--color-line))",
          800: "rgb(var(--color-subtle))",
          900: "rgb(var(--color-surface))",
          950: "rgb(var(--color-canvas))",
        },
        primary: {
          color: "rgb(var(--color-primary))",
          contrastColor: "rgb(var(--color-on-primary))",
          hoverColor: "rgb(var(--color-primary-hover))",
          activeColor: "#004f9e",
        },
        highlight: {
          background: "rgb(var(--color-accent-muted))",
          focusBackground: "rgb(var(--color-accent-line))",
          color: "rgb(var(--color-accent-strong))",
          focusColor: "rgb(var(--color-accent-strong))",
        },
      },
      light: {
        surface: {
          0: "#ffffff",
          50: "#f5f5f7",
          100: "#eeeff3",
          200: "#dee1e8",
          300: "#c4c9d5",
          400: "#707785",
          500: "#686f7d",
          600: "#636975",
          700: "#494d57",
          800: "#303136",
          900: "#1d1d1f",
          950: "#121215",
        },
        primary: {
          color: "#0066cc",
          contrastColor: "#ffffff",
          hoverColor: "#005bb8",
          activeColor: "#004f9e",
        },
        highlight: {
          background: "#e8f2ff",
          focusBackground: "#bfdbfe",
          color: "#004f9e",
          focusColor: "#004f9e",
        },
      },
    },
  },
});
