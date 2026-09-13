<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full glass-control px-2.5 py-1 text-xs font-medium"
    :class="config.text"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="config.dot"></span>
    {{ config.label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Difficulty } from "@/types";

const props = defineProps<{ difficulty: Difficulty }>();

const config = computed(() => {
  switch (props.difficulty) {
    case "beginner":
      return { label: "Beginner", dot: "bg-dot-neutral", text: "text-secondary" };
    case "advanced":
      return { label: "Advanced", dot: "bg-primary", text: "text-accent-strong" };
    default:
      return { label: "Intermediate", dot: "bg-warning-bright", text: "text-warning-ink" };
  }
});
</script>
