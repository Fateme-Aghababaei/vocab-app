from django.conf import settings
from django.db import models
from django.utils import timezone


class Difficulty(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"


# Suggested categories shown in the UI. Stored as free-form strings so users
# (or the LLM) aren't hard-blocked from introducing a new one.
SUGGESTED_CATEGORIES = [
    "Everyday Conversation",
    "Work",
    "Travel",
    "Sports",
    "Technology",
    "Academic",
    "Business",
    "Food & Dining",
    "Health",
    "Nature",
    "Arts & Culture",
    "News & Media",
]


class Word(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="words", on_delete=models.CASCADE
    )
    word = models.CharField(max_length=100)

    # --- LLM-generated (user-editable) learning content ---
    pronunciation = models.CharField(max_length=200, blank=True, default="")
    definition = models.TextField(blank=True)
    examples = models.JSONField(default=list, blank=True)  # list[str]
    usage_notes = models.TextField(blank=True)
    collocations = models.JSONField(default=list, blank=True)  # list[str]
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE
    )
    categories = models.JSONField(default=list, blank=True)  # list[str]

    # --- Spaced repetition state (SM-2 derived) ---
    repetitions = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.FloatField(default=0)
    next_review_date = models.DateField(default=timezone.localdate)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "word"], name="unique_word_per_user"),
        ]

    def __str__(self):
        return self.word

    @property
    def is_due(self):
        return self.next_review_date <= timezone.localdate()

    @property
    def is_new(self):
        return self.repetitions == 0


class ReviewLog(models.Model):
    """One row per flashcard review, kept for stats/history."""

    class Quality(models.IntegerChoices):
        AGAIN = 0, "Again"
        HARD = 1, "Hard"
        GOOD = 2, "Good"
        EASY = 3, "Easy"

    word = models.ForeignKey(Word, related_name="review_logs", on_delete=models.CASCADE)
    quality = models.PositiveSmallIntegerField(choices=Quality.choices)
    interval_before = models.FloatField()
    interval_after = models.FloatField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]
class GlobalWord(models.Model):
    word = models.CharField(max_length=100, unique=True, db_index=True)
    definition = models.TextField(blank=True)
    examples = models.JSONField(default=list, blank=True)
    usage_notes = models.TextField(blank=True)
    collocations = models.JSONField(default=list, blank=True)
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE
    )
    categories = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["word"]
        verbose_name = "Global Word"
        verbose_name_plural = "Global Words (Dictionary)"

    def __str__(self):
        return self.word