import { defineStore } from "pinia";
import type { ProgressAward } from "@/types";

export const useProgressStore = defineStore("progress", {
  state: () => ({
    queue: [] as (ProgressAward & { id: number })[],
    sequence: 0,
  }),
  actions: {
    celebrate(award: ProgressAward) {
      if (!award.streak_increased && !award.level_increased) return;
      this.queue.push({ ...award, id: ++this.sequence });
    },
    dismiss() {
      this.queue.shift();
    },
    clear() {
      this.queue = [];
    },
  },
});
