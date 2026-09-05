<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useWordsStore } from "@/stores/words";

const store = useWordsStore();
const router = useRouter();

onMounted(async () => {
  await Promise.all([store.fetchStats(), store.fetchDueWords(), store.fetchWords()]);
});

const difficultyBreakdown = computed(() => {
  const s = store.stats;
  if (!s) return [];
  const total = Math.max(1, s.total_words);
  return [
    { label: "Beginner", value: s.by_difficulty.beginner, color: "bg-stone-300", pct: (s.by_difficulty.beginner / total) * 100 },
    { label: "Intermediate", value: s.by_difficulty.intermediate, color: "bg-yellow-400", pct: (s.by_difficulty.intermediate / total) * 100 },
    { label: "Advanced", value: s.by_difficulty.advanced, color: "bg-pink-500", pct: (s.by_difficulty.advanced / total) * 100 },
  ];
});

const recentWords = computed(() => store.words.slice(0, 5));
</script>

<template>
  <div class="flex flex-col gap-6">
    <header>
      <h1 class="text-2xl font-semibold">Good to see you</h1>
      <p class="text-stone-500 mt-1">Here&rsquo;s what your vocabulary practice looks like today.</p>
    </header>

    <!-- Hero: due today -->
    <section
      class="rounded-xl2 bg-pink-500 text-white px-6 sm:px-8 py-7 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5"
    >
      <div>
        <p class="text-pink-100 text-sm font-medium mb-1">Due for review</p>
        <p class="font-display text-5xl font-semibold">{{ store.dueCount }}</p>
        <p class="text-pink-100 text-sm mt-2 max-w-xs">
          {{
            store.dueCount > 0
              ? "A few minutes now keeps these words in memory."
              : "You're all caught up. Add a new word to keep building your list."
          }}
        </p>
      </div>
      <button
        type="button"
        class="self-start sm:self-auto rounded-full bg-white text-pink-600 font-semibold px-6 py-3 hover:bg-pink-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        :disabled="store.dueCount === 0"
        @click="router.push('/review')"
      >
        Start reviewing
      </button>
    </section>

    <!-- Stat tiles -->
    <section class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="rounded-xl2 bg-white border border-stone-200 px-5 py-4">
        <p class="text-xs font-medium text-stone-400 mb-1">Total words</p>
        <p class="text-2xl font-semibold text-stone-900">{{ store.stats?.total_words ?? "&ndash;" }}</p>
      </div>
      <div class="rounded-xl2 bg-white border border-stone-200 px-5 py-4">
        <p class="text-xs font-medium text-stone-400 mb-1">New words</p>
        <p class="text-2xl font-semibold text-stone-900">{{ store.stats?.new_words ?? "&ndash;" }}</p>
      </div>
      <div class="rounded-xl2 bg-yellow-50 border border-yellow-200 px-5 py-4">
        <p class="text-xs font-medium text-yellow-700 mb-1">Reviewed today</p>
        <p class="text-2xl font-semibold text-yellow-800">{{ store.stats?.reviewed_today ?? "&ndash;" }}</p>
      </div>
      <div class="rounded-xl2 bg-white border border-stone-200 px-5 py-4">
        <p class="text-xs font-medium text-stone-400 mb-1">Learned</p>
        <p class="text-2xl font-semibold text-stone-900">{{ store.stats?.learned ?? "&ndash;" }}</p>
      </div>
    </section>

    <div class="grid lg:grid-cols-5 gap-6">
      <!-- Difficulty breakdown -->
      <section class="lg:col-span-2 rounded-xl2 bg-white border border-stone-200 px-6 py-5">
        <h2 class="text-sm font-semibold text-stone-700 mb-4">Words by difficulty</h2>
        <div class="flex flex-col gap-3">
          <div v-for="d in difficultyBreakdown" :key="d.label">
            <div class="flex justify-between text-xs text-stone-500 mb-1">
              <span>{{ d.label }}</span>
              <span>{{ d.value }}</span>
            </div>
            <div class="h-2 rounded-full bg-stone-100 overflow-hidden">
              <div class="h-full rounded-full" :class="d.color" :style="{ width: d.pct + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recently added -->
      <section class="lg:col-span-3 rounded-xl2 bg-white border border-stone-200 px-6 py-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-stone-700">Recently added</h2>
          <router-link to="/library" class="text-xs font-medium text-pink-600 hover:text-pink-700"
            >View all</router-link
          >
        </div>
        <ul v-if="recentWords.length" class="divide-y divide-stone-100">
          <li v-for="w in recentWords" :key="w.id" class="py-2.5 flex items-center justify-between gap-3">
            <span class="font-medium text-stone-800">{{ w.word }}</span>
            <span class="text-xs text-stone-400 truncate max-w-[14rem]">{{ w.definition }}</span>
          </li>
        </ul>
        <p v-else class="text-sm text-stone-400 py-4">
          No words yet.
          <router-link to="/add" class="text-pink-600 font-medium">Add your first word</router-link>.
        </p>
      </section>
    </div>
  </div>
</template>
