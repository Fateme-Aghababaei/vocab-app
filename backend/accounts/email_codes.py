import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import APIException

from .models import EmailCode


class DeliveryError(APIException):
    status_code = 503
    default_detail = "We couldn't send your email. Please try again shortly."


def send_code(user, purpose):
    # Call while holding the user's row lock in a transaction.
    previous = EmailCode.objects.filter(user=user, purpose=purpose).first()
    if previous and previous.sent_at > timezone.now() - timedelta(seconds=60):
        return
    code = f"{secrets.randbelow(1000000):06d}"
    EmailCode.objects.update_or_create(user=user, purpose=purpose, defaults={
        "code_hash": make_password(code), "attempts": 0,
        "sent_at": timezone.now(), "expires_at": timezone.now() + timedelta(minutes=10),
    })
    action = "verify your email" if purpose == "signup" else "reset your password"
    try:
        sent = send_mail(
            f"Memento: {action}",
            f"Your code to {action} is {code}.\n\nThis code expires in 10 minutes. "
            "If you didn't request this, you can ignore this email.",
            settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False,
        )
        if not sent:
            raise RuntimeError("Email backend did not accept the message")
    except Exception as exc:
        raise DeliveryError() from exc


def check_code(user, purpose, code):
    challenge = EmailCode.objects.select_for_update().filter(user=user, purpose=purpose).first()
    if not challenge or challenge.expires_at <= timezone.now() or challenge.attempts >= 5:
        return False
    challenge.attempts += 1
    challenge.save(update_fields=["attempts"])
    return check_password(code, challenge.code_hash)
