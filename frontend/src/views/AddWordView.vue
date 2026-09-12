<template>
  <div class="max-w-3xl mx-auto flex flex-col gap-6">
    <header>
      <h1 class="text-2xl font-semibold">
        Add Vocabulary
      </h1>
      <p class="text-stone-500 mt-1">
        Look up a single word or extract key vocabulary from real-world text.
      </p>
    </header>

    <div class="flex items-center gap-2 p-1 rounded-xl bg-stone-200/70 w-fit">
      <button
        type="button"
        class="px-4 py-2 rounded-lg text-sm font-semibold transition-all"
        :class="activeTab === 'single' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-600 hover:text-stone-900'"
        @click="activeTab = 'single'"
      >
        <i class="pi pi-pencil mr-1.5 text-xs"></i>Single Word
      </button>
      <button
        type="button"
        class="px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-1.5"
        :class="activeTab === 'extract' ? 'bg-white text-pink-600 shadow-sm' : 'text-stone-600 hover:text-stone-900'"
        @click="activeTab = 'extract'"
      >
        <i class="pi pi-sparkles text-xs text-pink-500"></i>
        <span>Learn From Anything</span>
        <span class="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-pink-100 text-pink-700">AI</span>
      </button>
    </div>

    <div v-if="activeTab === 'single'" class="flex flex-col gap-6">
      <section class="rounded-xl2 bg-white border border-stone-200 p-5 shadow-soft flex flex-col sm:flex-row gap-3">
        <InputText
          v-model="wordInput"
          placeholder="e.g. serendipity, call it a day..."
          class="flex-1 text-base"
          @keyup.enter="handleGenerate"
        />
        <button
          type="button"
          class="rounded-full bg-pink-500 hover:bg-pink-600 text-white font-semibold px-6 py-2.5 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          :disabled="!wordInput.trim() || generating"
          @click="handleGenerate"
        >
          <i v-if="generating" class="pi pi-spin pi-spinner text-sm"></i>
          <i v-else class="pi pi-sparkles text-sm"></i>
          <span>Generate with AI</span>
        </button>
      </section>

      <section v-if="form.word" class="rounded-xl2 bg-white border border-stone-200 p-6 shadow-soft flex flex-col gap-5">
        <WordForm :model-value="form" @update:model-value="(v) => Object.assign(form, v)" />
        <div class="flex justify-end gap-3 pt-4 border-t border-stone-100">
          <button
            type="button"
            class="rounded-full bg-pink-500 hover:bg-pink-600 text-white font-semibold px-6 py-2.5 transition-all disabled:opacity-50"
            :disabled="saving"
            @click="handleSaveSingle"
          >
            {{ saving ? "Saving..." : "Save to my list" }}
          </button>
        </div>
      </section>
    </div>

    <div v-else class="flex flex-col gap-6">
      <section class="rounded-xl2 bg-white border border-stone-200 p-5 shadow-soft flex flex-col gap-4">
        <label class="font-medium text-sm text-stone-700">
          Paste an article snippet, email, tweet, or book passage:
        </label>
        <Textarea
          v-model="rawText"
          rows="5"
          placeholder="Paste your English text here... (e.g. 'The team had to pivot quickly because the bottleneck was impeding our scalability...')"
          class="w-full text-sm leading-relaxed p-3"
        />
        <div class="flex justify-between items-center">
          <span class="text-xs text-stone-400">{{ rawText.length }} characters</span>
          <button
            type="button"
            class="rounded-full bg-pink-500 hover:bg-pink-600 text-white font-semibold px-6 py-2.5 transition-all flex items-center gap-2 disabled:opacity-50 shadow-sm"
            :disabled="rawText.trim().length < 15 || extracting"
            @click="handleExtract"
          >
            <i v-if="extracting" class="pi pi-spin pi-spinner text-sm"></i>
            <i v-else class="pi pi-sparkles text-sm"></i>
            <span>{{ extracting ? "Analyzing with AI..." : "Extract Vocabulary" }}</span>
          </button>
        </div>
      </section>

      <section v-if="extractedItems.length" class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h2 class="font-display font-semibold text-lg text-stone-900">
            Extracted Words ({{ extractedItems.length }})
          </h2>
          <button
            type="button"
            class="rounded-full bg-pink-500 hover:bg-pink-600 text-white text-xs font-semibold px-5 py-2 transition-all flex items-center gap-1.5 disabled:opacity-50"
            :disabled="selectedCount() === 0 || savingBatch"
            @click="handleSaveBatch"
          >
            <i v-if="savingBatch" class="pi pi-spin pi-spinner text-xs"></i>
            <i v-else class="pi pi-plus text-xs"></i>
            <span>Add {{ selectedCount() }} Selected to Library</span>
          </button>
        </div>

        <div class="grid gap-3">
          <div
            v-for="item in extractedItems"
            :key="item.word"
            class="rounded-xl bg-white border p-4 shadow-sm transition-all flex items-start gap-3.5"
            :class="selectedItems[item.word] ? 'border-pink-300 ring-1 ring-pink-300' : 'border-stone-200 opacity-80'"
          >
            <input
              v-if="!item.already_in_library"
              v-model="selectedItems[item.word]"
              type="checkbox"
              class="mt-1 w-4 h-4 rounded text-pink-500 focus:ring-pink-400 cursor-pointer"
            />
            <span v-else class="mt-1 text-xs px-2 py-0.5 rounded bg-stone-100 text-stone-500 font-medium">Saved</span>

            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 mb-1">
                <div class="flex items-center gap-2">
                  <h3 class="font-display font-bold text-lg text-stone-900">
                    {{ item.word }}
                  </h3>
                  <SpeakButton :text="item.word" size="sm" />
                </div>
                <DifficultyBadge :difficulty="item.difficulty" />
              </div>

              <p class="text-sm text-stone-700 mb-2">
                {{ item.definition }}
              </p>

              <div v-if="item.context_sentence" class="bg-yellow-50/70 border-l-2 border-yellow-400 px-3 py-1.5 rounded-r text-xs text-stone-700 italic mb-2">
                &ldquo;{{ item.context_sentence }}&rdquo;
              </div>

              <div class="flex flex-wrap gap-1">
                <CategoryChip v-for="c in item.categories" :key="c">
                  {{ c }}
                </CategoryChip>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import DifficultyBadge from "@/components/DifficultyBadge.vue";
import CategoryChip from "@/components/CategoryChip.vue";
import SpeakButton from "@/components/SpeakButton.vue";
import WordForm from "@/components/WordForm.vue";
import { useWordsStore } from "@/stores/words";
import { api, apiErrorMessage } from "@/services/api";
import type { NewWordPayload } from "@/types";

const router = useRouter();
const store = useWordsStore();
const toast = useToast();

const activeTab = ref<"single" | "extract">("single");

const wordInput = ref("");
const generating = ref(false);
const saving = ref(false);

function emptyPayload(word = ""): NewWordPayload {
  return {
    word,
    pronunciation: "",
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
  try {
    const info = await api.generateWordInfo(w);
    Object.assign(form, {
      word: info.word,
      pronunciation: info.pronunciation,
      definition: info.definition,
      examples: info.examples,
      usage_notes: info.usage_notes,
      collocations: info.collocations,
      difficulty: info.difficulty,
      categories: info.categories,
    });
    toast.add({ severity: "success", summary: "Ready to save", detail: `Generated definition for "${info.word}"`, life: 2000 });
  } catch (e) {
    Object.assign(form, emptyPayload(w));
    toast.add({ severity: "error", summary: "Couldn't generate", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    generating.value = false;
  }
}

async function handleSaveSingle() {
  if (!form.word || !form.definition) return;
  saving.value = true;
  try {
    await store.createWord(form);
    toast.add({ severity: "success", summary: "Word saved", detail: `"${form.word}" added to your library!`, life: 2000 });
    router.push("/library");
  } catch (e) {
    toast.add({ severity: "error", summary: "Couldn't save", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    saving.value = false;
  }
}

const rawText = ref("");
const extracting = ref(false);
const savingBatch = ref(false);
const extractedItems = ref<any[]>([]);
const selectedItems = ref<Record<string, boolean>>({});

async function handleExtract() {
  if (!rawText.value.trim() || rawText.value.trim().length < 15) {
    toast.add({ severity: "warn", summary: "Too short", detail: "Please paste a longer text excerpt.", life: 3000 });
    return;
  }
  extracting.value = true;
  extractedItems.value = [];
  try {
    const items = await api.extractWordsFromText(rawText.value);
    extractedItems.value = items;
    const selected: Record<string, boolean> = {};
    items.forEach((item) => {
      if (!item.already_in_library) {
        selected[item.word] = true;
      }
    });
    selectedItems.value = selected;
    toast.add({ severity: "success", summary: "Extracted!", detail: `Found ${items.length} key vocabulary items!`, life: 3000 });
  } catch (e) {
    toast.add({ severity: "error", summary: "Extraction failed", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    extracting.value = false;
  }
}

const selectedCount = () => Object.values(selectedItems.value).filter(Boolean).length;

async function handleSaveBatch() {
  const toAdd = extractedItems.value.filter((item) => selectedItems.value[item.word]);
  if (!toAdd.length) return;
  savingBatch.value = true;
  try {
    const res = await api.batchCreateWords(toAdd);
    toast.add({ severity: "success", summary: "Added to Library!", detail: `Saved ${res.created_count} words to your library!`, life: 2500 });
    await store.fetchStats();
    router.push("/library");
  } catch (e) {
    toast.add({ severity: "error", summary: "Couldn't save words", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    savingBatch.value = false;
  }
}
</script>
