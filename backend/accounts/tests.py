from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer


class PlanetLevelTests(SimpleTestCase):
    def test_new_account_starts_on_mercury(self):
        profile = UserProfile(xp=0)
        self.assertEqual((profile.level, profile.level_title), (1, "Mercury"))
        self.assertEqual(profile.level_progress, {
            "next_planet": "Venus", "xp_remaining": 500, "percentage": 0,
        })

    def test_crossing_xp_threshold_unlocks_next_planet(self):
        profile = UserProfile(xp=499)
        self.assertEqual(profile.level_title, "Mercury")
        self.assertEqual(profile.level_progress["xp_remaining"], 1)
        profile.xp += 1
        self.assertEqual((profile.level, profile.level_title), (2, "Venus"))
        self.assertEqual(profile.level_progress, {
            "next_planet": "Earth", "xp_remaining": 500, "percentage": 0,
        })

    def test_planets_follow_solar_system_order(self):
        for level, planet in enumerate([
            "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",
        ], start=1):
            with self.subTest(level=level):
                self.assertEqual(UserProfile(xp=(level - 1) * 500).level_title, planet)

    def test_progress_toward_last_planet(self):
        profile = UserProfile(xp=3499)
        self.assertEqual(profile.level_title, "Uranus")
        self.assertEqual(profile.level_progress, {
            "next_planet": "Neptune", "xp_remaining": 1, "percentage": 99,
        })

    def test_neptune_completion_keeps_higher_levels_valid(self):
        for xp, level in [(3500, 8), (4000, 9), (10000, 21)]:
            with self.subTest(xp=xp):
                profile = UserProfile(xp=xp)
                self.assertEqual((profile.level, profile.level_title), (level, "Neptune"))
                self.assertEqual(profile.level_progress, {
                    "next_planet": None, "xp_remaining": 0, "percentage": 100,
                })

    def test_planet_progress_is_read_only_in_profile_api(self):
        serializer = UserProfileSerializer(data={
            "level_title": "Neptune",
            "level_progress": {"next_planet": None, "percentage": 100},
        }, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data, {})
        self.assertTrue(serializer.fields["level_progress"].read_only)


class AvatarSettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="avatar@example.com", email="avatar@example.com", first_name="Explorer",
        )

    def test_new_account_uses_initial_by_default(self):
        self.assertEqual(self.user.profile.avatar, "")
        self.assertEqual(UserSerializer(self.user).data["avatar"], "")

    def test_each_avatar_persists_and_is_available_to_auth_responses(self):
        expected_avatars = [
            "Nilo",
            "Mobi",
            "Lumi",
            "Rico",
            "Selu",
            "Orbi",
            "Veya",
            "Soli",
        ]
        for avatar in expected_avatars:
            with self.subTest(avatar=avatar):
                serializer = UserProfileSerializer(
                    self.user.profile, data={"avatar": avatar}, partial=True,
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)
                serializer.save()
                self.user.profile.refresh_from_db()
                self.assertEqual(self.user.profile.avatar, avatar)
                self.assertEqual(UserSerializer(self.user).data["avatar"], avatar)
                self.assertEqual(self.user.first_name, "Explorer")

    def test_avatar_can_be_cleared_without_changing_other_preferences(self):
        profile = self.user.profile
        profile.avatar = "Nilo"
        profile.daily_goal = 20
        profile.save()
        serializer = UserProfileSerializer(profile, data={"avatar": ""}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        profile.refresh_from_db()
        self.assertEqual(profile.avatar, "")
        self.assertEqual(profile.daily_goal, 20)

    def test_invalid_avatar_is_rejected_without_changing_selection(self):
        for avatar in ["unknown", "../other-image.png", "https://example.com/avatar.png", None]:
            with self.subTest(avatar=avatar):
                serializer = UserProfileSerializer(
                    self.user.profile, data={"avatar": avatar}, partial=True,
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("avatar", serializer.errors)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.avatar, "")


from datetime import timedelta
import re
from unittest.mock import patch
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import EmailCode


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.email = "learner@example.com"
        self.password = "Learning!Words42"

    def post(self, action, **data):
        return self.client.post(reverse("auth-" + action), data, format="json")

    def signup(self):
        return self.post("register", email=self.email, password=self.password, name="Learner")

    def code(self):
        return re.search(r"\b[0-9]{6}\b", mail.outbox[-1].body).group()

    def test_signup_requires_verification_and_code_is_single_use(self):
        response = self.signup()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("token", response.data)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)
        self.assertEqual(mail.outbox[0].to, [self.email])
        code = self.code()
        self.assertNotEqual(EmailCode.objects.get(user=user).code_hash, code)
        self.assertEqual(self.post("login", email=self.email, password=self.password).status_code, 400)
        response = self.post("verify-email", email=self.email.upper(), code=code)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(self.post("verify-email", email=self.email, code=code).status_code, 400)
        self.assertEqual(self.post("login", email=self.email, password=self.password).status_code, 200)

    def test_expiry_attempt_limit_and_resend(self):
        self.signup()
        code = self.code()
        for _ in range(5):
            self.assertEqual(self.post("verify-email", email=self.email, code="000000" if code != "000000" else "111111").status_code, 400)
        self.assertEqual(self.post("verify-email", email=self.email, code=code).status_code, 400)
        self.post("resend-code", email=self.email)
        self.assertEqual(len(mail.outbox), 1)
        EmailCode.objects.update(sent_at=timezone.now() - timedelta(seconds=61))
        self.post("resend-code", email=self.email)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(EmailCode.objects.get().attempts, 0)
        EmailCode.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.post("verify-email", email=self.email, code=self.code()).status_code, 400)

    def test_reset_revokes_token_and_changes_password(self):
        user = User.objects.create_user(username=self.email, email=self.email, password=self.password)
        token = Token.objects.create(user=user)
        response = self.post("forgot-password", email=self.email)
        self.assertEqual(response.status_code, 200)
        code = self.code()
        self.assertEqual(self.post("verify-email", email=self.email, code=code).status_code, 400)
        self.assertEqual(self.post("reset-password", email=self.email, code=code, password="short").status_code, 400)
        response = self.post("reset-password", email=self.email, code=code, password="Another!Password42")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Token.objects.filter(key=token.key).exists())
        self.assertEqual(self.post("login", email=self.email, password=self.password).status_code, 400)
        self.assertEqual(self.post("login", email=self.email, password="Another!Password42").status_code, 200)
        self.assertEqual(self.post("reset-password", email=self.email, code=code, password=self.password).status_code, 400)

    def test_reset_does_not_reveal_unknown_or_unverified_accounts(self):
        self.signup()
        unknown = self.post("forgot-password", email="unknown@example.com")
        pending = self.post("forgot-password", email=self.email)
        User.objects.create_user(username="active@example.com", email="active@example.com")
        active = self.post("forgot-password", email="active@example.com")
        self.assertEqual(unknown.data, pending.data)
        self.assertEqual(unknown.data, active.data)
        self.assertEqual(len(mail.outbox), 2)

    @patch("accounts.email_codes.send_mail", side_effect=OSError("SMTP unavailable"))
    def test_delivery_failure_rolls_back_signup(self, mocked):
        self.assertEqual(self.signup().status_code, 503)
        self.assertFalse(User.objects.filter(email=self.email).exists())

    def test_requests_are_throttled(self):
        for _ in range(20):
            self.post("forgot-password", email="unknown@example.com")
        self.assertEqual(self.post("forgot-password", email="unknown@example.com").status_code, 429)
