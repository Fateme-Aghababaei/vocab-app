from rest_framework.exceptions import ValidationError

LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "fa": "Persian", "ar": "Arabic",
    "tr": "Turkish", "ru": "Russian", "uk": "Ukrainian", "zh": "Mandarin Chinese",
    "ja": "Japanese", "ko": "Korean", "hi": "Hindi", "nl": "Dutch",
    "sv": "Swedish", "no": "Norwegian", "da": "Danish", "fi": "Finnish",
    "pl": "Polish", "el": "Greek", "he": "Hebrew", "vi": "Vietnamese",
    "th": "Thai", "id": "Indonesian", "ur": "Urdu",
}


def study_language(request):
    from .models import StudyProfile

    profile, _ = StudyProfile.objects.get_or_create(user=request.user)
    language = request.headers.get("X-Study-Language", profile.active_language)
    if language not in profile.languages or language not in LANGUAGES:
        raise ValidationError({"language": "Add this study language to your account first."})
    return language
