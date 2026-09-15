import type { Word } from "@/types";

function initialEase(difficulty: Word["difficulty"]): number {
  if (difficulty === "beginner") return 2.8;
  if (difficulty === "advanced") return 2.3;
  return 2.5;
}

export function formatInterval(days: number): string {
  if (days < 1) return "<10m";
  if (days < 1.5) return "1d";
  if (days < 21) return `${Math.round(days)}d`;
  if (days < 60) return `${Math.round(days / 7)}w`;
  if (days < 365) return `${Math.round(days / 30)}mo`;
  return `${Math.round(days / 365)}y`;
}

export function previewIntervals(word: Word): Record<0 | 1 | 2 | 3, string> {
  const ease =
    word.repetitions === 0 && (!word.ease_factor || word.ease_factor === 2.5)
      ? initialEase(word.difficulty)
      : word.ease_factor || 2.5;

  const intervalBefore = word.interval_days || 0;

  const again = 10 / (24 * 60);
  let hard: number;
  let good: number;
  let easy: number;

  if (intervalBefore < 1) {
    hard = 1;
    good = 3;
    easy = 7;
  } else {
    hard = Math.max(intervalBefore + 1, Math.round(intervalBefore * 1.2 * 10) / 10);
    good = Math.max(Math.round(intervalBefore * ease * 10) / 10, hard + 1);
    easy = Math.max(Math.round(intervalBefore * ease * 1.35 * 10) / 10, good + 2);
  }

  return {
    0: formatInterval(again),
    1: formatInterval(hard),
    2: formatInterval(good),
    3: formatInterval(easy),
  };
}