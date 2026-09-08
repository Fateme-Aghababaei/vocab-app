<script setup lang="ts">
import { onMounted, reactive, watch } from "vue";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Select from "primevue/select";
import ListEditor from "@/components/ListEditor.vue";
import CategoryPicker from "@/components/CategoryPicker.vue";
import { useWordsStore } from "@/stores/words";
import type { Difficulty, NewWordPayload } from "@/types";

const props = defineProps<{ modelValue: NewWordPayload }>();
const emit = defineEmits<{ (e: "update:modelValue", value: NewWordPayload): void }>();

const store = useWordsStore();

const difficultyOptions: { label: string; value: Difficulty }[] = [
  { label: "Beginner", value: "beginner" },
  { label: "Intermediate", value: "intermediate" },
  { label: "Advanced", value: "advanced" },
];

const form = reactive<NewWordPayload>({ ...props.modelValue });

watch(
  form,
  (v) => emit("update:modelValue", { ...v }),
  { deep: true }
);

watch(
  () => props.modelValue,
  (v) => Object.assign(form, v)
);

onMounted(() => {
  if (!store.categories.length) store.fetchCategories();
});
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5" for="word">Word</label>
      <InputText id="word" v-model="form.word" dir="auto" class="w-full text-lg" placeholder="e.g. resilient" />
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5" for="pronunciation">
        Pronunciation (IPA)
      </label>
      <InputText
        id="pronunciation"
        v-model="form.pronunciation"
        dir="ltr"
        class="w-full"
        placeholder="e.g. /rɪˈzɪliənt/"
        :maxlength="200"
        :spellcheck="false"
        aria-describedby="pronunciation-help"
      />
      <p id="pronunciation-help" class="text-xs text-stone-400 mt-1.5">
        Optional. Phonetic symbols show how the word sounds. You can edit the generated pronunciation.
      </p>
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5" for="definition"
        >Definition</label
      >
      <Textarea
        id="definition"
        v-model="form.definition"
        rows="3"
        auto-resize
        class="w-full"
        placeholder="A clear, learner-friendly definition"
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5">Example sentences</label>
      <ListEditor
        v-model="form.examples"
        multiline
        placeholder="A natural sentence using the word"
        add-label="Add example"
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5" for="usage_notes"
        >Usage notes</label
      >
      <Textarea
        id="usage_notes"
        v-model="form.usage_notes"
        rows="3"
        auto-resize
        class="w-full"
        placeholder="Formality, common mistakes, grammar patterns..."
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5">Common collocations</label>
      <ListEditor v-model="form.collocations" placeholder="e.g. deeply resilient" add-label="Add phrase" />
    </div>

    <div class="grid sm:grid-cols-2 gap-6">
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1.5" for="difficulty"
          >Difficulty</label
        >
        <Select
          id="difficulty"
          v-model="form.difficulty"
          :options="difficultyOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-stone-700 mb-1.5">Categories</label>
      <CategoryPicker v-model="form.categories" :suggestions="store.categories" />
    </div>
  </div>
</template>
