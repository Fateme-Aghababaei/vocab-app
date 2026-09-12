<template>
  <section v-if="store.recommendations && store.recommendations.length > 0" class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="font-display font-semibold text-lg text-stone-900 flex items-center gap-2">
          <span>Recommended for you</span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-pink-100 text-pink-700 font-sans font-medium">Smart pick</span>
        </h2>
        <p class="text-xs text-stone-500 mt-0.5">
          Words tailored to your interests and study level.
        </p>
      </div>

      <button
        type="button"
        class="text-xs font-semibold text-pink-600 hover:text-pink-700 flex items-center gap-1 transition-colors"
        @click="store.fetchRecommendations"
      >
        <i class="pi pi-refresh text-xs"></i>
        <span>Refresh</span>
      </button>
    </div>

    <!-- Cards Grid -->
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="rec in (store.recommendations as RecommendedWord[])"
        :key="rec.id"
        class="rounded-xl2 bg-white border border-stone-200 p-4 shadow-soft flex flex-col justify-between hover:border-pink-200 transition-all group"
      >
        <div>
          <!-- Header -->
          <div class="flex items-start justify-between gap-2 mb-2">
            <div class="flex items-center gap-2">
              <h3 class="font-display font-bold text-lg text-stone-900 group-hover:text-pink-600 transition-colors">
                {{ rec.word }}
              </h3>
              <SpeakButton :text="rec.word" size="sm" />
            </div>
            <DifficultyBadge :difficulty="rec.difficulty" />
          </div>

          <!-- Definition -->
          <p class="text-xs text-stone-600 line-clamp-2 mb-3 leading-relaxed">
            {{ rec.definition }}
          </p>

          <!-- Categories -->
          <div class="flex flex-wrap gap-1 mb-4">
            <CategoryChip v-for="c in rec.categories.slice(0, 1)" :key="c">
              {{ c }}
            </CategoryChip>
          </div>
        </div>

        <!-- Action Button -->
        <button
          type="button"
          class="w-full rounded-full border border-stone-200 bg-stone-50 hover:bg-pink-50 hover:border-pink-300 text-stone-700 hover:text-pink-600 text-xs font-semibold py-2 transition-all flex items-center justify-center gap-1.5 active:scale-95 disabled:opacity-50"
          :disabled="addingId === rec.id"
          @click="handleAdd(rec)"
        >
          <i v-if="addingId === rec.id" class="pi pi-spin pi-spinner text-xs"></i>
          <i v-else class="pi pi-plus text-xs"></i>
          <span>Add to Deck</span>
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
