"""
Thin wrapper around the Gemini Flash API used to auto-generate learning
content for a new word: definition, examples, usage notes, collocations,
difficulty, and categories.
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


def generate_word_info(word: str) -> dict:
    if not settings.GEMINI_API_KEY:
        raise GeminiError(
            "GEMINI_API_KEY is not configured on the backend. Add it to backend/.env."
        )

    url = GEMINI_ENDPOINT.format(model=settings.GEMINI_MODEL)
    payload = {
        "contents": [{"parts": [{"text": _build_prompt(word)}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
        },
    }

    # Vocabulary drafts do not need the model's default reasoning effort.
    # Keep this model-specific: thinking options differ between model versions.
    if settings.GEMINI_MODEL in ("gemini-3.6-flash", "gemini-3.5-flash"):
        payload["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "minimal"}

    # Retry only temporary server failures, once. Retrying quota errors or
    # timeouts immediately can waste quota and make the user wait much longer.
    started = time.monotonic()
    for attempt in range(2):
        try:
            response = requests.post(
                url,
                headers={
                    "x-goog-api-key": settings.GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=(5, settings.GEMINI_READ_TIMEOUT),
            )
        except requests.Timeout as exc:
            logger.warning("Gemini timed out model=%s elapsed=%.1fs",
                           settings.GEMINI_MODEL, time.monotonic() - started)
            raise GeminiError("Gemini took too long to respond. Please try again.", 504) from exc
        except requests.RequestException as exc:
            # Do not expose request details, proxy credentials, or API keys.
            logger.warning("Gemini connection failed model=%s error=%s",
                           settings.GEMINI_MODEL, type(exc).__name__)
            raise GeminiError("Could not connect to Gemini. Please try again.", 503) from exc

        logger.info("Gemini model=%s status=%s attempt=%s elapsed=%.1fs",
                    settings.GEMINI_MODEL, response.status_code, attempt + 1,
                    time.monotonic() - started)
        if response.status_code in (500, 502, 503, 504) and attempt == 0:
            time.sleep(1)
            continue
        break

    if not response.ok:
        logger.warning("Gemini rejected request model=%s status=%s",
                       settings.GEMINI_MODEL, response.status_code)
        if response.status_code == 429:
            raise GeminiError("Gemini's request limit or quota has been reached. Please try later or check your API quota.", 429)
        if response.status_code in (401, 403):
            raise GeminiError("Gemini denied access. Check the backend API key and its permissions.")
        if response.status_code == 404:
            raise GeminiError("The configured Gemini model is unavailable. Check GEMINI_MODEL in backend/.env.")
        if response.status_code >= 500:
            raise GeminiError("Gemini is temporarily unavailable. Please try again.", 503)
        raise GeminiError("Gemini rejected the request. Check the backend model configuration.")

    try:
        data = response.json()
        candidate = data["candidates"][0]
        if candidate.get("finishReason") not in (None, "STOP"):
            raise GeminiError("Gemini could not finish generating this word. Please try again.")
        text = "".join(
            part["text"] for part in candidate["content"]["parts"]
            if "text" in part and not part.get("thought")
        )
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise GeminiError("Gemini returned an unreadable response. Please try again.") from exc

    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(text)
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

    return {
        "word": word,
        "definition": parsed.get("definition", ""),
        "examples": parsed.get("examples", []) or [],
        "usage_notes": parsed.get("usage_notes", ""),
        "collocations": parsed.get("collocations", []) or [],
        "difficulty": parsed.get("difficulty", "intermediate"),
        "categories": parsed.get("categories", []) or [],
    }
