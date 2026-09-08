from django.conf import settings
from django.db import models


def default_languages():
    return ["en"]


class StudyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_profile")
    languages = models.JSONField(default=default_languages)
    active_language = models.CharField(max_length=10, default="en")
