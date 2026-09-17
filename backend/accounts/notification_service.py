# accounts/notification_service.py
import json
import logging
import random
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException
from words.models import Word, ReviewLog
from .models import PushSubscription

logger = logging.getLogger(__name__)


def build_smart_hook(user) -> dict | None:
    """
    Analyzes user deck activity and builds an engaging psychological hook in English.
    """
    today = timezone.localdate()

    # Do not disturb if the user has already completed a review today
    already_reviewed_today = ReviewLog.objects.filter(
        word__user=user, reviewed_at__date=today
    ).exists()
    if already_reviewed_today:
        return None

    profile = getattr(user, "profile", None)
    streak = profile.streak_count if profile else 0

    # 1. Streak Saver Hook (High urgency)
    if streak >= 2:
        return {
            "title": f"🔥 Your {streak}-day streak is on the line!",
            "body": "Complete a quick 2-minute review to keep your learning streak alive.",
            "url": "/study?due=true",
        }

    # 2. Micro-Quiz Hook (Curiosity trigger)
    due_words = list(
        Word.objects.filter(
            user=user, is_mastered=False, next_review_date__lte=today
        )[:10]
    )

    if due_words:
        target_word = random.choice(due_words)
        return {
            "title": f"🤔 Quick test: Remember '{target_word.word}'?",
            "body": "Tap to check if you still know the meaning and examples.",
            "url": f"/study?word={target_word.word}",
        }

    # 3. Word Garden Metaphor Hook (Growth & progress)
    sprouts_count = Word.objects.filter(
        user=user, repetitions__lte=1, is_mastered=False
    ).count()
    if sprouts_count > 0:
        return {
            "title": "🌱 Your word garden is waiting!",
            "body": f"You have {sprouts_count} young sprouts ready to grow into mature trees today.",
            "url": "/study",
        }

    # 4. Default Motivation Hook
    return {
        "title": "📚 Time for your daily vocabulary boost",
        "body": "Review a few flashcards to keep new words fresh in long-term memory.",
        "url": "/study",
    }


def send_notification_to_user(user, payload: dict) -> int:
    """Dispatches Web Push payload to all active registered devices of the user."""
    subscriptions = PushSubscription.objects.filter(user=user)
    if not subscriptions.exists() or not settings.VAPID_PRIVATE_KEY:
        return 0

    sent_count = 0
    data_str = json.dumps(payload)

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=data_str,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL},
            )
            sent_count += 1
        except WebPushException as exc:
            # Delete expired / unsubscribed push endpoints
            if exc.response and exc.response.status_code in [404, 410]:
                sub.delete()
            logger.warning("WebPush failed for %s: %s", user.email, exc)

    return sent_count