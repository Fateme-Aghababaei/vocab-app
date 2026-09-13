<template>
  <span
    class="inline-flex items-center gap-1 rounded-full border border-line bg-surface px-2.5 py-1 text-xs font-medium text-secondary"
  >
    <slot></slot>
    <button
      v-if="removable"
      type="button"
      class="ml-0.5 text-faint hover:text-accent transition-colors"
      aria-label="Remove"
      @click="$emit('remove')"
    >
      <i class="pi pi-times" style="font-size: 0.6rem"></i>
    </button>
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    removable?: boolean;
  }>(),
  { removable: false },
);

defineEmits<{ (e: "remove"): void }>();
</script>
