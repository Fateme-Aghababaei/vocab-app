import { defineStore } from "pinia";
import { api, type WordFilters } from "@/services/api";
import type { NewWordPayload, ReviewQuality, Stats, Word } from "@/types";

export const useWordsStore = defineStore("words", {
  state: () => ({
    words: [] as Word[],
    dueWords: [] as Word[],
    stats: null as Stats | null,
    categories: [] as string[],
    loading: false,
    error: "" as string,
    recommendations: [] as any[],
  }),
  getters: {
    dueCount: (state) => state.dueWords.length,
  },
  actions: {
    async fetchWords(filters: WordFilters = {}) {
      this.loading = true;
      this.error = "";
      try {
        this.words = await api.listWords(filters);
      } catch {
        this.error = "Couldn't load your words.";
      } finally {
        this.loading = false;
      }
    },

    async fetchRecommendations() {
      try {
        const data = await api.getRecommendations();
        this.recommendations = data;
      } catch (error) {
        console.error("Failed to load recommendations", error);
      }
    },

    async claimRecommendation(id: number) {
      const newWord = await api.claimRecommendation(id);
      this.recommendations = this.recommendations.filter((r) => r.id !== id);
      this.words.unshift(newWord);
      await this.fetchStats();
      return newWord;
    },

    async fetchDueWords() {
      this.dueWords = await api.getDueWords();
    },

    async fetchStats() {
      this.stats = await api.getStats();
    },

    async fetchCategories() {
      this.categories = await api.getCategories();
    },

    async createWord(payload: NewWordPayload) {
      const word = await api.createWord(payload);
      this.words.unshift(word);
      return word;
    },

    async updateWord(id: number, payload: Partial<NewWordPayload>) {
      const word = await api.updateWord(id, payload);
      const idx = this.words.findIndex((w) => w.id === id);
      if (idx !== -1) this.words[idx] = word;
      return word;
    },

    async deleteWord(id: number) {
      await api.deleteWord(id);
      this.words = this.words.filter((w) => w.id !== id);
      this.dueWords = this.dueWords.filter((w) => w.id !== id);
    },

    async reviewWord(id: number, quality: ReviewQuality) {
      const updated = await api.submitReview(id, quality);
      this.dueWords = this.dueWords.filter((w) => w.id !== id);
      const idx = this.words.findIndex((w) => w.id === id);
      if (idx !== -1) this.words[idx] = updated;
      return updated;
    },
  },
});
