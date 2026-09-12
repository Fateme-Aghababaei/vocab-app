import axios from "axios";
import type {
  AuthResponse,
  GeneratedWordInfo,
  NewWordPayload,
  ReviewQuality,
  Stats,
  User,
  Word,
} from "@/types";
import { clearToken, getToken } from "@/services/authStorage";

const client = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// A 401 means the token is missing/expired - clear it and send the user
// back to login rather than leaving them stuck on a broken page.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      clearToken();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export interface WordFilters {
  category?: string;
  difficulty?: string;
  due?: boolean;
  search?: string;
}

function toParams(filters: WordFilters = {}) {
  const params: Record<string, string> = {};
  if (filters.category) params.category = filters.category;
  if (filters.difficulty) params.difficulty = filters.difficulty;
  if (filters.due !== undefined) params.due = String(filters.due);
  if (filters.search) params.search = filters.search;
  return params;
}

export const api = {
  async register(email: string, password: string, name: string): Promise<AuthResponse> {
    const { data } = await client.post("/auth/register/", { email, password, name });
    return data;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await client.post("/auth/login/", { email, password });
    return data;
  },

  async logout(): Promise<void> {
    await client.post("/auth/logout/");
  },

  async me(): Promise<User> {
    const { data } = await client.get("/auth/me/");
    return data;
  },

  async listWords(filters: WordFilters = {}): Promise<Word[]> {
    const { data } = await client.get("/words/", { params: toParams(filters) });
    return data.results ?? data;
  },

  async getDueWords(): Promise<Word[]> {
    const { data } = await client.get("/words/due/");
    return data;
  },

  async getWord(id: number): Promise<Word> {
    const { data } = await client.get(`/words/${id}/`);
    return data;
  },

  async generateWordInfo(word: string): Promise<GeneratedWordInfo> {
    const { data } = await client.post("/words/generate/", { word });
    return data;
  },

  async createWord(payload: NewWordPayload): Promise<Word> {
    const { data } = await client.post("/words/", payload);
    return data;
  },

  async updateWord(id: number, payload: Partial<NewWordPayload>): Promise<Word> {
    const { data } = await client.patch(`/words/${id}/`, payload);
    return data;
  },

  async deleteWord(id: number): Promise<void> {
    await client.delete(`/words/${id}/`);
  },

  async submitReview(id: number, quality: ReviewQuality): Promise<Word> {
    const { data } = await client.post(`/words/${id}/review/`, { quality });
    return data;
  },

  async getCategories(): Promise<string[]> {
    const { data } = await client.get("/words/categories/");
    return data;
  },

  async getStats(): Promise<Stats> {
    const { data } = await client.get("/stats/");
    return data;
  },

  async getRecommendations(): Promise<any[]> {
    const { data } = await client.get("/words/recommendations/");
    return data;
  },

  async claimRecommendation(id: number): Promise<Word> {
    const { data } = await client.post("/words/claim/", { id });
    return data;
  },

  async extractWordsFromText(text: string): Promise<any[]> {
    const { data } = await client.post("/words/extract/", { text });
    return data;
  },

  async batchCreateWords(words: any[]): Promise<{ created_count: number; words: Word[] }> {
    const { data } = await client.post("/words/batch-create/", { words });
    return data;
  },

};

export function apiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data;
    if (!data) return err.message;
    if (typeof data.detail === "string") return data.detail;
    // DRF validation errors look like {"field": ["msg", ...], "non_field_errors": [...]}
    const firstKey = Object.keys(data)[0];
    if (firstKey && Array.isArray(data[firstKey])) {
      return data[firstKey][0];
    }
    return err.message;
  }
  return "Something went wrong.";
}
