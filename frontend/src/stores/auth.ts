import { defineStore } from "pinia";
import { api } from "@/services/api";
import { clearToken, getToken, setToken } from "@/services/authStorage";
import type { User } from "@/types";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    // Tri-state: we don't know yet whether the stored token (if any) is
    // still valid until /me/ resolves. The router guard waits on this.
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
  },
  actions: {
    // Called once at app startup. If a token is stored, validate it against
    // the backend so refreshing the page doesn't show a flash of "logged
    // in" state for an expired/invalid token.
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
    },

    async register(email: string, password: string, name: string) {
      const { token, user } = await api.register(email, password, name);
      setToken(token);
      this.user = user;
    },

    async logout() {
      try {
        await api.logout();
      } catch {
        // Ignore network/auth errors on logout - we're clearing local state
        // regardless so the user isn't stuck.
      }
      clearToken();
      this.user = null;
    },
  },
});
