export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface Word {
  id: number;
  language: string;
  word: string;
  pronunciation: string;
  definition: string;
  examples: string[];
  usage_notes: string;
  collocations: string[];
  difficulty: Difficulty;
  categories: string[];
  repetitions: number;
  ease_factor: number;
  interval_days: number;
  next_review_date: string; // ISO date
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  is_due: boolean;
  is_new: boolean;
}

export interface GeneratedWordInfo {
  word: string;
  pronunciation: string;
  definition: string;
  examples: string[];
  usage_notes: string;
  collocations: string[];
  difficulty: Difficulty;
  categories: string[];
}

export type NewWordPayload = Omit<
  Word,
  | "id"
  | "language"
  | "repetitions"
  | "ease_factor"
  | "interval_days"
  | "next_review_date"
  | "last_reviewed_at"
  | "created_at"
  | "updated_at"
  | "is_due"
  | "is_new"
>;

export const REVIEW_QUALITY = {
  AGAIN: 0,
  HARD: 1,
  GOOD: 2,
  EASY: 3,
} as const;

export type ReviewQuality = (typeof REVIEW_QUALITY)[keyof typeof REVIEW_QUALITY];

export interface User {
  id: number;
  email: string;
  name: string;
  languages: string[];
  active_language: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Stats {
  total_words: number;
  due_today: number;
  new_words: number;
  reviewed_today: number;
  learned: number;
  by_difficulty: Record<Difficulty, number>;
}

export interface StudyLanguage {
  code: string;
  name: string;
}
