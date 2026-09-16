<template>
  <div class="flex flex-col gap-6">
    <div class="flex w-full min-w-0 flex-col gap-6">
      <div class="capture-tabs flex items-center gap-2 p-1 rounded-xl glass-control border border-line w-fit">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border text-sm font-semibold transition-colors"
          :class="activeTab === 'single' ? 'bg-accent-muted border-accent-line-strong text-accent-strong shadow-sm' : 'border-transparent text-secondary hover:text-heading'"
          :aria-pressed="activeTab === 'single'"
          @click="activeTab = 'single'"
        >
          <i class="pi pi-pencil mr-1.5 text-xs"></i>Single Word
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg border text-sm font-semibold transition-colors flex items-center gap-1.5"
          :class="activeTab === 'extract' ? 'bg-accent-muted border-accent-line-strong text-accent-strong shadow-sm' : 'border-transparent text-secondary hover:text-heading'"
          :aria-pressed="activeTab === 'extract'"
          @click="activeTab = 'extract'"
        >
          <i class="pi pi-sparkles text-xs"></i>
          <span>Learn From Anything</span>
          <span class="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-accent-muted text-accent-strong">AI</span>
        </button>
      </div>

      <div v-if="activeTab === 'single'" class="flex flex-col gap-6">
        <section class="rounded-xl2 content-panel border p-5 flex flex-col gap-3">
          <div class="flex flex-col gap-3 sm:flex-row">
            <InputText
              id="word-search"
              v-model="wordInput"
              aria-label="Word or phrase"
              aria-describedby="word-search-help"
              placeholder="e.g. serendipity, call it a day..."
              class="flex-1 text-base"
              @keyup.enter="handleGenerate"
            />
            <button
              type="button"
              class="rounded-full glass-primary glass-control hover:bg-primary-hover text-on-primary font-semibold px-6 py-2.5 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              :disabled="!wordInput.trim() || generating"
              @click="handleGenerate"
            >
              <i v-if="generating" class="pi pi-spin pi-spinner text-sm" aria-hidden="true"></i>
              <i v-else class="pi pi-sparkles text-sm" aria-hidden="true"></i>
              <span>Generate with AI</span>
            </button>
          </div>
          <p id="word-search-help" class="text-xs text-quiet">
            Explore a word’s meaning and examples, then save it for practice.
          </p>
        </section>

        <section v-if="form.word" class="rounded-xl2 content-panel border p-6 flex flex-col gap-5">
          <WordForm :model-value="form" @update:model-value="(v) => Object.assign(form, v)" />
          <div class="flex justify-end gap-3 pt-4 border-t border-line-soft">
            <button
              type="button"
              class="rounded-full glass-primary glass-control hover:bg-primary-hover text-on-primary font-semibold px-6 py-2.5 transition-all disabled:opacity-50"
              :disabled="saving"
              @click="handleSaveSingle"
            >
              {{ saving ? "Saving..." : "Save to my list" }}
            </button>
          </div>
        </section>
      </div>

      <div v-else class="flex flex-col gap-6">
        <section class="rounded-xl2 content-panel border p-5 flex flex-col gap-4">
          <label for="extract-text" class="font-medium text-sm text-copy">
            Paste an article snippet, email, tweet, or book passage:
          </label>
          <Textarea
            id="extract-text"
            v-model="rawText"
            aria-describedby="extract-text-help"
            rows="5"
            placeholder="Paste your English text here... (e.g. 'The team had to pivot quickly because the bottleneck was impeding our scalability...')"
            class="w-full text-sm leading-relaxed p-3"
          />
          <p id="extract-text-help" class="text-xs text-quiet">
            Use at least 15 characters. We’ll find words you can choose to save.
          </p>
          <div class="flex justify-between items-center">
            <span class="text-xs text-faint">{{ rawText.length }} characters</span>
            <button
              type="button"
              class="rounded-full glass-primary glass-control hover:bg-primary-hover text-on-primary font-semibold px-6 py-2.5 transition-all flex items-center gap-2 disabled:opacity-50"
              :disabled="rawText.trim().length < 15 || extracting"
              @click="handleExtract"
            >
              <i v-if="extracting" class="pi pi-spin pi-spinner text-sm" aria-hidden="true"></i>
              <i v-else class="pi pi-sparkles text-sm" aria-hidden="true"></i>
              <span>{{ extracting ? "Analyzing with AI..." : "Extract Vocabulary" }}</span>
            </button>
          </div>
        </section>

        <StatePanel
          v-if="extracted && !extractedItems.length"
          title="No new stars in this passage"
          description="Try a longer passage, or choose a word you’d like to explore on its own."
          action-label="Try another passage"
          @action="focusInput('extract-text')"
        />
        <StatePanel
          v-else-if="allAlreadySaved"
          title="These stars are already in your universe."
          description="Every word we found is already in your library. Revisit them, or explore a different passage."
          action-label="Browse your library"
          to="/library"
        />
        <section v-if="extractedItems.length" class="flex flex-col gap-4">
          <div class="flex items-center justify-between">
            <h2 class="font-display font-semibold text-lg text-heading">
              Extracted Words ({{ extractedItems.length }})
            </h2>
            <button
              type="button"
              class="rounded-full glass-primary glass-control hover:bg-primary-hover text-on-primary text-xs font-semibold px-5 py-2 transition-all flex items-center gap-1.5 disabled:opacity-50"
              :disabled="selectedCount() === 0 || savingBatch"
              @click="handleSaveBatch"
            >
              <i v-if="savingBatch" class="pi pi-spin pi-spinner text-xs"></i>
              <i v-else class="pi pi-plus text-xs"></i>
              <span>Add {{ selectedCount() }} Selected to Library</span>
            </button>
          </div>
          <p v-if="!allAlreadySaved && selectedCount() === 0" class="text-sm text-quiet" role="status">
            Which words spark your curiosity? Select a word to add it to your library.
          </p>

          <div class="grid gap-3">
            <div
              v-for="item in extractedItems"
              :key="item.word"
              class="rounded-xl content-panel border p-4 transition-all flex items-start gap-3.5"
              :class="selectedItems[item.word] ? 'border-accent-line-strong ring-1 ring-accent-line-strong' : 'border-line opacity-80'"
            >
              <input
                v-if="!item.already_in_library"
                v-model="selectedItems[item.word]"
                type="checkbox"
                class="mt-1 w-4 h-4 shrink-0 rounded accent-primary focus-visible:outline-accent cursor-pointer"
              />
              <span v-else class="mt-1 text-xs px-2 py-0.5 rounded bg-subtle text-quiet font-medium">Saved</span>

              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2 mb-1">
                  <div class="flex items-center gap-2">
                    <h3 class="font-display font-bold text-lg text-heading">
                      {{ item.word }}
                    </h3>
                    <SpeakButton :text="item.word" size="sm" />
                  </div>
                  <DifficultyBadge :difficulty="item.difficulty" />
                </div>

                <p class="text-sm text-copy mb-2">
                  {{ item.definition }}
                </p>

                <div v-if="item.context_sentence" class="bg-warning-soft/70 border-l-2 border-warning px-3 py-1.5 rounded-r text-xs text-copy italic mb-2">
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
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import StatePanel from "@/components/StatePanel.vue";
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
    if (!form.word) Object.assign(form, emptyPayload(w));
    toast.add({ severity: "error", summary: "Couldn't generate this word", detail: `${apiErrorMessage(e)} Your draft is kept. Try again, or add the details yourself.`, life: 5000 });
  } finally {
    generating.value = false;
  }
}

async function handleSaveSingle() {
  if (saving.value) return;
  if (!form.word.trim() || !form.definition.trim()) {
    toast.add({ severity: "warn", summary: "Give your word a meaning", detail: "Add a word and a definition before saving it to your library.", life: 4000 });
    return;
  }
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
const extracted = ref(false);
const extractedItems = ref<any[]>([]);
const selectedItems = ref<Record<string, boolean>>({});
const allAlreadySaved = computed(() => extractedItems.value.length > 0 && extractedItems.value.every((item) => item.already_in_library));

function focusInput(id: string) {
  document.getElementById(id)?.focus();
}

async function handleExtract() {
  if (extracting.value) return;
  if (!rawText.value.trim() || rawText.value.trim().length < 15) {
    toast.add({ severity: "warn", summary: "Too short", detail: "Please paste a longer text excerpt.", life: 3000 });
    return;
  }
  extracting.value = true;
  extracted.value = false;
  extractedItems.value = [];
  try {
    const items = await api.extractWordsFromText(rawText.value);
    extractedItems.value = items;
    extracted.value = true;
    const selected: Record<string, boolean> = {};
    items.forEach((item) => {
      if (!item.already_in_library) {
        selected[item.word] = true;
      }
    });
    selectedItems.value = selected;
    if (items.length) toast.add({ severity: "success", summary: "New discoveries", detail: `Found ${items.length} words to explore.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: "error", summary: "Couldn't extract words", detail: `${apiErrorMessage(e)} Your text has been kept, so you can try again.`, life: 5000 });
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
