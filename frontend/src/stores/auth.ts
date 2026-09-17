import { defineStore } from "pinia";
import { api } from "@/services/api";
import { clearToken, getToken, setToken } from "@/services/authStorage";
import type { User } from "@/types";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    initialized: false,
    streakLoading: false,
    streakError: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
  },
  actions: {
    async refreshStreak() {
      if (!this.user || this.streakLoading) return;
      const token = getToken();
      this.streakLoading = true;
      this.streakError = false;
      try {
        const profile = await api.getProfile();
        if (this.user && getToken() === token) {
          this.user.streak_count = profile.streak_count;
        }
      } catch {
        if (getToken() === token) this.streakError = true;
      } finally {
        this.streakLoading = false;
      }
    },

    async init() {
      const token = getToken();
      if (!token) {
        this.initialized = true;
        return;
      }
      try {
        this.user = await api.me();
      } catch {
        clearToken();
        this.user = null;
      } finally {
        this.initialized = true;
      }
    },

    async login(email: string, password: string) {
      const { token, user } = await api.login(email, password);
      setToken(token);
      this.user = user;
      this.streakError = false;
    },

    async verifyEmail(email: string, code: string) {
      const { token, user } = await api.verifyEmail(email, code);
      setToken(token);
      this.user = user;
      this.streakError = false;
    },

    async logout() {
      try {
        await api.logout();
      } catch {
        // Clear the local session even if the logout request fails.
      }
      clearToken();
      this.user = null;
      this.streakError = false;
    },
  },
});
