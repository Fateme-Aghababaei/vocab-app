<template>
  <router-link
    :to="count === 0 ? '/review' : '/profile'"
    class="inline-flex min-h-11 items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold transition-colors sm:text-sm"
    :class="count !== null && count > 0 ? 'border-warning-line bg-warning-soft text-warning-ink hover:bg-warning-muted' : 'border-line bg-surface text-secondary hover:bg-subtle'"
    :aria-label="description"
    :title="description"
  >
    <span v-if="count !== null && count > 0" aria-hidden="true">🔥</span>
    <i v-else :class="auth.streakLoading ? 'pi pi-spinner pi-spin' : 'pi pi-bolt'" aria-hidden="true"></i>
    <span aria-live="polite">{{ label }}</span>
  </router-link>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const count = computed(() => {
  if (auth.streakError) return null;
  const value = auth.user?.streak_count;
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
});
const label = computed(() => {
  if (count.value === 0) return "Start your streak";
  if (count.value !== null) return `${count.value} ${count.value === 1 ? "day" : "days"}`;
  return auth.streakLoading ? "Loading streak…" : "Streak unavailable";
});
const description = computed(() => {
  if (count.value === 0) return "No active streak yet. Review a word to start your streak.";
  if (count.value !== null) return `${count.value}-day streak. View your profile for details.`;
  return auth.streakLoading ? "Loading your streak" : "Your streak could not be loaded. Open your profile to try again.";
});

watch(() => auth.user?.id, (id) => {
  if (id !== undefined && count.value === null) void auth.refreshStreak();
}, { immediate: true });
</script>
