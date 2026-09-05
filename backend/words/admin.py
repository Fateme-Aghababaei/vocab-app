from django.contrib import admin
from .models import Word, ReviewLog


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "difficulty", "categories", "next_review_date", "repetitions")
    search_fields = ("word", "definition")
    list_filter = ("difficulty",)


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ("word", "quality", "interval_before", "interval_after", "reviewed_at")
    list_filter = ("quality",)
