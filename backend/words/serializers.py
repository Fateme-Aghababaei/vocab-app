from rest_framework import serializers
from .models import Word, ReviewLog, GlobalWord


class GlobalWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalWord
        fields = [
            "id",
            "word",
            "definition",
            "examples",
            "usage_notes",
            "collocations",
            "difficulty",
            "categories",
        ]


class WordSerializer(serializers.ModelSerializer):
    is_due = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()

    class Meta:
        model = Word
        fields = [
            "id",
            "word",
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
            "repetitions",
            "ease_factor",
            "interval_days",
            "next_review_date",
            "last_reviewed_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        word_text = attrs.get("word", "").strip()
        if not self.instance and Word.objects.filter(user=user, word__iexact=word_text).exists():
            raise serializers.ValidationError({"word": "This word is already saved in your flashcard list."})
        return attrs


class GenerateWordRequestSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=100, trim_whitespace=True)


class ReviewSubmitSerializer(serializers.Serializer):
    quality = serializers.IntegerField(min_value=0, max_value=3)


class ReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLog
        fields = ["id", "word", "quality", "interval_before", "interval_after", "reviewed_at"]