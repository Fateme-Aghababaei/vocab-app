<template>
  <div class="flex flex-col gap-6">
    <section
      class="rounded-xl2 bg-primary text-on-primary px-6 sm:px-8 py-7 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5"
    >
      <div>
        <p class="text-on-primary-muted text-sm font-medium mb-1">
          Due for review
        </p>
        <p class="font-display text-5xl font-semibold">
          {{ store.dueCount }}
        </p>
        <p class="text-on-primary-muted text-sm mt-2 max-w-xs">
          {{
            store.dueCount > 0
              ? "A few minutes now keeps these words in memory."
              : "You're all caught up. Add a new word to keep building your list."
          }}
        </p>
      </div>
      <button
        type="button"
        class="self-start sm:self-auto rounded-full bg-surface text-accent font-semibold px-6 py-3 hover:bg-accent-soft transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        :disabled="store.dueCount === 0"
        @click="router.push('/review')"
      >
        Start reviewing
      </button>
    </section>

    <section class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="rounded-xl2 bg-surface border border-line px-5 py-4">
        <p class="text-xs font-medium text-faint mb-1">
          Total words
        </p>
        <p class="text-2xl font-semibold text-heading">
          {{ store.stats?.total_words ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 bg-surface border border-line px-5 py-4">
        <p class="text-xs font-medium text-faint mb-1">
          New words
        </p>
        <p class="text-2xl font-semibold text-heading">
          {{ store.stats?.new_words ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 bg-warning-soft border border-warning-line px-5 py-4">
        <p class="text-xs font-medium text-warning-copy mb-1">
          Reviewed today
        </p>
        <p class="text-2xl font-semibold text-warning-ink">
          {{ store.stats?.reviewed_today ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 bg-surface border border-line px-5 py-4">
        <p class="text-xs font-medium text-faint mb-1">
          Learned
        </p>
        <p class="text-2xl font-semibold text-heading">
          {{ store.stats?.learned ?? "&ndash;" }}
        </p>
      </div>
    </section>

    <RecommendedSection />

    <div class="grid lg:grid-cols-5 gap-6">
      <section class="lg:col-span-2 rounded-xl2 bg-surface border border-line px-6 py-5">
        <h2 class="text-sm font-semibold text-copy mb-4">
          Words by difficulty
        </h2>
        <div class="flex flex-col gap-3">
          <div v-for="d in difficultyBreakdown" :key="d.label">
            <div class="flex justify-between text-xs text-quiet mb-1">
              <span>{{ d.label }}</span>
              <span>{{ d.value }}</span>
            </div>
            <div class="h-2 rounded-full bg-subtle overflow-hidden">
              <div class="h-full rounded-full" :class="d.color" :style="{ width: d.pct + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="lg:col-span-3 rounded-xl2 bg-surface border border-line px-6 py-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-copy">
            Recently added
          </h2>
          <router-link
            to="/library"
            class="text-xs font-medium text-accent hover:text-accent-strong"
          >
            View all
          </router-link>
        </div>
        <ul v-if="recentWords.length" class="divide-y divide-line-soft">
          <li v-for="w in recentWords" :key="w.id" class="py-2.5 flex items-center justify-between gap-3">
            <span class="font-medium text-body">{{ w.word }}</span>
            <span class="text-xs text-faint truncate max-w-[14rem]">{{ w.definition }}</span>
          </li>
        </ul>
        <p v-else class="text-sm text-faint py-4">
          No words yet.
          <router-link to="/add" class="text-accent font-medium">
            Add your first word
          </router-link>.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useWordsStore } from "@/stores/words";
import { useNotifications } from "../composables/useNotifications";
import RecommendedSection from "@/components/RecommendedSection.vue";

const store = useWordsStore();
const router = useRouter();
const { checkAndNotifyDueWords } = useNotifications();

onMounted(async () => {
  await Promise.all([store.fetchStats(), store.fetchDueWords(), store.fetchWords()]);
  if (store.dueWords && store.dueWords.length > 0) {
    checkAndNotifyDueWords(store.dueWords);
  }
});

const difficultyBreakdown = computed(() => {
  const s = store.stats;
  if (!s) return [];
  const total = Math.max(1, s.total_words);
  return [
    { label: "Beginner", value: s.by_difficulty.beginner, color: "bg-chart-neutral", pct: (s.by_difficulty.beginner / total) * 100 },
    { label: "Intermediate", value: s.by_difficulty.intermediate, color: "bg-warning", pct: (s.by_difficulty.intermediate / total) * 100 },
    { label: "Advanced", value: s.by_difficulty.advanced, color: "bg-primary", pct: (s.by_difficulty.advanced / total) * 100 },
  ];
});

const recentWords = computed(() => store.words.slice(0, 5));
</script>
