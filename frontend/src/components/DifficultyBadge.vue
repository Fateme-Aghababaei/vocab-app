<script setup lang="ts">
import { computed } from "vue";
import type { Difficulty } from "@/types";

const props = defineProps<{ difficulty: Difficulty }>();

const config = computed(() => {
  switch (props.difficulty) {
    case "beginner":
      return { label: "Beginner", dot: "bg-stone-400", text: "text-stone-600" };
    case "advanced":
      return { label: "Advanced", dot: "bg-pink-500", text: "text-pink-700" };
    default:
      return { label: "Intermediate", dot: "bg-yellow-500", text: "text-yellow-800" };
  }
});
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full bg-stone-100 px-2.5 py-1 text-xs font-medium"
    :class="config.text"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="config.dot"></span>
    {{ config.label }}
  </span>
</template>
