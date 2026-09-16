import type { AvatarId } from "@/constants/avatars";

export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface Word {
  id: number;
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
  next_review_date: string;
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  is_due: boolean;
  is_new: boolean;
  is_mastered: boolean;
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
  | "repetitions"
  | "ease_factor"
  | "interval_days"
  | "next_review_date"
  | "last_reviewed_at"
  | "created_at"
  | "updated_at"
  | "is_due"
  | "is_new"
  | "is_mastered"
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
  streak_count?: number;
  avatar?: AvatarId | "";
}

export interface UserProfile extends User {
  avatar: AvatarId | "";
  streak_count: number;
  max_streak: number;
  streak_freeze_count: number;
  xp: number;
  level: number;
  level_title: string;
  level_progress?: {
    next_planet: string | null;
    xp_remaining: number;
    percentage: number;
  };
  daily_goal: number;
  preferred_study_time: string | null;
  notifications_enabled: boolean;
  garden_stats: {
    sprouts: number;
    growing: number;
    mature: number;
    total_words: number;
  };
  today_progress: {
    reviewed_today: number;
    goal: number;
    is_completed: boolean;
    percentage: number;
  };
}

export type ProfileSettings = Pick<
  UserProfile,
  "name" | "avatar" | "daily_goal" | "preferred_study_time" | "notifications_enabled"
>;

export type StudySettings = Omit<ProfileSettings, "avatar">;

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
