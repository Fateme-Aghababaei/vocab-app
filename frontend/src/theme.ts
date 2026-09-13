import { definePreset } from "@primevue/themes";
import Aura from "@primevue/themes/aura";

export const MementoPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#fef1f4",
      100: "#fde3e9",
      200: "#fac2cf",
      300: "#f698ae",
      400: "#f26989",
      500: "#ef476f",
      600: "#d93d61",
      700: "#bf113a",
      800: "#900d2c",
      900: "#6b0921",
      950: "#4a0617",
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
          activeColor: "#914e5e",
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
          950: "#161412",
        },
        primary: {
          color: "#ef476f",
          contrastColor: "#ffffff",
          hoverColor: "#d93d61",
          activeColor: "#bf113a",
        },
        highlight: {
          background: "#fde3e9",
          focusBackground: "#fac2cf",
          color: "#900d2c",
          focusColor: "#900d2c",
        },
      },
    },
  },
});
