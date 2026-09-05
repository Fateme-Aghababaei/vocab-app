<script setup lang="ts">
import { ref } from "vue";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import CategoryChip from "@/components/CategoryChip.vue";

const props = defineProps<{
  modelValue: string[];
  suggestions: string[];
}>();

const emit = defineEmits<{ (e: "update:modelValue", value: string[]): void }>();

const customInput = ref("");

function toggle(category: string) {
  const has = props.modelValue.includes(category);
  const next = has
    ? props.modelValue.filter((c) => c !== category)
    : [...props.modelValue, category];
  emit("update:modelValue", next);
}

function addCustom() {
  const value = customInput.value.trim();
  if (!value || props.modelValue.includes(value)) {
    customInput.value = "";
    return;
  }
  emit("update:modelValue", [...props.modelValue, value]);
  customInput.value = "";
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-wrap gap-2">
      <button
        v-for="cat in suggestions"
        :key="cat"
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-medium border transition-colors"
        :class="
          modelValue.includes(cat)
            ? 'bg-pink-500 border-pink-500 text-white'
            : 'bg-white border-stone-200 text-stone-600 hover:border-pink-300 hover:text-pink-600'
        "
        @click="toggle(cat)"
      >
        {{ cat }}
      </button>
    </div>

    <div class="flex items-center gap-2">
      <InputText
        v-model="customInput"
        placeholder="Add a custom category"
        class="max-w-xs"
        @keyup.enter="addCustom"
      />
      <Button label="Add" text size="small" class="!text-pink-600" @click="addCustom" />
    </div>

    <div v-if="modelValue.length" class="flex flex-wrap gap-2">
      <CategoryChip
        v-for="cat in modelValue.filter((c) => !suggestions.includes(c))"
        :key="cat"
        removable
        @remove="toggle(cat)"
      >
        {{ cat }}
      </CategoryChip>
    </div>
  </div>
</template>
