import django_filters
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Word, ReviewLog, SUGGESTED_CATEGORIES
from .serializers import (
    WordSerializer,
    GenerateWordRequestSerializer,
    ReviewSubmitSerializer,
)
from .srs import schedule_review
from .gemini_service import generate_word_info, GeminiError


class WordFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method="filter_category")
    difficulty = django_filters.CharFilter(field_name="difficulty")
    due = django_filters.BooleanFilter(method="filter_due")

    class Meta:
        model = Word
        fields = ["category", "difficulty", "due"]

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__icontains=value)

    def filter_due(self, queryset, name, value):
        today = timezone.localdate()
        if value:
            return queryset.filter(next_review_date__lte=today)
        return queryset.filter(next_review_date__gt=today)


class WordViewSet(viewsets.ModelViewSet):
    serializer_class = WordSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = WordFilter
    search_fields = ["word", "definition"]

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """Ask Gemini Flash to draft learning content for a word (not saved)."""
        serializer = GenerateWordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word = serializer.validated_data["word"].strip()

        try:
            info = generate_word_info(word)
        except GeminiError as exc:
            return Response({"detail": str(exc)}, status=exc.status_code)

        return Response(info, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="due")
    def due(self, request):
        today = timezone.localdate()
        queryset = self.filter_queryset(
            self.get_queryset().filter(next_review_date__lte=today).order_by(
                "next_review_date", "created_at"
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        word = self.get_object()
        serializer = ReviewSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quality = serializer.validated_data["quality"]

        result = schedule_review(word, quality)
        word.save()
        ReviewLog.objects.create(
            word=word,
            quality=quality,
            interval_before=result["interval_before"],
            interval_after=result["interval_after"],
        )

        return Response(self.get_serializer(word).data)

    @action(detail=False, methods=["get"], url_path="categories")
    def categories(self, request):
        used = set()
        for cats in self.get_queryset().values_list("categories", flat=True):
            used.update(cats or [])
        merged = sorted(used | set(SUGGESTED_CATEGORIES))
        return Response(merged)


class StatsView(APIView):
    def get(self, request):
        today = timezone.localdate()
        words = Word.objects.filter(user=request.user)
        total = words.count()
        due_today = words.filter(next_review_date__lte=today).count()
        new_words = words.filter(repetitions=0).count()
        reviewed_today = ReviewLog.objects.filter(
            word__user=request.user, reviewed_at__date=today
        ).count()
        learned = words.filter(repetitions__gte=1).count()

        by_difficulty = {
            level: words.filter(difficulty=level).count()
            for level in ["beginner", "intermediate", "advanced"]
        }

        return Response(
            {
                "total_words": total,
                "due_today": due_today,
                "new_words": new_words,
                "reviewed_today": reviewed_today,
                "learned": learned,
                "by_difficulty": by_difficulty,
            }
        )
