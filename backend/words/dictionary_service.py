# words/dictionary_service.py
import re
import logging
import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def _clean_html(raw_html: str) -> str:
    clean = re.sub(r"<.*?>", "", raw_html)
    return clean.replace("&nbsp;", " ").replace("&quot;", '"').strip()

def correct_spelling_if_needed(word: str) -> str:
    try:
        url = f"https://api.datamuse.com/sug?s={word}&max=1"
        res = requests.get(url, headers=HEADERS, timeout=2.5)
        if res.ok:
            data = res.json()
            if data and isinstance(data, list) and "word" in data[0]:
                return data[0]["word"].lower()
    except Exception:
        pass
    return word.lower()

def fetch_from_open_apis(word: str) -> dict | None:
    cleaned_input = word.strip().lower()
    resolved_word = correct_spelling_if_needed(cleaned_input)
    is_corrected = resolved_word != cleaned_input
    dm_data = []
    pronunciation = ""
    collocations = []
    frequency_score = 0
    definition = ""
    examples = []

    try:
        dm_url = f"https://api.datamuse.com/words?sp={resolved_word}&md=dprf&ipa=1&max=1"
        dm_res = requests.get(dm_url, headers=HEADERS, timeout=2.5)
        if dm_res.ok:
            dm_data = dm_res.json()
            if dm_data and isinstance(dm_data, list):
                tags = dm_data[0].get("tags", [])
                for t in tags:
                    if t.startswith("ipa_pron:"):
                        pronunciation = f"/{t.replace('ipa_pron:', '').strip()}/"
                    elif t.startswith("f:"):
                        try:
                            frequency_score = float(t.replace("f:", ""))
                        except ValueError:
                            pass
    except Exception as e:
        logger.warning("Datamuse metadata error for '%s': %s", resolved_word, e)

    try:
        colloc_url = f"https://api.datamuse.com/words?rel_jja={resolved_word}&max=5"
        c_res = requests.get(colloc_url, headers=HEADERS, timeout=2.5)
        if c_res.ok:
            collocations = [item["word"] for item in c_res.json() if "word" in item]
    except Exception:
        pass

    try:
        wiki_url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{resolved_word}"
        wiki_res = requests.get(wiki_url, headers=HEADERS, timeout=3.0)
        if wiki_res.ok:
            wiki_data = wiki_res.json()
            en_entries = wiki_data.get("en", [])
            for section in en_entries:
                for d in section.get("definitions", []):
                    raw_def = d.get("definition", "")
                    clean_def = _clean_html(raw_def)
                    if not definition and clean_def and len(clean_def) > 6:
                        definition = clean_def
                    for ex in d.get("examples", []):
                        clean_ex = _clean_html(ex)
                        if clean_ex and clean_ex not in examples and len(examples) < 2:
                            examples.append(clean_ex)
                if definition and len(examples) >= 1:
                    break
    except Exception as e:
        logger.warning("Wiktionary lookup failed for '%s': %s", resolved_word, e)

    if not definition and dm_data and isinstance(dm_data, list) and dm_data[0].get("defs"):
        first_def = dm_data[0]["defs"][0]
        definition = first_def.split("\t")[-1].capitalize()

    if not definition:
        return None

    difficulty = "intermediate"
    if frequency_score > 30:
        difficulty = "beginner"
    elif frequency_score < 2 and frequency_score > 0:
        difficulty = "advanced"

    return {
        "word": resolved_word,
        "original_input": cleaned_input,
        "is_corrected": is_corrected,
        "pronunciation": pronunciation,
        "definition": definition,
        "examples": examples,
        "usage_notes": f"Standard lemma: {resolved_word}",
        "collocations": collocations,
        "difficulty": difficulty,
        "categories": ["Everyday Conversation"],
        "source": "open_dictionary",
    }