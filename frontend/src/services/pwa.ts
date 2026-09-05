import { ref } from "vue";

interface InstallPrompt extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export const installPrompt = ref<InstallPrompt | null>(null);
const standalone = window.matchMedia("(display-mode: standalone)");
export const isInstalled = ref(standalone.matches ||
  (navigator as Navigator & { standalone?: boolean }).standalone === true);
standalone.addEventListener("change", (event) => { isInstalled.value = event.matches; });
window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt.value = event as InstallPrompt;
});
window.addEventListener("appinstalled", () => {
  isInstalled.value = true;
  installPrompt.value = null;
});

export async function installApp() {
  const prompt = installPrompt.value;
  if (!prompt) return;
  try {
    await prompt.prompt();
    await prompt.userChoice;
  } finally {
    installPrompt.value = null;
  }
}

// Keep development free of service-worker interception.
if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      console.warn("Vocab offline support could not be registered.");
    });
  });
}
