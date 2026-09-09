"""
Resilient Gemini Flash API wrapper with Key Rotation and Model Fallback.
Handles 429 (Rate-limits/Quota) by rotating API keys and 503/500/504 (Outages)
by switching fallback models.
"""
import json
import re
import logging
import time
import requests
from django.conf import settings
from .models import SUGGESTED_CATEGORIES

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

logger = logging.getLogger(__name__)

# شاخص سراسری برای توزیع درخواست‌ها بین کلیدها (Round-Robin)
_CURRENT_KEY_INDEX = 0


class GeminiError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def _build_prompt(word: str) -> str:
    categories_hint = ", ".join(SUGGESTED_CATEGORIES)
    return f"""You are an assistant inside an English vocabulary flashcard app for a
self-study learner. A learner just saved the word/phrase: "{word}"

Return ONLY a single JSON object (no markdown fences, no commentary) with
exactly these keys:

- "definition": a single clear, learner-friendly English definition (one or
  two sentences, plain language, no jargon).
- "examples": an array of 1-2 natural example sentences that show the word
  used in realistic context. Each sentence should be different from the
  others.
- "usage_notes": a short string with practical usage notes a learner would
  find helpful (e.g. formality, common mistakes, grammar patterns, register,
  connotation). Leave as an empty string if there's nothing notable.
- "collocations": an array of 3-6 short common collocations or set phrases
  that use this word.
- "difficulty": one of "beginner", "intermediate", "advanced" reflecting how
  hard this word is for an English learner.
- "categories": an array of 1-3 practical categories this word is most
  useful for, preferably chosen from this list when a good fit exists:
  {categories_hint}. You may introduce a different short category name if
  none of these fit well.

Respond with raw JSON only."""


def _get_api_keys() -> list[str]:
    keys = getattr(settings, "GEMINI_API_KEYS", [])
    if not keys and getattr(settings, "GEMINI_API_KEY", ""):
        keys = [settings.GEMINI_API_KEY]
    return keys


def _get_models() -> list[str]:
    models = getattr(settings, "GEMINI_MODELS", [])
    if not models and getattr(settings, "GEMINI_MODEL", ""):
        models = [settings.GEMINI_MODEL]
    return models or ["gemini-2.0-flash", "gemini-1.5-flash"]


def _clean_and_parse_json(text: str) -> dict:
    """پارس کردن امن خروجی JSON مدل و حذف بلوک‌های مارک‌داون احتمالی"""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiError("Gemini returned invalid word data. Please try again.") from exc

    if not isinstance(parsed, dict):
        raise GeminiError("Gemini returned invalid word data. Please try again.")
    if not isinstance(parsed.get("definition"), str) or not parsed["definition"].strip():
        raise GeminiError("Gemini returned no definition. Please try again.")
    for field in ("examples", "collocations", "categories"):
        value = parsed.get(field, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise GeminiError("Gemini returned invalid word data. Please try again.")
    if not isinstance(parsed.get("usage_notes", ""), str):
        raise GeminiError("Gemini returned invalid usage notes. Please try again.")
    if parsed.get("difficulty", "intermediate") not in ("beginner", "intermediate", "advanced"):
        raise GeminiError("Gemini returned an invalid difficulty. Please try again.")

    return parsed


def generate_word_info(word: str) -> dict:
    global _CURRENT_KEY_INDEX
    keys = _get_api_keys()
    models = _get_models()

    if not keys:
        raise GeminiError(
            "No GEMINI_API_KEYS configured on the backend. Add them to backend/.env."
        )

    prompt = _build_prompt(word)
    num_keys = len(keys)

    # اگر کلیدهای چندگانه داریم، از کلید جاری شروع می‌کنیم و در صورت بروز خطا به بعدی‌ها می‌رویم
    key_indices_to_try = [(_CURRENT_KEY_INDEX + i) % num_keys for i in range(num_keys)]

    last_error_message = "Failed to generate word info."
    last_status = 502

    # حلقه چرخش: مدل‌ها را به ترتیب اولویت و برای هر مدل کلیدها را تست می‌کنیم
    for model in models:
        url = GEMINI_ENDPOINT.format(model=model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json",
            },
        }

        # در مدل‌های فکری اگر نیاز به غیرفعال‌سازی یا مینیمال کردن باشد
        if "3.5" in model or "3.6" in model:
            payload["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "minimal"}

        for key_idx in key_indices_to_try:
            current_key = keys[key_idx]
            started = time.monotonic()

            try:
                response = requests.post(
                    url,
                    headers={
                        "x-goog-api-key": current_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=(5, settings.GEMINI_READ_TIMEOUT),
                )
            except requests.Timeout:
                elapsed = time.monotonic() - started
                logger.warning("Gemini timed out with model=%s key_idx=%s after %.1fs", model, key_idx, elapsed)
                last_error_message = "Gemini request timed out. Trying next provider..."
                last_status = 504
                continue
            except requests.RequestException as exc:
                logger.warning("Gemini connection failed model=%s: %s", model, type(exc).__name__)
                last_error_message = "Could not connect to Gemini."
                last_status = 503
                continue

            # حالت ۱: درخواست موفقیت‌آمیز بود (200 OK)
            if response.ok:
                # برای درخواست‌های بعدی از همین کلید یا کلید بعدی استفاده کن
                _CURRENT_KEY_INDEX = (key_idx + 1) % num_keys
                try:
                    data = response.json()
                    candidate = data["candidates"][0]
                    if candidate.get("finishReason") not in (None, "STOP"):
                        raise GeminiError("Gemini stopped before finishing generation.")

                    text = "".join(
                        part["text"] for part in candidate["content"]["parts"]
                        if "text" in part and not part.get("thought")
                    )
                    parsed = _clean_and_parse_json(text)

                    return {
                        "word": word,
                        "definition": parsed.get("definition", ""),
                        "examples": parsed.get("examples", []) or [],
                        "usage_notes": parsed.get("usage_notes", ""),
                        "collocations": parsed.get("collocations", []) or [],
                        "difficulty": parsed.get("difficulty", "intermediate"),
                        "categories": parsed.get("categories", []) or [],
                    }
                except (ValueError, KeyError, IndexError, TypeError) as exc:
                    logger.error("Error unpacking Gemini response: %s", exc)
                    last_error_message = "Gemini returned an unreadable response."
                    continue

            # حالت ۲: برخورد با خطای سهمیه یا محدودیت نرخ (429)
            if response.status_code == 429:
                logger.warning("Gemini quota reached for key_idx=%s on model=%s. Rotating key...", key_idx, model)
                last_error_message = "API rate limit reached. Retrying with fallback..."
                last_status = 429
                continue  # بلافاصله کلید بعدی امتحان می‌شود

            # حالت ۳: خطاهای سرور جمنای یا شلوغی سرویس (500, 502, 503, 504)
            if response.status_code in (500, 502, 503, 504):
                logger.warning("Gemini server error %s on model=%s. Switching...", response.status_code, model)
                last_error_message = "Gemini service is temporarily unavailable."
                last_status = 503
                break  # خطای سمت مدل است؛ برو سراغ مدل بعدی!

            # حالت ۴: مدل پیدا نشد (404)
            if response.status_code == 404:
                logger.warning("Model %s not found (404). Falling back to next model.", model)
                break  # مدل اشتباه است یا برداشته شده؛ مدل بعدی را تست کن

            # خطاهای دیگر مثل دسترسی نامعتبر (401, 403)
            if response.status_code in (401, 403):
                logger.warning("Key_idx=%s denied access (401/403). Rotating...", key_idx)
                continue

    # اگر تمام ترکیب‌های کلید و مدل شکست خوردند
    raise GeminiError(
        f"All AI services/keys were exhausted: {last_error_message}",
        status_code=last_status,
    )