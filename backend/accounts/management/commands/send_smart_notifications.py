from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import UserProfile
from accounts.notification_service import build_smart_hook, send_notification_to_user


class Command(BaseCommand):
    help = "Dispatches smart contextual notifications based on user's preferred study time"

    def handle(self, *args, **options):
        now_time = timezone.localtime().time()
        current_hour = now_time.hour

        self.stdout.write(f"Running smart notification dispatcher for hour: {current_hour}:00...")

        profiles = UserProfile.objects.filter(
            notifications_enabled=True,
            preferred_study_time__hour=current_hour
        ).select_related("user")

        dispatched = 0
        for p in profiles:
            hook = build_smart_hook(p.user)
            if hook:
                count = send_notification_to_user(p.user, hook)
                if count > 0:
                    dispatched += 1
                    self.stdout.write(self.style.SUCCESS(f"Sent hook '{hook['title']}' to {p.user.email}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Sent to {dispatched} users."))