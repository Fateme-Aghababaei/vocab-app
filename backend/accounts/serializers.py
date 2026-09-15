# accounts/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from .models import UserProfile
from words.models import Word, ReviewLog


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    streak_count = serializers.IntegerField(source="profile.streak_count", read_only=True)
    xp = serializers.IntegerField(source="profile.xp", read_only=True)
    level = serializers.IntegerField(source="profile.level", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "streak_count", "xp", "level"]

    def get_name(self, obj):
        return obj.first_name or obj.email.split("@")[0]


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    level = serializers.ReadOnlyField()
    level_title = serializers.ReadOnlyField()
    level_progress = serializers.ReadOnlyField()
    garden_stats = serializers.SerializerMethodField()
    today_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "email",
            "name",
            "streak_count",
            "max_streak",
            "streak_freeze_count",
            "xp",
            "level",
            "level_title",
            "level_progress",
            "daily_goal",
            "preferred_study_time",
            "notifications_enabled",
            "garden_stats",
            "today_progress",
        ]
        read_only_fields = ["streak_count", "max_streak", "streak_freeze_count", "xp"]

    def get_garden_stats(self, obj):
        words = Word.objects.filter(user=obj.user)
        mature = words.filter(Q(repetitions__gte=4) | Q(is_mastered=True)).count()
        growing = words.filter(repetitions__in=[2, 3], is_mastered=False).count()
        sprouts = words.filter(repetitions__lte=1, is_mastered=False).count()

        return {
            "sprouts": sprouts,
            "growing": growing,
            "mature": mature,
            "total_words": words.count(),
        }

    def get_today_progress(self, obj):
        today = timezone.localdate()
        reviewed_today = ReviewLog.objects.filter(
            word__user=obj.user, reviewed_at__date=today
        ).count()
        goal = obj.daily_goal or 10

        return {
            "reviewed_today": reviewed_today,
            "goal": goal,
            "is_completed": reviewed_today >= goal,
            "percentage": min(100, int((reviewed_today / goal) * 100)) if goal else 0,
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "first_name" in user_data:
            instance.user.first_name = user_data["first_name"].strip()
            instance.user.save(update_fields=["first_name"])

        return super().update(instance, validated_data)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=validated_data.get("name", "").strip(),
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = authenticate(username=email, password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Incorrect email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs["user"] = user
        return attrs
