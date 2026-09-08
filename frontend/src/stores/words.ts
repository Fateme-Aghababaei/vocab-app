import { defineStore } from "pinia";
import { api, type WordFilters } from "@/services/api";
import type { NewWordPayload, ReviewQuality, Stats, Word } from "@/types";

let studyVersion = 0;

export const useWordsStore = defineStore("words", {
  state: () => ({
    words: [] as Word[],
    dueWords: [] as Word[],
    stats: null as Stats | null,
    categories: [] as string[],
    loading: false,
    error: "" as string,
  }),
  getters: {
    dueCount: (state) => state.dueWords.length,
  },
  actions: {
    clearStudyState() {
      studyVersion += 1;
      this.$reset();
    },
    async fetchWords(filters: WordFilters = {}) {
      const version = studyVersion;
      this.loading = true;
      this.error = "";
      try {
        const words = await api.listWords(filters);
        if (version === studyVersion) this.words = words;
      } catch (e) {
        if (version === studyVersion) this.error = "Couldn't load your words.";
      } finally {
        if (version === studyVersion) this.loading = false;
      }
    },

    async fetchDueWords() {
      const version = studyVersion;
      const result = await api.getDueWords();
      if (version === studyVersion) this.dueWords = result;
    },

    async fetchStats() {
      const version = studyVersion;
      const result = await api.getStats();
      if (version === studyVersion) this.stats = result;
    },

    async fetchCategories() {
      const version = studyVersion;
      const result = await api.getCategories();
      if (version === studyVersion) this.categories = result;
    },

    async createWord(payload: NewWordPayload) {
      const version = studyVersion;
      const word = await api.createWord(payload);
      if (version === studyVersion) this.words.unshift(word);
      return word;
    },

    async updateWord(id: number, payload: Partial<NewWordPayload>) {
      const version = studyVersion;
      const word = await api.updateWord(id, payload);
      if (version !== studyVersion) return word;
      const idx = this.words.findIndex((w) => w.id === id);
      if (idx !== -1) this.words[idx] = word;
      return word;
    },

    async deleteWord(id: number) {
      const version = studyVersion;
      await api.deleteWord(id);
      if (version !== studyVersion) return;
      this.words = this.words.filter((w) => w.id !== id);
      this.dueWords = this.dueWords.filter((w) => w.id !== id);
    },

    async reviewWord(id: number, quality: ReviewQuality) {
      const version = studyVersion;
      const updated = await api.submitReview(id, quality);
      if (version !== studyVersion) return updated;
      this.dueWords = this.dueWords.filter((w) => w.id !== id);
      const idx = this.words.findIndex((w) => w.id === id);
      if (idx !== -1) this.words[idx] = updated;
      return updated;
    },
  },
});
