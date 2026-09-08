from rest_framework import serializers
from .models import Word, ReviewLog
from accounts.languages import study_language


class WordSerializer(serializers.ModelSerializer):
    is_due = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()

    class Meta:
        model = Word
        fields = [
            "id",
            "word",
            "language",
            "pronunciation",
            "definition",
            "examples",
            "usage_notes",
            "collocations",
            "difficulty",
            "categories",
            "repetitions",
            "ease_factor",
            "interval_days",
            "next_review_date",
            "last_reviewed_at",
            "created_at",
            "updated_at",
            "is_due",
            "is_new",
        ]
        read_only_fields = [
            "language",
            "repetitions",
            "ease_factor",
            "interval_days",
            "next_review_date",
            "last_reviewed_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        language = study_language(request)
        word = attrs.get("word", self.instance.word if self.instance else "")
        matches = Word.objects.filter(user=request.user, language=language, word=word)
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise serializers.ValidationError({"word": "You already saved this word in this language."})
        return attrs


class GenerateWordRequestSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=100, trim_whitespace=True)


class ReviewSubmitSerializer(serializers.Serializer):
    quality = serializers.IntegerField(min_value=0, max_value=3)


class ReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLog
        fields = ["id", "word", "quality", "interval_before", "interval_after", "reviewed_at"]
