<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import InputText from "primevue/inputtext";
import WordForm from "@/components/WordForm.vue";
import { api, apiErrorMessage } from "@/services/api";
import { useWordsStore } from "@/stores/words";
import type { NewWordPayload } from "@/types";

const router = useRouter();
const toast = useToast();
const store = useWordsStore();

const step = ref<"input" | "review">("input");
const wordInput = ref("");
const generating = ref(false);
const saving = ref(false);
const genError = ref("");

function emptyPayload(word = ""): NewWordPayload {
  return {
    word,
    definition: "",
    examples: [],
    usage_notes: "",
    collocations: [],
    difficulty: "intermediate",
    categories: [],
  };
}

const form = reactive<NewWordPayload>(emptyPayload());

async function handleGenerate() {
  const w = wordInput.value.trim();
  if (!w || generating.value) return;
  generating.value = true;
  genError.value = "";
  try {
    const info = await api.generateWordInfo(w);
    Object.assign(form, info);
    step.value = "review";
  } catch (e) {
    genError.value = apiErrorMessage(e);
    // Let the learner continue manually even if Gemini is unavailable.
    Object.assign(form, emptyPayload(w));
    step.value = "review";
  } finally {
    generating.value = false;
  }
}

function updateForm(v: NewWordPayload) {
  Object.assign(form, v);
}

async function handleSave() {
  if (!form.word.trim()) {
    toast.add({ severity: "warn", summary: "Word is required", life: 3000 });
    return;
  }
  saving.value = true;
  try {
    await store.createWord({ ...form, word: form.word.trim() });
    toast.add({ severity: "success", summary: "Word saved", detail: `"${form.word}" added to your list.`, life: 3000 });
    router.push("/library");
  } catch (e) {
    toast.add({ severity: "error", summary: "Couldn't save word", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    saving.value = false;
  }
}

function startOver() {
  step.value = "input";
  wordInput.value = "";
  genError.value = "";
  Object.assign(form, emptyPayload());
}
</script>

<template>
  <div class="max-w-2xl mx-auto flex flex-col gap-6">
    <header>
      <h1 class="text-2xl font-semibold">Add a word</h1>
      <p class="text-stone-500 mt-1">
        Type a word you came across &mdash; we'll draft the definition, examples, and everything
        else so you can review and tweak it.
      </p>
    </header>

    <section v-if="step === 'input'" class="rounded-xl2 bg-white border border-stone-200 px-6 py-8 flex flex-col gap-4">
      <label for="new-word" class="text-sm font-medium text-stone-700">Word or phrase</label>
      <div class="flex flex-col sm:flex-row gap-3">
        <InputText
          id="new-word"
          v-model="wordInput"
          placeholder="e.g. meticulous"
          class="w-full text-lg"
          @keyup.enter="handleGenerate"
        />
        <button
          type="button"
          class="shrink-0 rounded-full bg-pink-500 hover:bg-pink-600 disabled:bg-stone-300 disabled:cursor-not-allowed text-white font-semibold px-6 py-2.5 transition-colors flex items-center justify-center gap-2"
          :disabled="!wordInput.trim() || generating"
          @click="handleGenerate"
        >
          <i v-if="generating" class="pi pi-spin pi-spinner"></i>
          {{ generating ? "Generating\u2026" : "Generate with AI" }}
        </button>
      </div>
      <p class="text-xs text-stone-400">
        Powered by Gemini Flash. You can edit everything it produces, or skip straight to filling
        it in yourself.
      </p>
    </section>

    <section v-else class="flex flex-col gap-6">
      <div
        v-if="genError"
        class="rounded-xl bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm px-4 py-3"
      >
        Couldn't auto-generate details ({{ genError }}). You can still fill everything in below.
      </div>

      <div class="rounded-xl2 bg-white border border-stone-200 px-6 py-7">
        <WordForm :model-value="form" @update:model-value="updateForm" />
      </div>

      <div class="flex items-center justify-between gap-3 sticky bottom-4">
        <button
          type="button"
          class="rounded-full bg-white border border-stone-200 text-stone-600 hover:bg-stone-100 text-sm font-semibold px-5 py-2.5 transition-colors"
          @click="startOver"
        >
          Start over
        </button>
        <button
          type="button"
          class="rounded-full bg-pink-500 hover:bg-pink-600 disabled:bg-stone-300 text-white font-semibold px-6 py-2.5 transition-colors flex items-center gap-2"
          :disabled="saving"
          @click="handleSave"
        >
          <i v-if="saving" class="pi pi-spin pi-spinner"></i>
          Save word
        </button>
      </div>
    </section>
  </div>
</template>
