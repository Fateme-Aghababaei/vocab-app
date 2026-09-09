<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Dialog from "primevue/dialog";
import DifficultyBadge from "@/components/DifficultyBadge.vue";
import CategoryChip from "@/components/CategoryChip.vue";
import WordForm from "@/components/WordForm.vue";
import SpeakButton from "@/components/SpeakButton.vue";
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
  debounceHandle = setTimeout(refresh, 300);
});
watch([categoryFilter, difficultyFilter, dueOnly], refresh);

onMounted(async () => {
  await Promise.all([refresh(), store.fetchCategories()]);
});

// --- Edit dialog ---
const editing = ref<Word | null>(null);
const editForm = reactive<NewWordPayload>({
  word: "",
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
  const n = store.words.length;
  return n === 1 ? "1 word" : `${n} words`;
});
</script>

<template>
  <div class="flex flex-col gap-6">
    <header>
      <h1 class="text-2xl font-semibold">Library</h1>
      <p class="text-stone-500 mt-1">Browse, search, and fine-tune everything you've saved.</p>
    </header>

    <!-- Filters -->
    <section class="rounded-xl2 bg-white border border-stone-200 px-4 sm:px-5 py-4 flex flex-col sm:flex-row gap-3 sm:items-center">
      <span class="p-input-icon-left w-full sm:max-w-xs relative">
        <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-stone-400 text-sm"></i>
        <InputText v-model="search" placeholder="Search words" class="w-full pl-9" />
      </span>
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
            ? 'bg-pink-500 border-pink-500 text-white'
            : 'bg-white border-stone-200 text-stone-600 hover:border-pink-300'
        "
        @click="dueOnly = !dueOnly"
      >
        <i class="pi pi-bolt mr-1.5"></i>Due only
      </button>
    </section>

    <p class="text-xs text-stone-400 -mt-2">{{ resultCountLabel }}</p>

    <!-- List -->
    <section v-if="store.words.length" class="flex flex-col gap-3">
      <div
        v-for="w in store.words"
        :key="w.id"
        class="rounded-xl2 bg-white border border-stone-200 px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-5 hover:border-pink-200 transition-colors cursor-pointer"
        @click="openEdit(w)"
      >
        <div class="flex items-center gap-2 sm:w-48 shrink-0">
          <span
            v-if="w.is_due"
            class="w-2 h-2 rounded-full bg-yellow-400 shrink-0"
            title="Due for review"
          ></span>
          <span class="font-display text-lg font-semibold text-stone-900 truncate">{{ w.word }}</span>
          <SpeakButton :text="w.word" size="sm" />
        </div>
        <p class="text-sm text-stone-500 line-clamp-2 flex-1 min-w-0">{{ w.definition }}</p>
        <div class="flex items-center gap-2 flex-wrap shrink-0">
          <DifficultyBadge :difficulty="w.difficulty" />
          <CategoryChip v-for="c in w.categories.slice(0, 2)" :key="c">{{ c }}</CategoryChip>
        </div>
        <button
          type="button"
          class="text-stone-300 hover:text-pink-600 transition-colors shrink-0"
          aria-label="Delete word"
          @click.stop="confirmDelete(w)"
        >
          <i class="pi pi-trash"></i>
        </button>
      </div>
    </section>

    <div v-else class="rounded-xl2 bg-white border border-stone-200 px-8 py-16 text-center flex flex-col items-center gap-3">
      <p class="font-display text-xl font-semibold text-stone-900">No words match yet</p>
      <p class="text-stone-500 text-sm max-w-sm">
        Try clearing your filters, or
        <router-link to="/add" class="text-pink-600 font-medium">add a new word</router-link>.
      </p>
    </div>

    <!-- Edit dialog -->
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
          class="rounded-full bg-white border border-stone-200 text-stone-600 hover:bg-stone-100 text-sm font-semibold px-5 py-2.5 transition-colors mr-2"
          @click="editing = null"
        >
          Cancel
        </button>
        <button
          type="button"
          class="rounded-full bg-pink-500 hover:bg-pink-600 text-white text-sm font-semibold px-5 py-2.5 transition-colors disabled:opacity-60"
          :disabled="savingEdit"
          @click="saveEdit"
        >
          Save changes
        </button>
      </template>
    </Dialog>
  </div>
</template>