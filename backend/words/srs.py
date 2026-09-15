"""
Adaptive Spaced Repetition Scheduling (SM-2 Enhanced).
Guarantees: Again < Hard < Good < Easy under all conditions.
"""
from datetime import timedelta
from django.utils import timezone

MIN_EASE_FACTOR = 1.3
MAX_EASE_FACTOR = 3.5

DIFFICULTY_STARTING_EASE = {
    "beginner": 2.8,
    "intermediate": 2.5,
    "advanced": 2.3,
}

def initial_ease_factor(difficulty: str) -> float:
    return DIFFICULTY_STARTING_EASE.get(difficulty, 2.5)

def schedule_review(word, quality: int) -> dict:
    interval_before = word.interval_days
    ease = word.ease_factor or 2.5

    if quality == 0:
        word.repetitions = 0
        word.interval_days = 1 / 144
        word.ease_factor = max(MIN_EASE_FACTOR, ease - 0.2)

    elif interval_before < 1:
        if quality == 1:  # Hard
            word.repetitions = 1
            word.interval_days = 1.0
            word.ease_factor = max(MIN_EASE_FACTOR, ease - 0.15)
        elif quality == 2:  # Good
            word.repetitions = 1
            word.interval_days = 3.0
        elif quality == 3:  # Easy
            word.repetitions = 1
            word.interval_days = 7.0
            word.ease_factor = min(MAX_EASE_FACTOR, ease + 0.15)

    else:
        hard_interval = max(interval_before + 1, round(interval_before * 1.2, 1))
        good_interval = max(round(interval_before * ease, 1), hard_interval + 1)
        easy_interval = max(round(interval_before * ease * 1.35, 1), good_interval + 2)

        if quality == 1:  # Hard
            word.repetitions += 1
            word.interval_days = hard_interval
            word.ease_factor = max(MIN_EASE_FACTOR, ease - 0.15)

        elif quality == 2:  # Good
            word.repetitions += 1
            word.interval_days = good_interval

        elif quality == 3:  # Easy
            word.repetitions += 1
            word.interval_days = easy_interval
            word.ease_factor = min(MAX_EASE_FACTOR, ease + 0.15)

    now = timezone.now()
    word.last_reviewed_at = now

    if word.interval_days < 1:
        word.next_review_date = timezone.localdate()
    else:
        word.next_review_date = (now + timedelta(days=word.interval_days)).date()

    return {"interval_before": interval_before, "interval_after": word.interval_days}


def master_word(word) -> dict:
    interval_before = word.interval_days
    now = timezone.now()

    word.is_mastered = True
    word.repetitions = max(word.repetitions, 5)
    word.interval_days = 180
    word.next_review_date = (now + timedelta(days=180)).date()
    word.last_reviewed_at = now
    word.save()

    return {"interval_before": interval_before, "interval_after": word.interval_days}