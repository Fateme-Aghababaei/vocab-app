import "./services/pwa";
import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";
import Tooltip from "primevue/tooltip";

import "primeicons/primeicons.css";
import "./style.css";

import App from "./App.vue";
import router from "./router";
import { MementoPreset } from "./theme";
import { useAuthStore } from "./stores/auth";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: MementoPreset,
    options: {
      darkModeSelector: '[data-theme="dark"]',
    },
  },
});
app.use(ToastService);
app.use(ConfirmationService);
app.directive("tooltip", Tooltip);

const authStore = useAuthStore();
authStore.init().finally(() => {
  app.mount("#app");
});
