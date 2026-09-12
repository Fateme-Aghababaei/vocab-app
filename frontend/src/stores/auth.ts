import { defineStore } from "pinia";
import { api } from "@/services/api";
import { clearToken, getToken, setToken } from "@/services/authStorage";
import type { User } from "@/types";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
  },
  actions: {
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
      }
      clearToken();
      this.user = null;
    },
  },
});
