<template>
  <section v-if="store.recommendations && store.recommendations.length > 0" class="min-w-0 flex flex-col gap-3">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 class="font-display font-semibold text-lg text-heading flex flex-wrap items-center gap-2">
          <span>Recommended for you</span>
          <span class="shrink-0 whitespace-nowrap text-xs px-2 py-0.5 rounded-full bg-accent-muted text-accent-strong font-sans font-medium">Smart pick</span>
        </h2>
        <p class="text-xs text-quiet mt-0.5">
          Words tailored to your interests and study level.
        </p>
      </div>

      <button
        type="button"
        class="shrink-0 py-2 text-xs font-semibold text-accent hover:text-accent-strong flex items-center gap-1 transition-colors"
        @click="store.fetchRecommendations"
      >
        <i class="pi pi-refresh text-xs"></i>
        <span>Refresh</span>
      </button>
    </div>

    <div class="grid grid-cols-[repeat(auto-fit,minmax(min(100%,14rem),1fr))] gap-4">
      <div
        v-for="rec in (store.recommendations as RecommendedWord[])"
        :key="rec.id"
        class="min-w-0 rounded-xl2 bg-surface border border-line p-4 shadow-soft flex flex-col justify-between hover:border-accent-line hover:bg-accent-soft/40 hover:shadow-md hover:shadow-accent-muted/50 transition-all duration-200 motion-reduce:transition-none group"
      >
        <div>
          <div class="flex flex-col items-start gap-2 mb-2">
            <div class="flex w-full min-w-0 items-start gap-2">
              <h3 class="min-w-0 [overflow-wrap:anywhere] font-display font-bold text-lg text-heading group-hover:text-accent transition-colors">
                {{ rec.word }}
              </h3>
              <SpeakButton :text="rec.word" size="sm" class="shrink-0" />
            </div>
            <DifficultyBadge :difficulty="rec.difficulty" class="shrink-0 whitespace-nowrap" />
          </div>

          <p class="[overflow-wrap:anywhere] text-xs text-secondary line-clamp-2 mb-3 leading-relaxed">
            {{ rec.definition }}
          </p>

          <div class="flex flex-wrap gap-1 mb-4">
            <CategoryChip v-for="c in rec.categories.slice(0, 1)" :key="c" class="min-w-0 max-w-full [overflow-wrap:anywhere]">
              {{ c }}
            </CategoryChip>
          </div>
        </div>

        <button
          type="button"
          class="w-full rounded-full border border-line bg-canvas hover:bg-accent-soft hover:border-accent-line-strong text-copy hover:text-accent text-xs font-semibold py-2 transition-all flex items-center justify-center gap-1.5 active:scale-95 disabled:opacity-50"
          :disabled="addingId === rec.id"
          @click="handleAdd(rec)"
        >
          <i v-if="addingId === rec.id" class="pi pi-spin pi-spinner text-xs"></i>
          <i v-else class="pi pi-plus text-xs"></i>
          <span>Add to Library</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useWordsStore } from "@/stores/words";
import { useToast } from "primevue/usetoast";
import DifficultyBadge from "@/components/DifficultyBadge.vue";
import CategoryChip from "@/components/CategoryChip.vue";
import SpeakButton from "@/components/SpeakButton.vue";
import type { Difficulty } from "@/types";

interface RecommendedWord {
  id: number;
  word: string;
  definition: string;
  difficulty: Difficulty;
  categories: string[];
}

const store = useWordsStore();
const toast = useToast();
const addingId = ref<number | null>(null);

onMounted(() => {
  store.fetchRecommendations();
});

const handleAdd = async (rec: RecommendedWord) => {
  addingId.value = rec.id;
  try {
    await store.claimRecommendation(rec.id);
    toast.add({
      severity: "success",
      summary: "Added to your cards!",
      detail: `"${rec.word}" is ready to practice.`,
      life: 2500,
    });
  } catch {
    toast.add({
      severity: "error",
      summary: "Failed to add",
      detail: "Could not add this word.",
      life: 3000,
    });
  } finally {
    addingId.value = null;
  }
};
</script>
