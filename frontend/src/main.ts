/// <reference types="vite/client" />
import "./services/pwa";
import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";

import "primeicons/primeicons.css";
import "./style.css";

import App from "./App.vue";
import router from "./router";
import { VocabPreset } from "./theme";
import { useAuthStore } from "./stores/auth";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: VocabPreset,
    options: {
      darkModeSelector: false, // light-only, per the brand palette
    },
  },
});
app.use(ToastService);
app.use(ConfirmationService);

// Validate any stored token before the first render so a refresh doesn't
// flash logged-in content for a stale/expired token. The router guard also
// checks `initialized` as a safety net for any navigation that beats this.
const authStore = useAuthStore();
authStore.init().finally(() => {
  app.mount("#app");
});
