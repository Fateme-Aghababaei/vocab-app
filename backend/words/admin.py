from django.contrib import admin
from .models import Word, ReviewLog, GlobalWord


@admin.register(GlobalWord)
class GlobalWordAdmin(admin.ModelAdmin):
    list_display = ("word", "difficulty", "categories", "created_at")
    search_fields = ("word", "definition")
    list_filter = ("difficulty",)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "difficulty", "categories", "next_review_date", "repetitions")
    search_fields = ("word", "definition")
    list_filter = ("difficulty",)


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ("word", "quality", "interval_before", "interval_after", "reviewed_at")
    list_filter = ("quality",)