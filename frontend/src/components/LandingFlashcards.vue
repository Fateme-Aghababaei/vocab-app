<template>
  <div
    class="min-w-0 py-8"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
    @focusin="focused = true"
    @focusout="focused = false"
  >
    <div class="card-stage relative" aria-label="Example vocabulary flashcards" aria-roledescription="carousel">
      <div class="card-stack relative grid">
        <article
          v-for="(word, index) in words"
          :key="word.word"
          class="stack-card rounded-3xl border border-line bg-surface p-7 shadow-soft sm:p-10"
          :class="{ 'is-outgoing': outgoing === index }"
          :style="{ '--depth': depth(index) }"
          :data-depth="depth(index)"
          :aria-hidden="index !== current"
        >
          <div class="flex items-center justify-between text-xs text-quiet">
            <span class="uppercase tracking-widest">A word to keep</span><i class="pi pi-bookmark text-accent" aria-hidden="true"></i>
          </div>
          <h2 class="mt-10 break-words text-4xl">
            {{ word.word }}
          </h2>
          <p class="mt-2 text-sm italic text-quiet">
            {{ word.type }}
          </p>
          <p class="mt-6 text-lg leading-relaxed text-copy">
            {{ word.definition }}
          </p>
          <p class="mt-5 border-l-2 border-accent-line pl-4 text-sm italic leading-relaxed text-quiet">
            “{{ word.example }}”
          </p>
          <div class="mt-auto flex flex-wrap items-center justify-between gap-2 border-t border-line pt-5 text-xs text-secondary">
            <span>Discover. Save. Remember.</span><span class="rounded-full bg-accent-soft px-3 py-1 text-accent-strong">One word at a time</span>
          </div>
        </article>
      </div>
    </div>
    <div class="relative z-10 mt-12 flex items-center justify-between gap-3 text-xs text-quiet">
      <span>{{ current + 1 }} / {{ words.length }} · A little inspiration</span>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="header-action"
          :aria-label="paused ? 'Play flashcards' : 'Pause flashcards'"
          :aria-pressed="paused"
          @click="paused = !paused"
        >
          <i :class="paused ? 'pi pi-play' : 'pi pi-pause'" aria-hidden="true"></i>
        </button>
        <button
          type="button"
          class="header-action"
          aria-label="Next flashcard"
          :disabled="outgoing !== null"
          @click="advance"
        >
          <i class="pi pi-arrow-right" aria-hidden="true"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

const words = [
  { word: "serendipity", type: "noun", definition: "The chance discovery of something beautiful or valuable when you weren’t looking for it.", example: "Finding this little bookshop was pure serendipity." },
  { word: "resilient", type: "adjective", definition: "Able to recover and keep going after something difficult happens.", example: "Like a tree after a storm, she remained resilient." },
  { word: "sonder", type: "noun", definition: "The realization that every passerby has a life as vivid and complex as your own.", example: "Watching the busy station, he felt a moment of sonder." },
  { word: "flourish", type: "verb", definition: "To grow, develop, or succeed in a healthy and beautiful way.", example: "With a little daily practice, her confidence began to flourish." },
];
const current = ref(0);
const outgoing = ref<number | null>(null);
const depth = (index: number) => (index - current.value + words.length) % words.length;
const paused = ref(false);
const hovered = ref(false);
const focused = ref(false);
let timer: ReturnType<typeof setInterval> | undefined;
let animationTimer: ReturnType<typeof setTimeout> | undefined;
const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
paused.value = motion.matches;
function updateMotion() { paused.value = motion.matches; }
function advance() {
  if (outgoing.value !== null) return;
  const previous = current.value;
  current.value = (current.value + 1) % words.length;
  if (!motion.matches) {
    outgoing.value = previous;
    animationTimer = setTimeout(() => { outgoing.value = null; }, 1100);
  }
}
onMounted(() => {
  motion.addEventListener("change", updateMotion);
  timer = setInterval(() => {
    if (!paused.value && !hovered.value && !focused.value && !document.hidden) advance();
  }, 3000);
});
onUnmounted(() => {
  clearInterval(timer);
  clearTimeout(animationTimer);
  motion.removeEventListener("change", updateMotion);
});
</script>

<style scoped>
.card-stage {
  padding: 18px 12px 0;
  isolation: isolate;
}
.stack-card {
  grid-area: 1 / 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 440px;
  z-index: calc(4 - var(--depth));
  transform-origin: 50% 80%;
  transform: translateY(calc(var(--depth) * -10px)) scale(calc(1 - var(--depth) * 0.035));
  transition: transform 800ms cubic-bezier(0.22, 1, 0.36, 1), background-color 800ms ease;
  will-change: transform;
}
.stack-card[data-depth="1"] {
  transform: translate(8px, -12px) rotate(3deg) scale(0.97);
  background-color: rgb(var(--color-warning-soft));
}
.stack-card[data-depth="2"] {
  transform: translate(-7px, -24px) rotate(-3deg) scale(0.94);
  background-color: rgb(var(--color-accent-soft));
}
.stack-card[data-depth="3"] {
  transform: translate(3px, -34px) rotate(1deg) scale(0.91);
}
.stack-card > :last-child { margin-top: auto; padding-top: 1.25rem; }
.stack-card > :nth-last-child(2) { margin-bottom: 2.5rem; }
.stack-card.is-outgoing {
  animation: tuck-card 1100ms both;
  pointer-events: none;
}
@keyframes tuck-card {
  0% {
    z-index: 5;
    transform: translate(0, 0) rotate(0) scale(1);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    z-index: 5;
    transform: translate(4%, 27%) rotate(8deg) scale(1.02);
  }
  49% {
    z-index: 0;
    transform: translate(4%, 27%) rotate(8deg) scale(1.02);
    animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  }
  100% {
    z-index: 0;
    transform: translate(3px, -34px) rotate(1deg) scale(0.91);
  }
}
@media (prefers-reduced-motion: reduce) {
  .stack-card { transition: none; }
  .stack-card.is-outgoing { animation: none; }
}
</style>
