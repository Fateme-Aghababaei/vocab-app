<template>
  <button
    type="button"
    :title="title"
    :aria-label="title"
    class="relative inline-flex items-center justify-center rounded-full transition-all duration-200 text-stone-500 hover:text-pink-600 hover:bg-pink-50 active:scale-95 shadow-sm"
    :class="[
      size === 'sm' ? 'w-7 h-7' : size === 'lg' ? 'w-11 h-11' : 'w-9 h-9',
      isSpeaking ? 'text-pink-600 bg-pink-100' : 'bg-stone-100',
    ]"
    @click="handleClick"
  >
    <!-- ripple rings, only while speaking -->
    <template v-if="isSpeaking">
      <span class="absolute inset-0 rounded-full bg-pink-400/40 animate-speak-ring"></span>
      <span class="absolute inset-0 rounded-full bg-pink-400/40 animate-speak-ring [animation-delay:0.4s]"></span>
    </template>

    <!-- آیکون بلندگوی پیش‌فرض -->
    <svg
      v-if="!isSpeaking"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      class="relative z-10"
      :class="size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'"
    >
      <path
        d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.5A2.25 2.25 0 002.25 9.75v4.5A2.25 2.25 0 004.5 16.5h1.94l4.5 4.5c.944.945 2.56.276 2.56-1.06V4.06zM18.584 5.106a.75.75 0 011.06 0c3.808 3.807 3.808 9.98 0 13.788a.75.75 0 11-1.06-1.06 8.25 8.25 0 000-11.668.75.75 0 010-1.06z"
      />
      <path
        d="M15.932 7.757a.75.75 0 011.061 0 6 6 0 010 8.486.75.75 0 01-1.06-1.061 4.5 4.5 0 000-6.364.75.75 0 010-1.06z"
      />
    </svg>

    <!-- آیکون هنگام پخش صدا: بلندگو ثابت + امواج متحرک -->
    <svg
      v-else
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      class="relative z-10 text-pink-600"
      :class="size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'"
    >
      <path
        d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.5A2.25 2.25 0 002.25 9.75v4.5A2.25 2.25 0 004.5 16.5h1.94l4.5 4.5c.944.945 2.56.276 2.56-1.06V4.06z"
      />
      <path
        class="origin-[16px_12px] animate-speak-wave"
        d="M15.932 7.757a.75.75 0 011.061 0 6 6 0 010 8.486.75.75 0 01-1.06-1.061 4.5 4.5 0 000-6.364.75.75 0 010-1.06z"
      />
      <path
        class="origin-[20px_12px] animate-speak-wave [animation-delay:0.15s]"
        d="M18.584 5.106a.75.75 0 011.06 0c3.808 3.807 3.808 9.98 0 13.788a.75.75 0 11-1.06-1.06 8.25 8.25 0 000-11.668.75.75 0 010-1.06z"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { useSpeech } from "@/composables/useSpeech";

const props = withDefaults(
  defineProps<{
    text: string;
    size?: "sm" | "md" | "lg";
    title?: string;
  }>(),
  {
    size: "md",
    title: "Word pronunciation",
  },
);

const { speak, isSpeaking } = useSpeech();

const handleClick = (e: Event) => {
  e.stopPropagation();
  speak(props.text);
};
</script>

<style scoped>
@keyframes speak-ring {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
.animate-speak-ring {
  animation: speak-ring 1.2s ease-out infinite;
}

@keyframes speak-wave {
  0%, 100% {
    opacity: 0.5;
    transform: scale(0.85);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-speak-wave {
  animation: speak-wave 0.9s ease-in-out infinite;
  transform-box: fill-box;
}
</style>
