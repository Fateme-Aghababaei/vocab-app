<template>
  <div class="flex flex-col gap-6">
    <div class="mx-auto flex w-full max-w-xl flex-col gap-5">
      <div class="flex items-center justify-between gap-3">
        <p class="text-sm text-quiet">
          {{ sessionTotal > 0 ? `${reviewedCount} reviewed${masteredCount ? ` · ${masteredCount} mastered` : ''} · ${sessionTotal} total` : "" }}
        </p>
        <router-link to="/add" class="text-sm font-medium text-accent hover:text-accent-strong">
          + Add word
        </router-link>
      </div>
      <div v-if="sessionTotal > 0" class="h-1.5 rounded-full bg-subtle overflow-hidden">
        <div
          class="h-full bg-primary rounded-full transition-all duration-300"
          :style="{ width: progressPct + '%' }"
        ></div>
      </div>

      <StatePanel v-if="loading" kind="loading" title="Gathering your next discoveries…" />
      <StatePanel
        v-else-if="store.dueError || (!currentWord && store.statsError)"
        kind="error"
        title="Your practice is waiting for you"
        :description="store.dueError || store.statsError"
        action-label="Try again"
        @action="loadReview"
      />

      <FlashCard
        v-else-if="currentWord"
        :key="currentWord.id"
        :word="currentWord"
        :flipped="flipped"
        :disabled="rating || store.masteringIds.includes(currentWord.id)"
        @flip="handleFlip"
        @rate="handleRate"
      />

      <StatePanel
        v-else
        :title="sessionTotal > 0 ? 'A little practice, a brighter universe.' : store.stats?.total_words === 0 ? 'Your first review starts with a word.' : 'Your stars can rest for now.'"
        :description="sessionTotal > 0 ? 'You’ve finished every word in this session. Enjoy the progress you’ve made, and come back for your next discovery.' : store.stats?.total_words === 0 ? 'Save a word you’d love to remember. We’ll have it ready for your first practice.' : 'Nothing is due right now. Your words will be here when it’s time to revisit them.'"
        :action-label="store.stats?.total_words === 0 ? 'Add your first word' : 'Discover a new word'"
        to="/add"
      >
        <router-link
          to="/library"
          class="rounded-full glass-control hover:bg-muted text-copy text-sm font-semibold px-5 py-2.5 transition-colors"
        >
          Browse library
        </router-link>
      </StatePanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useToast } from "primevue/usetoast";
import { useWordsStore } from "@/stores/words";
import { useAuthStore } from "@/stores/auth";
import FlashCard from "@/components/FlashCard.vue";
import StatePanel from "@/components/StatePanel.vue";
import type { ReviewQuality } from "@/types";

const store = useWordsStore();
const auth = useAuthStore();
const toast = useToast();

const loading = ref(true);
const flipped = ref(false);
const reviewedCount = ref(0);
const sessionWordIds = ref<number[]>([]);
const masteredCount = computed(() => sessionWordIds.value.filter((id) => store.masteredIds.includes(id)).length);
const rating = ref(false);
const sessionTotal = ref(0);

async function loadReview() {
  loading.value = true;
  await Promise.all([store.fetchDueWords(), store.fetchStats()]);
  sessionTotal.value = store.dueWords.length;
  sessionWordIds.value = store.dueWords.map((word) => word.id);
  loading.value = false;
}
onMounted(loadReview);

const currentWord = computed(() => store.dueWords[0] ?? null);
watch(() => currentWord.value?.id, () => { flipped.value = false; });
const progressPct = computed(() =>
  sessionTotal.value === 0 ? 0 : Math.round(((reviewedCount.value + masteredCount.value) / sessionTotal.value) * 100),
);

function handleFlip() {
  flipped.value = true;
}

async function handleRate(quality: ReviewQuality) {
  if (!currentWord.value || rating.value || store.masteringIds.includes(currentWord.value.id)) return;
  rating.value = true;
  const word = currentWord.value;
  try {
    await store.reviewWord(word.id, quality);
    reviewedCount.value += 1;
    flipped.value = false;
    void auth.refreshStreak();
  } catch {
    toast.add({
      severity: "error",
      summary: "Couldn't save review",
      detail: "Please try again.",
      life: 3500,
    });
  } finally {
    rating.value = false;
  }
}

</script>
