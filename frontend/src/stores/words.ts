import { defineStore } from "pinia";
import { api, type WordFilters } from "@/services/api";
import type { NewWordPayload, ReviewQuality, Stats, Word } from "@/types";

export const useWordsStore = defineStore("words", {
  state: () => ({
    words: [] as Word[],
    wordsTotal: 0,
    dueWords: [] as Word[],
    stats: null as Stats | null,
    categories: [] as string[],
    loading: false,
    error: "" as string,
    recommendations: [] as any[],
    wordsRequest: 0,
    dueLoading: false,
    dueError: "",
    statsLoading: false,
    statsError: "",
    recommendationsLoading: false,
    recommendationsError: "",
    categoriesError: "",
    masteringIds: [] as number[],
    masteredIds: [] as number[],
  }),
  getters: {
    dueCount: (state) => state.dueWords.length,
  },
  actions: {
    async fetchWords(filters: WordFilters = {}) {
      const request = ++this.wordsRequest;
      this.loading = true;
      this.error = "";
      try {
        const words = await api.listWords(filters);
        if (request === this.wordsRequest) {
          this.wordsTotal = words.count;
          this.words = words.results.map((word) => this.masteredIds.includes(word.id)
            ? { ...word, is_mastered: true, is_due: false, is_new: false }
            : word);
        }
      } catch {
        if (request === this.wordsRequest) this.error = "We couldn’t load your words. Your library is still yours; try again in a moment.";
      } finally {
        if (request === this.wordsRequest) this.loading = false;
      }
    },

    async fetchRecommendations() {
      this.recommendationsLoading = true;
      this.recommendationsError = "";
      try {
        const data = await api.getRecommendations();
        this.recommendations = data;
      } catch {
        this.recommendationsError = "We couldn’t load your suggestions. Try again, or add a word of your own.";
      } finally {
        this.recommendationsLoading = false;
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
      this.dueLoading = true;
      this.dueError = "";
      try {
        this.dueWords = (await api.getDueWords()).filter((word) => !word.is_mastered && !this.masteredIds.includes(word.id));
      } catch {
        this.dueError = "We couldn’t load your review queue. Try again when you’re ready.";
      } finally {
        this.dueLoading = false;
      }
    },

    async fetchStats() {
      this.statsLoading = true;
      this.statsError = "";
      try {
        this.stats = await api.getStats();
      } catch {
        this.statsError = "We couldn’t load your progress. Try again in a moment.";
      } finally {
        this.statsLoading = false;
      }
    },

    async fetchCategories() {
      this.categoriesError = "";
      try {
        this.categories = await api.getCategories();
      } catch {
        this.categoriesError = "Category suggestions couldn’t load. You can still search or add your own category.";
      }
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

    async masterWord(id: number) {
      if (this.masteringIds.includes(id)) return;
      if (this.masteredIds.includes(id)) return;
      if (this.words.find((word) => word.id === id)?.is_mastered) return;
      this.masteringIds.push(id);
      try {
        const updated = await api.masterWord(id);
        this.masteredIds.push(id);
        this.words = this.words.map((word) => word.id === id ? updated : word);
        this.dueWords = this.dueWords.filter((word) => word.id !== id);
        void this.fetchStats();
        return updated;
      } finally {
        this.masteringIds = this.masteringIds.filter((wordId) => wordId !== id);
      }
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
