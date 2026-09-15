<template>
  <button
    v-if="!isInstalled"
    type="button"
    :disabled="installing"
    class="glass-control inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-full border border-line py-2.5 text-sm font-semibold text-secondary transition-colors hover:border-line-strong hover:text-copy disabled:cursor-wait disabled:opacity-50"
    :class="compact ? 'min-w-11 px-3 sm:px-5' : 'px-5'"
    aria-label="Install app"
    title="Install app"
    @click="install"
  >
    <i :class="installing ? 'pi pi-spinner pi-spin' : 'pi pi-download'" aria-hidden="true"></i>
    <span class="whitespace-nowrap" :class="{ 'hidden sm:inline': compact }">Install app</span>
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

defineProps<{ compact?: boolean }>();

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
