import { definePreset } from "@primevue/themes";
import Aura from "@primevue/themes/aura";

// Primary = coral/pink accent, used for primary buttons, active nav items,
// focus rings, and the "due now" signal across the app.
// Secondary accent (warm yellow) is applied per-component (badges, progress
// bars) rather than as PrimeVue's semantic "primary", since in this app
// yellow plays a highlight role, not an action role.
export const VocabPreset = definePreset(Aura, {
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
