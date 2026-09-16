<template>
  <div class="flex flex-col gap-6">
    <section class="library-toolbar glass-panel rounded-xl2 border px-4 sm:px-5 py-4 flex flex-col sm:flex-row sm:flex-wrap gap-3 sm:items-center">
      <IconField class="w-full sm:max-w-xs">
        <InputIcon class="pi pi-search pointer-events-none" aria-hidden="true" />
        <InputText
          v-model="search"
          placeholder="Search words"
          aria-label="Search words"
          class="w-full"
        />
      </IconField>
      <Select
        v-model="categoryFilter"
        :options="store.categories"
        placeholder="All categories"
        show-clear
        class="w-full sm:w-48"
      />
      <Select
        v-model="difficultyFilter"
        :options="difficultyOptions"
        option-label="label"
        option-value="value"
        placeholder="All difficulties"
        show-clear
        class="w-full sm:w-48"
      />
      <button
        type="button"
        class="rounded-full px-4 py-2 text-sm font-medium border transition-colors whitespace-nowrap"
        :class="
          dueOnly
            ? 'glass-control glass-primary border-primary text-on-primary'
            : 'glass-control border-line text-secondary hover:border-accent-line-strong'
        "
        @click="dueOnly = !dueOnly"
      >
        <i class="pi pi-bolt mr-1.5"></i>Due only
      </button>
    </section>

    <p v-if="!store.loading && !searchPending && !store.error" class="text-xs text-faint -mt-2">
      {{ resultCountLabel }}
    </p>

    <p v-if="store.categoriesError" class="text-sm text-quiet" role="alert">
      {{ store.categoriesError }}
      <button class="min-h-11 px-2 font-medium text-accent" @click="store.fetchCategories()">
        Try again
      </button>
    </p>
    <StatePanel v-if="store.loading || searchPending" kind="loading" title="Gathering your words…" />
    <StatePanel
      v-else-if="store.error"
      kind="error"
      title="Your library is taking a little longer"
      :description="store.error"
      action-label="Try again"
      @action="refresh"
    />
    <section v-else-if="visibleWords.length" class="flex flex-col gap-3">
      <div
        v-for="w in visibleWords"
        :key="w.id"
        class="library-row rounded-xl2 content-panel border px-5 py-4 flex flex-col xl:flex-row xl:items-center gap-3 xl:gap-5 hover:border-accent-line transition-colors cursor-pointer"
        @click="openEdit(w)"
      >
        <div class="flex items-center gap-2 xl:w-48 shrink-0">
          <span
            v-if="w.is_due && !w.is_mastered"
            class="w-2 h-2 rounded-full bg-warning shrink-0"
            title="Due for review"
          ></span>
          <span class="font-display text-lg font-semibold text-heading truncate">{{ w.word }}</span>
          <SpeakButton :text="w.word" size="sm" />
        </div>
        <p class="text-sm text-quiet line-clamp-2 flex-1 min-w-0">
          {{ w.definition }}
        </p>
        <div class="flex items-center gap-2 flex-wrap shrink-0">
          <DifficultyBadge :difficulty="w.difficulty" />
          <CategoryChip v-for="c in w.categories.slice(0, 2)" :key="c">
            {{ c }}
          </CategoryChip>
        </div>
        <div class="flex items-center gap-1 shrink-0" @click.stop>
          <MasteryAction :word="w" />
          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full text-faint transition-colors hover:bg-accent-soft hover:text-accent"
            aria-label="Delete word"
            title="Delete word"
            @click="confirmDelete(w)"
          >
            <i class="pi pi-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </section>

    <StatePanel
      v-else-if="hasFilters"
      title="No words in this corner yet"
      description="Try another search, or clear your filters to explore the rest of your library."
      action-label="Clear filters"
      @action="clearFilters"
    />
    <StatePanel
      v-else
      title="Your universe starts with one word."
      description="Save a word you’re curious about. We’ll help it stick."
      action-label="Add your first word"
      to="/add"
    />

    <Dialog
      :visible="!!editing"
      modal
      dismissable-mask
      :header="editing?.word ?? ''"
      class="w-full max-w-2xl mx-4"
      @update:visible="(v) => !v && (editing = null)"
    >
      <WordForm v-if="editing" :model-value="editForm" @update:model-value="updateEditForm" />
      <template #footer>
        <button
          type="button"
          class="rounded-full glass-control border border-line text-secondary hover:bg-subtle text-sm font-semibold px-5 py-2.5 transition-colors mr-2"
          @click="editing = null"
        >
          Cancel
        </button>
        <button
          type="button"
          class="rounded-full glass-primary glass-control hover:bg-primary-hover text-on-primary text-sm font-semibold px-5 py-2.5 transition-colors disabled:opacity-60"
          :disabled="savingEdit"
          @click="saveEdit"
        >
          Save changes
        </button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import StatePanel from "@/components/StatePanel.vue";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import InputText from "primevue/inputtext";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import Select from "primevue/select";
import Dialog from "primevue/dialog";
import DifficultyBadge from "@/components/DifficultyBadge.vue";
import CategoryChip from "@/components/CategoryChip.vue";
import WordForm from "@/components/WordForm.vue";
import SpeakButton from "@/components/SpeakButton.vue";
import MasteryAction from "@/components/MasteryAction.vue";
import { useWordsStore } from "@/stores/words";
import { apiErrorMessage } from "@/services/api";
import type { Difficulty, NewWordPayload, Word } from "@/types";

const store = useWordsStore();
const toast = useToast();
const confirm = useConfirm();

const search = ref("");
const categoryFilter = ref<string | null>(null);
const difficultyFilter = ref<Difficulty | null>(null);
const dueOnly = ref(false);
const visibleWords = computed(() => dueOnly.value ? store.words.filter((word) => !word.is_mastered) : store.words);
const searchPending = ref(false);
const hasFilters = computed(() => !!(search.value || categoryFilter.value || difficultyFilter.value || dueOnly.value));

function clearFilters() {
  search.value = "";
  categoryFilter.value = null;
  difficultyFilter.value = null;
  dueOnly.value = false;
}

const difficultyOptions: { label: string; value: Difficulty }[] = [
  { label: "Beginner", value: "beginner" },
  { label: "Intermediate", value: "intermediate" },
  { label: "Advanced", value: "advanced" },
];

async function refresh() {
  await store.fetchWords({
    search: search.value || undefined,
    category: categoryFilter.value || undefined,
    difficulty: difficultyFilter.value || undefined,
    due: dueOnly.value || undefined,
  });
}

let debounceHandle: ReturnType<typeof setTimeout> | undefined;
watch(search, () => {
  clearTimeout(debounceHandle);
  searchPending.value = true;
  debounceHandle = setTimeout(() => {
    searchPending.value = false;
    void refresh();
  }, 300);
});
onUnmounted(() => clearTimeout(debounceHandle));
watch([categoryFilter, difficultyFilter, dueOnly], refresh);

onMounted(async () => {
  await Promise.all([refresh(), store.fetchCategories()]);
});

const editing = ref<Word | null>(null);
const editForm = reactive<NewWordPayload>({
  word: "",
  pronunciation: "",
  definition: "",
  examples: [],
  usage_notes: "",
  collocations: [],
  difficulty: "intermediate",
  categories: [],
});
const savingEdit = ref(false);

function openEdit(word: Word) {
  editing.value = word;
  Object.assign(editForm, {
    word: word.word,
    pronunciation: word.pronunciation ?? "",
    definition: word.definition,
    examples: [...word.examples],
    usage_notes: word.usage_notes,
    collocations: [...word.collocations],
    difficulty: word.difficulty,
    categories: [...word.categories],
  });
}

function updateEditForm(v: NewWordPayload) {
  Object.assign(editForm, v);
}

async function saveEdit() {
  if (!editing.value) return;
  savingEdit.value = true;
  try {
    await store.updateWord(editing.value.id, editForm);
    toast.add({ severity: "success", summary: "Saved", life: 2000 });
    editing.value = null;
    refresh();
  } catch (e) {
    toast.add({ severity: "error", summary: "Couldn't save", detail: apiErrorMessage(e), life: 4000 });
  } finally {
    savingEdit.value = false;
  }
}

function confirmDelete(word: Word) {
  confirm.require({
    message: `Remove "${word.word}" from your list? This can't be undone.`,
    header: "Delete word",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: "Delete",
    acceptProps: { severity: "danger" },
    rejectLabel: "Cancel",
    rejectProps: { text: true, severity: "secondary" },
    accept: async () => {
      try {
        await store.deleteWord(word.id);
        toast.add({ severity: "success", summary: "Word deleted", life: 2000 });
      } catch (e) {
        toast.add({ severity: "error", summary: "Couldn't delete", detail: apiErrorMessage(e), life: 4000 });
      }
    },
  });
}

const resultCountLabel = computed(() => {
  const n = visibleWords.value.length;
  return n === 1 ? "1 word" : `${n} words`;
});
</script>
