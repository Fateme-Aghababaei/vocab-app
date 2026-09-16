<template>
  <section class="rounded-xl2 content-panel border p-5 sm:p-7" aria-labelledby="garden-heading">
    <div class="mb-5 flex flex-wrap items-center justify-between gap-2">
      <h2 id="garden-heading" class="text-lg font-semibold">
        Your word garden
      </h2>
      <span class="rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent-strong">
        {{ stats.total_words }} total words
      </span>
    </div>
    <dl class="grid grid-cols-3 gap-2 sm:gap-3">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="garden-stage flex min-w-0 flex-col items-center rounded-2xl border border-line-soft px-1 py-5 text-center"
      >
        <dt class="flex flex-col items-center gap-3 text-xs font-medium text-copy sm:text-sm">
          <span class="text-3xl sm:text-4xl" aria-hidden="true">{{ stage.icon }}</span>
          {{ stage.label }}
        </dt>
        <dd class="mt-1 text-2xl font-semibold tabular-nums text-heading sm:text-3xl">
          {{ stats[stage.key] }}
        </dd>
      </div>
    </dl>
    <p class="mt-4 text-xs leading-relaxed text-quiet">
      {{ stats.total_words === 0 ? 'Your garden is ready for its first word. Add a word, then review it to help it grow.' : 'Every review helps your words take root. Keep tending your garden, one day at a time.' }}
    </p>
    <router-link v-if="stats.total_words === 0" to="/add" class="mt-2 inline-flex min-h-11 items-center text-sm font-semibold text-accent hover:text-accent-strong">
      Add your first word <i class="pi pi-arrow-right ml-2 text-xs" aria-hidden="true"></i>
    </router-link>
  </section>
</template>

<script setup lang="ts">
import type { UserProfile } from "@/types";

defineProps<{ stats: UserProfile["garden_stats"] }>();
const stages = [
  { key: "sprouts", label: "Sprouts", icon: "🌱" },
  { key: "growing", label: "Growing", icon: "🌿" },
  { key: "mature", label: "Mature", icon: "🌳" },
] as const;
</script>

<style scoped>
.garden-stage {
  background: linear-gradient(180deg, rgb(var(--color-accent-soft)), rgb(var(--color-surface)));
}
</style>
