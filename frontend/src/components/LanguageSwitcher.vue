<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { api, apiErrorMessage } from "@/services/api";
import type { StudyLanguage } from "@/types";

const auth = useAuthStore();
const languages = ref<StudyLanguage[]>([]);
const adding = ref(false);
const selected = ref("");
const busy = ref(false);
const error = ref("");
const available = computed(() => languages.value.filter(item => !auth.user?.languages.includes(item.code)));
const name = (code: string) => languages.value.find(item => item.code === code)?.name ?? code;

async function loadLanguages() {
  try {
    languages.value = await api.getLanguages();
    error.value = "";
  } catch (e) {
    error.value = apiErrorMessage(e);
  }
}
onMounted(loadLanguages);

async function selectLanguage(language: string) {
  if (!language || busy.value || language === auth.user?.active_language) return;
  busy.value = true;
  error.value = "";
  try {
    await auth.selectLanguage(language);
    adding.value = false;
    selected.value = "";
  } catch (e) {
    error.value = apiErrorMessage(e);
  } finally {
    busy.value = false;
  }
}

function handleSwitch(event: Event) {
  const input = event.target as HTMLSelectElement;
  const language = input.value;
  // Keep the current selection until the server confirms the change.
  input.value = auth.user?.active_language ?? "en";
  selectLanguage(language);
}
</script>

<template>
  <section class="rounded-xl2 bg-white border border-stone-200 px-4 py-3 mb-6" aria-label="Study languages">
    <div class="flex flex-wrap items-center gap-3">
      <label for="active-language" class="text-sm font-medium text-stone-600">I'm learning</label>
      <select id="active-language" :value="auth.user?.active_language" :disabled="busy" class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm" @change="handleSwitch">
        <option v-for="code in auth.user?.languages" :key="code" :value="code">{{ name(code) }}</option>
      </select>
      <button v-if="available.length" type="button" :disabled="busy" class="text-sm font-semibold text-pink-600 hover:text-pink-700 disabled:opacity-50" @click="adding = !adding">{{ adding ? 'Cancel' : '+ Add language' }}</button>
      <span v-if="busy" role="status" class="text-sm text-stone-400">Switching language…</span>
    </div>
    <form v-if="adding" class="flex flex-wrap items-center gap-3 mt-3" @submit.prevent="selectLanguage(selected)">
      <label for="add-language" class="text-sm text-stone-600">New language</label>
      <select id="add-language" v-model="selected" :disabled="busy" class="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm" required>
        <option value="" disabled>Choose a language</option>
        <option v-for="item in available" :key="item.code" :value="item.code">{{ item.name }}</option>
      </select>
      <button type="submit" :disabled="!selected || busy" class="rounded-full bg-pink-500 text-white px-4 py-2 text-sm font-semibold disabled:opacity-50">Add and switch</button>
    </form>
    <p class="text-xs text-stone-400 mt-2">Each language has its own library and reviews. Save any edits before switching.</p>
    <p v-if="error" role="alert" class="text-sm text-pink-700 mt-2">{{ error }}</p>
    <button v-if="!languages.length && error" type="button" class="text-sm text-pink-600 mt-2" @click="loadLanguages">Reload languages</button>
  </section>
</template>
