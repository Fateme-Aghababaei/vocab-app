<template>
  <span v-if="word.is_mastered" class="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2.5 py-1 text-xs font-semibold text-accent-strong" title="This word is mastered and no longer appears in reviews">
    <i class="pi pi-check-circle" aria-hidden="true"></i>
    Mastered
  </span>
  <button
    v-else
    type="button"
    class="inline-flex h-10 w-10 items-center justify-center rounded-full text-faint transition-colors hover:bg-accent-soft hover:text-accent disabled:cursor-wait disabled:opacity-50"
    :disabled="busy"
    :aria-label="busy ? `Marking ${word.word} as mastered` : `Mark ${word.word} as mastered`"
    v-tooltip.top="busy ? 'Marking as mastered…' : 'Mark as mastered'"
    @click.stop="confirmMastery"
  >
    <i :class="busy ? 'pi pi-spinner pi-spin' : 'pi pi-star'" aria-hidden="true"></i>
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { useWordsStore } from "@/stores/words";
import { useAuthStore } from "@/stores/auth";
import { apiErrorMessage } from "@/services/api";
import type { Word } from "@/types";

const props = defineProps<{ word: Word }>();
const store = useWordsStore();
const auth = useAuthStore();
const confirm = useConfirm();
const toast = useToast();
const busy = computed(() => store.masteringIds.includes(props.word.id));

function confirmMastery() {
  if (busy.value || props.word.is_mastered) return;
  confirm.require({
    header: "Mark word as mastered?",
    message: `“${props.word.word}” will no longer appear in your review queue. This can’t be changed from the app yet.`,
    icon: "pi pi-star",
    acceptLabel: "Mark mastered",
    acceptProps: { severity: "primary" },
    rejectLabel: "Keep reviewing",
    rejectProps: { text: true, severity: "secondary" },
    accept: async () => {
      try {
        const word = await store.masterWord(props.word.id);
        if (!word) return;
        void auth.refreshStreak();
        toast.add({ severity: "success", summary: "Word mastered", detail: `“${word.word}” will no longer appear in reviews.`, life: 3500 });
      } catch (error) {
        toast.add({ severity: "error", summary: "Couldn’t mark word as mastered", detail: `${apiErrorMessage(error)} Your word is still in practice. Please try again.`, life: 5000 });
      }
    },
  });
}
</script>
