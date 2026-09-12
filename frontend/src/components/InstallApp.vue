<template>
  <div v-if="!isInstalled" class="mb-5 rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm">
    <button
      v-if="installPrompt"
      type="button"
      :disabled="installing"
      class="font-medium text-pink-600 disabled:opacity-50"
      @click="install"
    >
      <i class="pi pi-download mr-2" aria-hidden="true"></i>Add Memento to your home screen
    </button>
    <details v-else>
      <summary class="cursor-pointer font-medium text-stone-600">
        Use Memento like an app
      </summary>
      <p class="mt-2 text-stone-500">
        On iPhone, open this site in Safari, tap Share, then Add to Home Screen. On Android, open the browser menu and choose Install app or Add to Home screen.
      </p>
    </details>
    <p v-if="installError" role="status" class="mt-2 text-stone-500">
      {{ installError }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { installApp, installPrompt, isInstalled } from "@/services/pwa";
const installing = ref(false);
const installError = ref("");
async function install() {
  installing.value = true;
  installError.value = "";
  try { await installApp(); }
  catch { installError.value = "Open your browser menu to add Memento to your home screen."; }
  finally { installing.value = false; }
}
</script>
