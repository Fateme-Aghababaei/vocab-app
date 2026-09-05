<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "primevue/usetoast";
import { useWordsStore } from "@/stores/words";
import FlashCard from "@/components/FlashCard.vue";
import type { ReviewQuality } from "@/types";

const store = useWordsStore();
const toast = useToast();

const loading = ref(true);
const flipped = ref(false);
const reviewedCount = ref(0);
const sessionTotal = ref(0);

onMounted(async () => {
  await store.fetchDueWords();
  sessionTotal.value = store.dueWords.length;
  loading.value = false;
});

const currentWord = computed(() => store.dueWords[0] ?? null);
const progressPct = computed(() =>
  sessionTotal.value === 0 ? 0 : Math.round((reviewedCount.value / sessionTotal.value) * 100)
);

function handleFlip() {
  flipped.value = true;
}

async function handleRate(quality: ReviewQuality) {
  if (!currentWord.value) return;
  const word = currentWord.value;
  try {
    await store.reviewWord(word.id, quality);
    reviewedCount.value += 1;
    flipped.value = false;
  } catch {
    toast.add({
      severity: "error",
      summary: "Couldn't save review",
      detail: "Please try again.",
      life: 3500,
    });
  }
}
</script>

<template>
  <div class="max-w-xl mx-auto flex flex-col gap-5">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">Review</h1>
        <p class="text-stone-500 text-sm mt-0.5">
          {{ sessionTotal > 0 ? `${reviewedCount} of ${sessionTotal} reviewed` : "" }}
        </p>
      </div>
      <router-link to="/add" class="text-sm font-medium text-pink-600 hover:text-pink-700"
        >+ Add word</router-link
      >
    </header>

    <div v-if="sessionTotal > 0" class="h-1.5 rounded-full bg-stone-100 overflow-hidden">
      <div
        class="h-full bg-pink-500 rounded-full transition-all duration-300"
        :style="{ width: progressPct + '%' }"
      ></div>
    </div>

    <div v-if="loading" class="py-24 text-center text-stone-400">Loading your review queue&hellip;</div>

    <FlashCard
      v-else-if="currentWord"
      :key="currentWord.id"
      :word="currentWord"
      :flipped="flipped"
      @flip="handleFlip"
      @rate="handleRate"
    />

    <div v-else class="rounded-xl2 bg-white border border-stone-200 px-8 py-16 text-center flex flex-col items-center gap-3">
      <div class="w-14 h-14 rounded-full bg-yellow-100 flex items-center justify-center text-yellow-600 mb-1">
        <i class="pi pi-check text-2xl"></i>
      </div>
      <h2 class="font-display text-xl font-semibold text-stone-900">
        {{ sessionTotal > 0 ? "Nice work — you're all caught up" : "Nothing due right now" }}
      </h2>
      <p class="text-stone-500 text-sm max-w-sm">
        {{
          sessionTotal > 0
            ? "You've reviewed every word that was due today. Come back tomorrow, or add more words to your list."
            : "New and overdue words will show up here when it's time to review them."
        }}
      </p>
      <div class="flex gap-3 mt-2">
        <router-link
          to="/add"
          class="rounded-full bg-pink-500 hover:bg-pink-600 text-white text-sm font-semibold px-5 py-2.5 transition-colors"
          >Add a word</router-link
        >
        <router-link
          to="/library"
          class="rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 text-sm font-semibold px-5 py-2.5 transition-colors"
          >Browse library</router-link
        >
      </div>
    </div>
  </div>
</template>
