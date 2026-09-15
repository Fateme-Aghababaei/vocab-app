import django_filters
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .gemini_service import generate_word_info, extract_vocabulary_from_text, GeminiError
from .models import Word, ReviewLog, GlobalWord, SUGGESTED_CATEGORIES
from .serializers import (
    WordSerializer,
    GlobalWordSerializer,
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

    @action(detail=False, methods=["post"], url_path="extract")
    def extract_from_text(self, request):
        raw_text = request.data.get("text", "").strip()
        if len(raw_text) < 15:
            return Response(
                {"detail": "Please provide a longer text snippet (at least 15 characters)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            items = extract_vocabulary_from_text(raw_text[:3500])
        except GeminiError as exc:
            return Response({"detail": str(exc)}, status=exc.status_code)

        existing_user_words = set(
            Word.objects.filter(user=request.user).values_list("word", flat=True)
        )

        results = []
        for item in items:
            w_name = item.get("word", "").strip().lower()
            if not w_name:
                continue

            try:
                GlobalWord.objects.get_or_create(
                    word=w_name,
                    defaults={
                        "definition": item.get("definition", ""),
                        "examples": item.get("examples", []),
                        "usage_notes": item.get("usage_notes", ""),
                        "collocations": item.get("collocations", []),
                        "difficulty": item.get("difficulty", "intermediate"),
                        "categories": item.get("categories", []),
                    },
                )
            except Exception:
                pass

            item["already_in_deck"] = w_name in existing_user_words
            results.append(item)

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="batch-create")
    def batch_create_words(self, request):
        words_data = request.data.get("words", [])
        if not isinstance(words_data, list) or not words_data:
            return Response({"detail": "No words provided."}, status=status.HTTP_400_BAD_REQUEST)

        created_words = []
        for item in words_data:
            w_name = item.get("word", "").strip().lower()
            if not w_name or Word.objects.filter(user=request.user, word=w_name).exists():
                continue

            examples = item.get("examples", [])
            if item.get("context_sentence") and item["context_sentence"] not in examples:
                examples = [item["context_sentence"]] + examples

            word_obj = Word.objects.create(
                user=request.user,
                word=w_name,
                definition=item.get("definition", ""),
                examples=examples,
                usage_notes=item.get("usage_notes", ""),
                collocations=item.get("collocations", []),
                difficulty=item.get("difficulty", "intermediate"),
                categories=item.get("categories", []),
            )
            created_words.append(WordSerializer(word_obj).data)

        return Response(
            {"created_count": len(created_words), "words": created_words},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="recommendations")
    def recommendations(self, request):
        from collections import Counter

        user_words_qs = Word.objects.filter(user=request.user)
        existing_words = set(w.lower() for w in user_words_qs.values_list("word", flat=True))

        candidates = GlobalWord.objects.exclude(word__in=existing_words)

        if not candidates.exists():
            return Response([], status=status.HTTP_200_OK)

        categories_list = []
        for cats in user_words_qs.values_list("categories", flat=True):
            if isinstance(cats, list):
                categories_list.extend(cats)

        top_category = None
        if categories_list:
            top_category = Counter(categories_list).most_common(1)[0][0]

        difficulties = list(user_words_qs.values_list("difficulty", flat=True))
        user_difficulty = Counter(difficulties).most_common(1)[0][0] if difficulties else "intermediate"

        recommended_list = []

        if top_category:
            preferred = candidates.filter(
                difficulty=user_difficulty,
                categories__icontains=top_category
            ).order_by('?')[:4]
            recommended_list.extend(list(preferred))

        target_count = 4
        needed = target_count - len(recommended_list)

        if needed > 0:
            already_picked_ids = [w.id for w in recommended_list]
            random_fill = candidates.exclude(id__in=already_picked_ids).order_by('?')[:needed]
            recommended_list.extend(list(random_fill))

        serializer = GlobalWordSerializer(recommended_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="claim")
    def claim_recommendation(self, request):
        global_word_id = request.data.get("id")
        global_word = GlobalWord.objects.filter(id=global_word_id).first()

        if not global_word:
            return Response({"detail": "Word not found in dictionary."}, status=status.HTTP_404_NOT_FOUND)

        w_clean = global_word.word.strip().lower()
        if Word.objects.filter(user=request.user, word=w_clean).exists():
            return Response({"detail": "You already have this word in your deck."}, status=status.HTTP_400_BAD_REQUEST)

        word = Word.objects.create(
            user=request.user,
            word=w_clean,
            definition=global_word.definition,
            examples=global_word.examples,
            usage_notes=global_word.usage_notes,
            collocations=global_word.collocations,
            difficulty=global_word.difficulty,
            categories=global_word.categories,
        )
        return Response(WordSerializer(word).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        from .dictionary_service import fetch_from_open_apis

        serializer = GenerateWordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_word = serializer.validated_data["word"].strip().lower()

        cached = GlobalWord.objects.filter(word__iexact=raw_word).first()
        if cached:
            return Response({
                "word": cached.word,
                "original_input": raw_word,
                "is_corrected": False,
                "pronunciation": getattr(cached, "pronunciation", ""),
                "definition": cached.definition,
                "examples": cached.examples,
                "usage_notes": cached.usage_notes,
                "collocations": cached.collocations,
                "difficulty": cached.difficulty,
                "categories": cached.categories,
                "source": "database",
            }, status=status.HTTP_200_OK)

        dict_info = fetch_from_open_apis(raw_word)
        if dict_info:
            GlobalWord.objects.get_or_create(
                word=dict_info["word"].lower(),
                defaults={
                    "definition": dict_info.get("definition", ""),
                    "examples": dict_info.get("examples", []),
                    "usage_notes": dict_info.get("usage_notes", ""),
                    "collocations": dict_info.get("collocations", []),
                    "difficulty": dict_info.get("difficulty", "intermediate"),
                    "categories": dict_info.get("categories", []),
                }
            )
            return Response(dict_info, status=status.HTTP_200_OK)

        try:
            info = generate_word_info(raw_word)
        except GeminiError as exc:
            return Response({"detail": str(exc)}, status=exc.status_code)

        GlobalWord.objects.get_or_create(
            word=info["word"].lower(),
            defaults={
                "definition": info.get("definition", ""),
                "examples": info.get("examples", []),
                "usage_notes": info.get("usage_notes", ""),
                "collocations": info.get("collocations", []),
                "difficulty": info.get("difficulty", "intermediate"),
                "categories": info.get("categories", []),
            }
        )

        info["source"] = "ai"
        return Response(info, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="dictionary-search")
    def dictionary_search(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])
        matches = GlobalWord.objects.filter(word__icontains=query)[:10]
        return Response(GlobalWordSerializer(matches, many=True).data)

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

        if hasattr(request.user, "profile"):
            request.user.profile.update_streak_and_xp(earned_xp=5)

        return Response(self.get_serializer(word).data)

    @action(detail=False, methods=["get"], url_path="categories")
    def categories(self, request):
        used = set()
        for cats in self.get_queryset().values_list("categories", flat=True):
            used.update(cats or [])
        merged = sorted(used | set(SUGGESTED_CATEGORIES))
        return Response(merged)

    @action(detail=False, methods=["get"], url_path="due")
    def due(self, request):
        today = timezone.localdate()
        queryset = self.get_queryset().filter(
            is_mastered=False,
            next_review_date__lte=today
        ).order_by("ease_factor", "next_review_date", "-created_at")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="master")
    def mark_as_mastered(self, request, pk=None):
        from .srs import master_word

        word = self.get_object()
        master_word(word)

        if hasattr(request.user, "profile"):
            request.user.profile.update_streak_and_xp(earned_xp=25)

        return Response(self.get_serializer(word).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="pop-quiz")
    def pop_quiz(self, request):
        import random
        user_words = list(self.get_queryset().all())
        if len(user_words) < 4:
            return Response(
                {"detail": "You need at least 4 words in your deck for a pop quiz."},
                status=status.HTTP_400_BAD_REQUEST
            )

        quiz_sample = random.sample(user_words, min(len(user_words), 8))
        serializer = self.get_serializer(quiz_sample, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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