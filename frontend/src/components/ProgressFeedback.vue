<template>
  <span hidden aria-hidden="true"></span>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { useToast } from "primevue/usetoast";
import { useProgressStore } from "@/stores/progress";
import { useAuthStore } from "@/stores/auth";

const progress = useProgressStore();
const auth = useAuthStore();
const toast = useToast();

watch(() => progress.queue.length, () => {
  for (const award of progress.queue) {
    const detail = [];
    if (award.level_increased) detail.push(`${award.level_title} · Your practice is paying off!`);
    if (award.streak_increased) {
      detail.push(award.level_increased
        ? `${award.streak_count}-day streak!`
        : "Keep it going!");
    }

    toast.add({
      styleClass: `progress-toast progress-toast-${award.level_increased ? "level" : "streak"}`,
      severity: award.level_increased ? "success" : "warn",
      summary: award.level_increased
        ? `Level ${award.level} unlocked!`
        : `${award.streak_count}-day streak!`,
      detail: detail.join(" · "),
      life: award.level_increased ? 6500 : 4500,
    });
  }
  progress.clear();
});
watch(() => auth.user?.id, () => progress.clear());
</script>

<style>
.progress-toast .p-toast-message-icon {
  display: none;
}
.progress-toast .p-toast-message-content::before {
  content: "🔥";
  flex-shrink: 0;
  font-size: var(--p-toast-icon-size, 1.25rem);
  line-height: 1;
}
.progress-toast-level .p-toast-message-content::before {
  content: "🏆";
}
.progress-toast-streak .p-toast-message-content::before {
  content: "🔥";
}
</style>
