import { ref } from "vue";

const storageKey = "memento-theme";
const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
export const isDark = ref(document.documentElement.dataset.theme === "dark");
let hasPreference = false;
try {
  const saved = localStorage.getItem(storageKey);
  hasPreference = saved === "dark" || saved === "light";
} catch {
  // Theme switching also works without persistent storage.
}

function applyTheme(dark: boolean) {
  isDark.value = dark;
  document.documentElement.dataset.theme = dark ? "dark" : "light";
}

export function toggleTheme() {
  applyTheme(!isDark.value);
  hasPreference = true;
  try {
    localStorage.setItem(storageKey, isDark.value ? "dark" : "light");
  } catch {
    // Keep the chosen theme for this session.
  }
}

systemTheme.addEventListener("change", (event) => {
  if (!hasPreference) applyTheme(event.matches);
});

window.addEventListener("storage", (event) => {
  if (event.key !== storageKey && event.key !== null) return;
  hasPreference = event.newValue === "dark" || event.newValue === "light";
  applyTheme(hasPreference ? event.newValue === "dark" : systemTheme.matches);
});
