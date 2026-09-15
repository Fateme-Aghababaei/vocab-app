"""
Resilient Gemini Flash API wrapper with Key Rotation, Model Fallback,
Typo Correction, and configurable Base URL for proxying.
"""
import json
import logging
import re
import time
import requests
from django.conf import settings
from .models import SUGGESTED_CATEGORIES
logger = logging.getLogger(__name__)
_CURRENT_KEY_INDEX = 0
ENGLISH_PATTERN = re.compile(r"^[a-zA-Z0-9\s\'\-\./,!?:;]+$")


class GeminiError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def _get_api_endpoint(model: str) -> str:
    base_url = getattr(
        settings,
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com",
    ).rstrip("/")
    return f"{base_url}/v1beta/models/{model}:generateContent"


def _get_api_keys() -> list[str]:
    keys = getattr(settings, "GEMINI_API_KEYS", [])
    if not keys and getattr(settings, "GEMINI_API_KEY", ""):
        keys = [settings.GEMINI_API_KEY]
    return keys


def _get_models() -> list[str]:
    models = getattr(settings, "GEMINI_MODELS", [])
    if not models and getattr(settings, "GEMINI_MODEL", ""):
        models = [settings.GEMINI_MODEL]
    return models or ["gemini-3.5-flash", "gemini-3.6-flash","gemini-3.7-flash", "gemini-3.8-flash"]


def _build_prompt(word: str) -> str:
    categories_hint = ", ".join(SUGGESTED_CATEGORIES)
    return f"""You are an assistant inside an English vocabulary flashcard app for a self-study learner.
A learner submitted the word/phrase: "{word}"

IMPORTANT INSTRUCTIONS:
1. If the input has a typo, misspelled letters, or is an inflected form (e.g., "abondon" -> "abandon", "runing" -> "run", "definately" -> "definitely"), identify the correct standard English lemma/base form.
2. All explanations, definitions, and examples must be in English.

Return ONLY a single JSON object (no markdown fences, no commentary) with exactly these keys:

- "word": the corrected, standard base form of the word/phrase in lowercase English (e.g. "abandon").
- "pronunciation": a US English IPA transcription enclosed in slashes (e.g. /həˈloʊ/). Maximum 200 characters. Use an empty string if unsure.
- "definition": a single clear, learner-friendly English definition (one or two sentences, plain language, no jargon).
- "examples": an array of 1-2 natural example sentences showing the word used in realistic context.
- "usage_notes": a short string with practical usage notes (formality, common mistakes, grammar patterns). Leave as an empty string if nothing notable.
- "collocations": an array of 3-6 short common collocations or set phrases.
- "difficulty": one of "beginner", "intermediate", "advanced" reflecting learner difficulty.
- "categories": an array of 1-3 practical categories from this list: {categories_hint}. You may introduce a different short category name if none fit well.

Respond with raw JSON only."""


def _clean_and_parse_json(text: str) -> dict:
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

    pronunciation = parsed.get("pronunciation", "")
    if not isinstance(pronunciation, str) or len(pronunciation) > 200:
        raise GeminiError("Gemini returned invalid pronunciation. Please try again.")
    parsed["pronunciation"] = pronunciation.strip()

    return parsed


def generate_word_info(word: str) -> dict:
    global _CURRENT_KEY_INDEX

    cleaned_word = word.strip()
    if not cleaned_word:
        raise GeminiError("Word cannot be empty.", status_code=400)

    if not ENGLISH_PATTERN.match(cleaned_word):
        raise GeminiError(
            "Only English words, phrases, and characters are supported.",
            status_code=400,
        )

    keys = _get_api_keys()
    models = _get_models()

    if not keys:
        raise GeminiError(
            "No GEMINI_API_KEYS configured on the backend. Add them to backend/.env."
        )

    prompt = _build_prompt(cleaned_word)
    num_keys = len(keys)
    key_indices_to_try = [(_CURRENT_KEY_INDEX + i) % num_keys for i in range(num_keys)]

    last_error_message = "Failed to generate word info."
    last_status = 502

    for model in models:
        url = _get_api_endpoint(model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        if "3.5" in model or "3.6" in model or "thinking" in model:
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
                logger.warning(
                    "Gemini timed out with model=%s key_idx=%s after %.1fs",
                    model,
                    key_idx,
                    elapsed,
                )
                last_error_message = "Gemini request timed out. Trying next provider..."
                last_status = 504
                continue
            except requests.RequestException as exc:
                logger.warning(
                    "Gemini connection failed model=%s: %s", model, type(exc).__name__
                )
                last_error_message = "Could not connect to Gemini."
                last_status = 503
                continue

            if response.ok:
                _CURRENT_KEY_INDEX = (key_idx + 1) % num_keys
                try:
                    data = response.json()
                    candidate = data["candidates"][0]
                    if candidate.get("finishReason") not in (None, "STOP"):
                        raise GeminiError("Gemini stopped before finishing generation.")

                    text = "".join(
                        part["text"]
                        for part in candidate["content"]["parts"]
                        if "text" in part and not part.get("thought")
                    )
                    parsed = _clean_and_parse_json(text)
                    resolved_word = parsed.get("word", cleaned_word).strip().lower()

                    return {
                        "word": resolved_word,
                        "original_input": cleaned_word,
                        "is_corrected": resolved_word != cleaned_word.lower(),
                        "pronunciation": parsed.get("pronunciation", ""),
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

            if response.status_code == 429:
                logger.warning(
                    "Gemini quota reached for key_idx=%s on model=%s. Rotating key...",
                    key_idx,
                    model,
                )
                last_error_message = "API rate limit reached. Retrying with fallback..."
                last_status = 429
                continue

            if response.status_code in (500, 502, 503, 504):
                logger.warning(
                    "Gemini server error %s on model=%s. Switching...",
                    response.status_code,
                    model,
                )
                last_error_message = "Gemini service is temporarily unavailable."
                last_status = 503
                break

            if response.status_code == 404:
                logger.warning("Model %s not found (404). Falling back to next model.", model)
                break

            if response.status_code in (401, 403):
                logger.warning("Key_idx=%s denied access (401/403). Rotating...", key_idx)
                continue

    raise GeminiError(
        f"All AI services/keys were exhausted: {last_error_message}",
        status_code=last_status,
    )


def _build_extract_prompt(text: str) -> str:
    categories_hint = ", ".join(SUGGESTED_CATEGORIES)
    return f"""You are an expert English language coach. A learner provided this text snippet:
---
{text}
---

Identify 3 to 7 of the most valuable, challenging, or natural vocabulary words, idioms, or phrasal verbs from this text for an English learner.
Standardize all extracted items to their base lemmas in lowercase.

For each item, provide:
- "word": the base lemma/phrase (e.g. "streamline", "take for granted").
- "definition": clear, learner-friendly English definition in the context of this text.
- "context_sentence": the exact sentence from the provided text where this word appeared.
- "examples": an array of 1-2 other realistic example sentences.
- "usage_notes": short practical note (grammar, register, common mistake). Empty string if none.
- "collocations": array of 2-4 common collocations.
- "difficulty": "beginner", "intermediate", or "advanced".
- "categories": array of 1-2 categories from this list if applicable: {categories_hint}.

Return ONLY a valid JSON array of objects with these keys (no markdown code blocks, no commentary)."""


def extract_vocabulary_from_text(text: str) -> list[dict]:
    cleaned_text = text.strip()
    if len(cleaned_text) < 15:
        raise GeminiError("Text snippet is too short to extract vocabulary.", status_code=400)

    keys = _get_api_keys()
    models = _get_models()
    if not keys:
        raise GeminiError("No GEMINI_API_KEYS configured.")

    prompt = _build_extract_prompt(cleaned_text)
    num_keys = len(keys)

    for model in models:
        url = _get_api_endpoint(model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        for key_idx in range(num_keys):
            current_key = keys[key_idx]
            try:
                response = requests.post(
                    url,
                    headers={
                        "x-goog-api-key": current_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=(5, settings.GEMINI_READ_TIMEOUT + 10),
                )
            except requests.RequestException:
                continue

            if response.ok:
                try:
                    data = response.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = re.sub(
                        r"^```(?:json)?|```$", "", raw_text.strip(), flags=re.MULTILINE
                    ).strip()
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        for item in parsed:
                            if "word" in item:
                                item["word"] = item["word"].strip().lower()
                        return parsed
                except Exception:
                    continue

            if response.status_code == 429:
                continue
            if response.status_code in (500, 502, 503, 504):
                break

    raise GeminiError(
        "Could not extract vocabulary from text. Please try again or use a shorter text."
    )