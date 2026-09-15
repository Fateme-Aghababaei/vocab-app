from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
    streak_count = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    streak_freeze_count = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    daily_goal = models.PositiveIntegerField(default=10)
    preferred_study_time = models.TimeField(null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

    @property
    def level(self) -> int:
        return (self.xp // 500) + 1

    @property
    def level_title(self) -> str:
        lvl = self.level
        if lvl == 1:
            return "Seedling"
        elif lvl <= 3:
            return "Word Explorer"
        elif lvl <= 6:
            return "Vocab Builder"
        elif lvl <= 10:
            return "Lexicon Master"
        return "Grandmaster"

    def update_streak_and_xp(self, earned_xp: int = 10):
        today = timezone.localdate()
        self.xp += earned_xp

        if self.last_active_date == today:
            self.save(update_fields=["xp", "updated_at"])
            return

        yesterday = today - timedelta(days=1)

        if self.last_active_date == yesterday:
            self.streak_count += 1
        elif self.last_active_date == (today - timedelta(days=2)) and self.streak_freeze_count > 0:
            self.streak_freeze_count -= 1
            self.streak_count += 1
        else:
            self.streak_count = 1

        if self.streak_count > self.max_streak:
            self.max_streak = self.streak_count

        self.last_active_date = today
        self.save(update_fields=["streak_count", "max_streak", "last_active_date", "streak_freeze_count", "xp", "updated_at"])

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()