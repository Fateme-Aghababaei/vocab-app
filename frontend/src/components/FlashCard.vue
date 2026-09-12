<template>
  <div class="w-full">
    <div class="[perspective:1600px]">
      <div
        class="flip-card-inner relative w-full min-h-[22rem] sm:min-h-[24rem]"
        :class="{ 'is-flipped': flipped }"
      >
        <div
          class="flip-card-face absolute inset-0 rounded-xl2 bg-white border border-stone-200 shadow-soft flex flex-col items-center justify-center text-center px-8 py-10 cursor-pointer"
          @click="!flipped && emit('flip')"
        >
          <div class="absolute top-5 left-5 flex gap-2">
            <DifficultyBadge :difficulty="word.difficulty" />
          </div>
          <span class="text-xs font-medium text-stone-400 mb-3">Do you remember this word?</span>

          <div class="flex items-center justify-center gap-3 mb-6">
            <h2 class="font-display text-4xl sm:text-5xl font-semibold text-stone-900">
              {{ word.word }}
            </h2>
            <SpeakButton :text="word.word" size="lg" />
          </div>

          <p v-if="word.pronunciation" class="text-lg text-stone-500 mb-6 break-words" title="US English IPA">
            {{ word.pronunciation }}
          </p>
          <button
            type="button"
            class="rounded-full bg-pink-500 hover:bg-pink-600 text-white text-sm font-semibold px-5 py-2.5 transition-colors"
            @click.stop="emit('flip')"
          >
            Show answer
          </button>
        </div>

        <div
          class="flip-card-face flip-card-back absolute inset-0 rounded-xl2 bg-white border border-stone-200 shadow-soft flex flex-col px-6 sm:px-8 py-7 overflow-y-auto"
        >
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex items-center gap-2.5">
              <h2 class="font-display text-2xl sm:text-3xl font-semibold text-stone-900">
                {{ word.word }}
              </h2>
              <SpeakButton :text="word.word" size="md" />
            </div>
            <DifficultyBadge :difficulty="word.difficulty" />
          </div>

          <p v-if="word.pronunciation" class="text-sm text-stone-500 mb-3 break-words" title="US English IPA">
            {{ word.pronunciation }}
          </p>
          <p class="text-stone-700 leading-relaxed mb-4">
            {{ word.definition }}
          </p>

          <div v-if="word.examples.length" class="mb-4">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-stone-400 mb-1.5">
              Examples
            </h3>
            <ul class="space-y-2">
              <li
                v-for="(ex, i) in word.examples"
                :key="i"
                class="flex items-start gap-2 text-sm text-stone-600 italic leading-relaxed"
              >
                <SpeakButton
                  :text="ex"
                  size="sm"
                  title="Listen to example sentence"
                  class="mt-0.5 shrink-0"
                />
                <span>&ldquo;{{ ex }}&rdquo;</span>
              </li>
            </ul>
          </div>

          <div v-if="word.usage_notes" class="mb-4">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-stone-400 mb-1.5">
              Usage notes
            </h3>
            <p class="text-sm text-stone-600 leading-relaxed">
              {{ word.usage_notes }}
            </p>
          </div>

          <div v-if="word.collocations.length" class="mb-4">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-stone-400 mb-1.5">
              Common phrases
            </h3>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="(c, i) in word.collocations"
                :key="i"
                class="rounded-full bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-1"
              >
                {{ c }}
              </span>
            </div>
          </div>

          <div v-if="word.categories.length" class="flex flex-wrap gap-1.5 mt-auto pt-2">
            <CategoryChip v-for="c in word.categories" :key="c">
              {{ c }}
            </CategoryChip>
          </div>
        </div>
      </div>
    </div>

    <div v-if="flipped" class="mt-5 grid grid-cols-4 gap-2 sm:gap-3">
      <button
        v-for="r in ratings"
        :key="r.quality"
        type="button"
        class="flex flex-col items-center justify-center gap-1 rounded-xl py-3 text-sm font-semibold transition-colors"
        :class="r.classes"
        @click="emit('rate', r.quality)"
      >
        {{ r.label }}
        <span class="text-xs font-normal opacity-80">{{ intervals[r.quality] }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ReviewQuality, Word } from "@/types";
import DifficultyBadge from "@/components/DifficultyBadge.vue";
import CategoryChip from "@/components/CategoryChip.vue";
import SpeakButton from "@/components/SpeakButton.vue";
import { previewIntervals } from "@/utils/srsPreview";

const props = defineProps<{
  word: Word;
  flipped: boolean;
}>();

const emit = defineEmits<{
  (e: "flip"): void;
  (e: "rate", quality: ReviewQuality): void;
}>();

const intervals = computed(() => previewIntervals(props.word));

const ratings: { quality: ReviewQuality; label: string; classes: string }[] = [
  { quality: 0, label: "Again", classes: "bg-stone-100 text-stone-700 hover:bg-stone-200" },
  { quality: 1, label: "Hard", classes: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200" },
  { quality: 2, label: "Good", classes: "bg-pink-100 text-pink-700 hover:bg-pink-200" },
  { quality: 3, label: "Easy", classes: "bg-pink-500 text-white hover:bg-pink-600" },
];
</script>
