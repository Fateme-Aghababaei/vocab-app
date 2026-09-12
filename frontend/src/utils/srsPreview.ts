import type { Word } from "@/types";

function initialEase(difficulty: Word["difficulty"]): number {
  if (difficulty === "beginner") return 2.7;
  if (difficulty === "advanced") return 2.3;
  return 2.5;
}

export function formatInterval(days: number): string {
  if (days < 1) return "<10m";
  if (days < 1.5) return "1d";
  if (days < 21) return `${Math.round(days)}d`;
  if (days < 60) return `${Math.round(days / 7)}w`;
  return `${Math.round(days / 30)}mo`;
}

export function previewIntervals(word: Word): Record<0 | 1 | 2 | 3, string> {
  const ease = word.repetitions === 0 && word.ease_factor === 2.5
    ? initialEase(word.difficulty)
    : word.ease_factor;
  const base = word.interval_days >= 1 ? word.interval_days : 1;

  const again = 10 / (24 * 60);
  const hard = Math.max(1, base * 1.2);
  let good: number;
  if (word.repetitions === 0) good = 1;
  else if (word.repetitions === 1) good = 6;
  else good = base * ease;
  const easy = base * (word.repetitions > 0 ? ease * 1.3 : 4);

  return {
    0: formatInterval(again),
    1: formatInterval(hard),
    2: formatInterval(good),
    3: formatInterval(easy),
  };
}
