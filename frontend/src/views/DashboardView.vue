<template>
  <div class="flex flex-col gap-6">
    <StatePanel v-if="loading" kind="loading" title="Getting your universe ready…" />
    <StatePanel
      v-else-if="store.dueError || store.statsError"
      kind="error"
      title="Your progress is taking a little longer"
      :description="store.dueError || store.statsError"
      action-label="Try again"
      @action="loadDashboard"
    />
    <section
      v-else
      class="review-summary rounded-xl2 content-panel glass-primary border text-on-primary px-6 sm:px-8 py-7 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5"
    >
      <div>
        <p class="text-on-primary-muted text-sm font-medium mb-1">
          YOUR DAILY PRACTICE
        </p>
        <p v-if="store.stats?.total_words === 0" class="mt-4 max-w-sm text-3xl font-semibold leading-tight">
          Your universe starts with one word.
        </p>
        <p v-else class="review-count">
          <span class="review-count-value">{{ store.dueCount }}</span>
          <span class="review-count-label">{{ store.dueCount === 1 ? "word to revisit" : "words to revisit" }}</span>
        </p>
        <p class="text-on-primary-muted text-sm mt-2 max-w-xs">
          {{
            store.stats?.total_words === 0
              ? "Choose a word that sparks your curiosity. Your first discovery is a great place to begin."
              : store.dueCount > 0
                ? "A few minutes now keeps these words in memory."
                : "Your stars can rest for now. Come back when words are due, or discover something new."
          }}
        </p>
      </div>
      <button
        type="button"
        class="self-start sm:self-auto rounded-full glass-control text-accent font-semibold px-6 py-3 hover:bg-accent-soft transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        @click="router.push(store.dueCount > 0 ? '/review' : '/add')"
      >
        {{ store.dueCount > 0 ? 'Start reviewing' : store.stats?.total_words === 0 ? 'Add your first word' : 'Discover a new word' }}
      </button>
    </section>

    <section v-if="!store.statsError" class="stats-grid grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="rounded-xl2 content-panel border px-5 py-4">
        <p class="text-xs font-medium text-faint mb-1">
          Total words
        </p>
        <p class="text-2xl font-semibold text-heading">
          {{ store.stats?.total_words ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 content-panel border px-5 py-4">
        <p class="text-xs font-medium text-faint mb-1">
          New words
        </p>
        <p class="text-2xl font-semibold text-heading">
          {{ store.stats?.new_words ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 content-panel glass-warning border px-5 py-4">
        <p class="text-xs font-medium text-warning-copy mb-1">
          Reviewed today
        </p>
        <p class="text-2xl font-semibold text-warning-ink">
          {{ store.stats?.reviewed_today ?? "&ndash;" }}
        </p>
      </div>
      <div class="rounded-xl2 content-panel border px-5 py-4">
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
      <section class="lg:col-span-2 rounded-xl2 content-panel border px-6 py-5">
        <h2 class="text-sm font-semibold text-copy mb-4">
          Words by difficulty
        </h2>
        <StatePanel
          v-if="store.statsLoading"
          compact
          kind="loading"
          title="Gathering your progress…"
        />
        <StatePanel
          v-else-if="store.statsError"
          compact
          kind="error"
          title="Progress couldn’t load"
          action-label="Try again"
          @action="store.fetchStats()"
        />
        <StatePanel
          v-else-if="store.stats?.total_words === 0"
          compact
          title="Room for every kind of word"
          description="Your discoveries will appear here, from everyday words to new challenges."
        />
        <div v-else class="flex flex-col gap-3">
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

      <section class="lg:col-span-3 rounded-xl2 content-panel border px-6 py-5">
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
        <StatePanel
          v-if="store.loading"
          compact
          kind="loading"
          title="Gathering your words…"
        />
        <StatePanel
          v-else-if="store.error"
          compact
          kind="error"
          title="Your recent words couldn’t load"
          action-label="Try again"
          @action="store.fetchWords()"
        />
        <ul v-else-if="recentWords.length" class="divide-y divide-line-soft">
          <li v-for="w in recentWords" :key="w.id" class="py-2.5 flex items-center justify-between gap-3">
            <span class="font-medium text-body">{{ w.word }}</span>
            <span class="text-xs text-faint truncate max-w-[14rem]">{{ w.definition }}</span>
          </li>
        </ul>
        <StatePanel
          v-else
          compact
          title="A little curiosity goes a long way"
          description="The words you save will appear here, ready for your next adventure."
          action-label="Add your first word"
          to="/add"
        />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import StatePanel from "@/components/StatePanel.vue";
import { useRouter } from "vue-router";
import { useWordsStore } from "@/stores/words";
import { useNotifications } from "../composables/useNotifications";
import RecommendedSection from "@/components/RecommendedSection.vue";

const store = useWordsStore();
const router = useRouter();
const { checkAndNotifyDueWords } = useNotifications();

const loading = ref(true);
async function loadDashboard() {
  loading.value = true;
  await Promise.all([store.fetchStats(), store.fetchDueWords(), store.fetchWords()]);
  loading.value = false;
  if (!store.dueError && store.dueWords.length > 0) {
    void checkAndNotifyDueWords(store.dueWords).catch(() => {});
  }
}
onMounted(loadDashboard);

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
