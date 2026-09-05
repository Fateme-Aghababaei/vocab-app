"""
Spaced repetition scheduling, adapted from the SM-2 algorithm (as used by
Anki/SuperMemo) with a 4-button review UI: Again / Hard / Good / Easy.

Each Word carries its own `ease_factor` and `interval_days`, which this
module mutates in place based on how well the user remembered the word and
the word's difficulty level.
"""
from datetime import timedelta
from django.utils import timezone

MIN_EASE_FACTOR = 1.3

# A word's declared difficulty nudges its *starting* ease factor, so a hard
# word is scheduled a little more often than an easy one until the user's
# own review history takes over.
DIFFICULTY_STARTING_EASE = {
    "beginner": 2.7,
    "intermediate": 2.5,
    "advanced": 2.3,
}


def initial_ease_factor(difficulty: str) -> float:
    return DIFFICULTY_STARTING_EASE.get(difficulty, 2.5)


def schedule_review(word, quality: int) -> dict:
    """
    Mutates `word`'s SRS fields based on the review quality (0-3: Again,
    Hard, Good, Easy) and returns {"interval_before", "interval_after"} for
    logging. Does not save() the word - the caller is responsible for that.
    """
    interval_before = word.interval_days

    if word.repetitions == 0 and word.ease_factor == 2.5:
        # First ever review of a freshly created word: seed ease factor
        # from its difficulty rating.
        word.ease_factor = initial_ease_factor(word.difficulty)

    if quality == 0:  # Again - forgotten, restart the learning steps
        word.repetitions = 0
        word.interval_days = 1 / 24 * 10  # ~10 minutes, resurfaces same day
        word.ease_factor = max(MIN_EASE_FACTOR, word.ease_factor - 0.2)
    elif quality == 1:  # Hard - remembered with real effort
        word.repetitions += 1
        base = interval_before if interval_before >= 1 else 1
        word.interval_days = max(1, round(base * 1.2, 2))
        word.ease_factor = max(MIN_EASE_FACTOR, word.ease_factor - 0.15)
    elif quality == 2:  # Good - remembered comfortably
        word.repetitions += 1
        if word.repetitions == 1:
            word.interval_days = 1
        elif word.repetitions == 2:
            word.interval_days = 6
        else:
            base = interval_before if interval_before >= 1 else 1
            word.interval_days = round(base * word.ease_factor, 2)
    else:  # Easy - remembered instantly
        word.repetitions += 1
        base = interval_before if interval_before >= 1 else 1
        multiplier = word.ease_factor * 1.3 if word.repetitions > 1 else 4
        word.interval_days = round(base * multiplier, 2)
        word.ease_factor = word.ease_factor + 0.15

    now = timezone.now()
    word.last_reviewed_at = now
    # Anything under a day (the "Again" bucket) comes back the same day;
    # everything else is scheduled by whole days.
    if word.interval_days < 1:
        word.next_review_date = timezone.localdate()
    else:
        word.next_review_date = (now + timedelta(days=word.interval_days)).date()

    return {"interval_before": interval_before, "interval_after": word.interval_days}
