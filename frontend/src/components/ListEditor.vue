<script setup lang="ts">
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Button from "primevue/button";

const props = withDefaults(
  defineProps<{
    modelValue: string[];
    placeholder?: string;
    multiline?: boolean;
    addLabel?: string;
  }>(),
  { placeholder: "", multiline: false, addLabel: "Add" }
);

const emit = defineEmits<{ (e: "update:modelValue", value: string[]): void }>();

function update(i: number, value: string) {
  const next = [...props.modelValue];
  next[i] = value;
  emit("update:modelValue", next);
}

function add() {
  emit("update:modelValue", [...props.modelValue, ""]);
}

function remove(i: number) {
  const next = props.modelValue.filter((_, idx) => idx !== i);
  emit("update:modelValue", next);
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div v-for="(item, i) in modelValue" :key="i" class="flex items-start gap-2">
      <Textarea
        v-if="multiline"
        :model-value="item"
        dir="auto"
        rows="2"
        auto-resize
        class="w-full"
        :placeholder="placeholder"
        @update:model-value="(v) => update(i, String(v ?? ''))"
      />
      <InputText
        v-else
        :model-value="item"
        dir="auto"
        class="w-full"
        :placeholder="placeholder"
        @update:model-value="(v) => update(i, String(v ?? ''))"
      />
      <Button
        icon="pi pi-trash"
        text
        rounded
        severity="secondary"
        aria-label="Remove"
        @click="remove(i)"
      />
    </div>
    <Button
      :label="addLabel"
      icon="pi pi-plus"
      text
      size="small"
      class="self-start !text-pink-600"
      @click="add"
    />
  </div>
</template>
