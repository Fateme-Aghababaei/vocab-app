from django.test import SimpleTestCase

from .models import UserProfile
from .serializers import UserProfileSerializer


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
