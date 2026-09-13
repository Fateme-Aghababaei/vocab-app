<template>
  <button
    v-if="!isInstalled"
    type="button"
    :disabled="installing"
    class="header-action w-auto gap-2 px-2 text-xs"
    aria-label="Install app"
    title="Install app"
    @click="install"
  >
    <i :class="installing ? 'pi pi-spinner pi-spin' : 'pi pi-download'" aria-hidden="true"></i>
    <span class="whitespace-nowrap">Install app</span>
  </button>
  <Dialog
    v-model:visible="showHelp"
    modal
    header="Install Memento"
    class="mx-4 w-full max-w-sm"
  >
    <p class="text-sm leading-relaxed text-secondary">
      On iPhone, open this site in Safari, tap Share, then Add to Home Screen. On Android, open the browser menu and choose Install app or Add to Home screen. On desktop, look for the install option in your browser’s address bar or menu.
    </p>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Dialog from "primevue/dialog";
import { installApp, installPrompt, isInstalled } from "@/services/pwa";

const installing = ref(false);
const showHelp = ref(false);

async function install() {
  if (!installPrompt.value) {
    showHelp.value = true;
    return;
  }
  installing.value = true;
  try { await installApp(); }
  catch { showHelp.value = true; }
  finally { installing.value = false; }
}
</script>
