# words/management/commands/sync_dictionary.py
import csv
import io
import json
import os
import time
import urllib.request
from django.core.management.base import BaseCommand
from words.models import GlobalWord, Difficulty, SUGGESTED_CATEGORIES
from words.gemini_service import generate_word_info, GeminiError

OXFORD_WORDS_URL = "https://raw.githubusercontent.com/ciwga/Oxford3000_Vocab/main/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv"

FIELDNAMES = [
    "word",
    "pronunciation",
    "difficulty",
    "categories",
    "definition",
    "examples",
    "usage_notes",
    "collocations",
]


class Command(BaseCommand):
    help = "Smart sync: Loads vocabulary from CSV if exists, otherwise downloads Oxford 3000, enriches via Gemini, and builds the CSV progressively."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="oxford_dictionary.csv",
            help="Path to the dictionary CSV file (default: oxford_dictionary.csv)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of words to process with AI (0 = no limit)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.8,
            help="Delay in seconds between Gemini requests (default: 1.8s)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear GlobalWord table before importing",
        )

    def _parse_list_field(self, raw_val) -> list[str]:
        if not raw_val:
            return []
        val_str = str(raw_val).strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass

        if ";" in val_str:
            return [x.strip() for x in val_str.split(";") if x.strip()]
        if "," in val_str:
            return [x.strip() for x in val_str.split(",") if x.strip()]
        return [val_str]

    def _clean_difficulty(self, raw_diff: str) -> str:
        val = str(raw_diff).lower().strip()
        if any(x in val for x in ["a1", "a2", "beginner"]):
            return Difficulty.BEGINNER
        elif any(x in val for x in ["c1", "c2", "advanced"]):
            return Difficulty.ADVANCED
        return Difficulty.INTERMEDIATE

    def _import_from_csv(self, file_path: str, clear: bool):
        self.stdout.write(self.style.SUCCESS(f"\n[Mode 1] Found local CSV file: '{file_path}'"))

        if clear:
            self.stdout.write("Clearing existing GlobalWord table...")
            GlobalWord.objects.all().delete()

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            objects_to_create = []
            seen = set(GlobalWord.objects.values_list("word", flat=True))

            for row in reader:
                w = row.get("word", "").strip().lower()
                if not w or w in seen:
                    continue

                seen.add(w)
                objects_to_create.append(
                    GlobalWord(
                        word=w,
                        pronunciation=row.get("pronunciation", "").strip(),
                        definition=row.get("definition", "").strip(),
                        examples=self._parse_list_field(row.get("examples")),
                        usage_notes=row.get("usage_notes", "").strip(),
                        collocations=self._parse_list_field(row.get("collocations")),
                        difficulty=self._clean_difficulty(row.get("difficulty", "intermediate")),
                        categories=self._parse_list_field(row.get("categories")) or ["Everyday Conversation"],
                    )
                )

        self.stdout.write(f"Parsed {len(objects_to_create)} valid words. Inserting into database...")
        GlobalWord.objects.bulk_create(objects_to_create, batch_size=1000, ignore_conflicts=True)

        self.stdout.write("=" * 55)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully imported {len(objects_to_create)} words from CSV!"))
        self.stdout.write(self.style.SUCCESS(f"Total words in dictionary: {GlobalWord.objects.count()}"))
        self.stdout.write("=" * 55)

    def _download_and_enrich(self, file_path: str, limit: int, delay: float):
        self.stdout.write(self.style.WARNING(f"\n[Mode 2] File '{file_path}' not found."))
        self.stdout.write("Downloading Oxford 3000 base word list...")

        words_list = []
        try:
            req = urllib.request.Request(OXFORD_WORDS_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                reader = csv.DictReader(io.StringIO(content))
                for r in reader:
                    for k, v in r.items():
                        if k and k.lower().strip() in ["word", "vocabulary", "term", "headword"]:
                            clean_w = v.strip().lower()
                            if clean_w and clean_w not in words_list:
                                words_list.append(clean_w)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(words_list)} base words from Oxford list."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to download word list: {e}"))
            return

        existing_in_db = set(GlobalWord.objects.values_list("word", flat=True))
        file_is_new = not os.path.exists(file_path)

        existing_in_csv = set()
        if not file_is_new:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    if row.get("word"):
                        existing_in_csv.add(row["word"].strip().lower())

        already_done = existing_in_db.union(existing_in_csv)
        pending_words = [w for w in words_list if w not in already_done]

        if limit > 0:
            pending_words = pending_words[:limit]

        total = len(pending_words)
        if total == 0:
            self.stdout.write(self.style.SUCCESS("All words are already enriched and synced!"))
            return

        self.stdout.write(self.style.NOTICE(f"Enriching {total} words using Gemini AI and writing to '{file_path}'..."))

        with open(file_path, "a", encoding="utf-8", newline="") as csv_out:
            writer = csv.DictWriter(csv_out, fieldnames=FIELDNAMES)
            if file_is_new:
                writer.writeheader()
                csv_out.flush()

            success_count = 0
            fail_count = 0

            for idx, word_text in enumerate(pending_words, start=1):
                self.stdout.write(f"[{idx}/{total}] Enriching '{word_text}' via Gemini...", ending=" ")

                try:
                    info = generate_word_info(word_text)
                    w = info.get("word", word_text).lower()
                    pronunciation = info.get("pronunciation", "")
                    definition = info.get("definition", "")
                    examples = info.get("examples", [])
                    usage_notes = info.get("usage_notes", "")
                    collocations = info.get("collocations", [])
                    difficulty = self._clean_difficulty(info.get("difficulty", "intermediate"))
                    categories = info.get("categories", ["Everyday Conversation"])

                    GlobalWord.objects.update_or_create(
                        word=w,
                        defaults={
                            "pronunciation": pronunciation,
                            "definition": definition,
                            "examples": examples,
                            "usage_notes": usage_notes,
                            "collocations": collocations,
                            "difficulty": difficulty,
                            "categories": categories,
                        },
                    )

                    writer.writerow({
                        "word": w,
                        "pronunciation": pronunciation,
                        "difficulty": difficulty,
                        "categories": json.dumps(categories, ensure_ascii=False),
                        "definition": definition,
                        "examples": json.dumps(examples, ensure_ascii=False),
                        "usage_notes": usage_notes,
                        "collocations": json.dumps(collocations, ensure_ascii=False),
                    })
                    csv_out.flush()

                    self.stdout.write(self.style.SUCCESS(f"✓ Saved! (IPA: {pronunciation} | {difficulty})"))
                    success_count += 1

                except GeminiError as exc:
                    self.stdout.write(self.style.ERROR(f"✗ Gemini error: {exc}"))
                    fail_count += 1
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"✗ Error: {exc}"))
                    fail_count += 1

                time.sleep(delay)

        self.stdout.write("=" * 55)
        self.stdout.write(self.style.SUCCESS(f"Sync complete! Processed: {success_count} | Failed: {fail_count}"))
        self.stdout.write(self.style.SUCCESS(f"Dataset successfully appended to '{file_path}'"))
        self.stdout.write("=" * 55)

    def handle(self, *args, **options):
        file_path = options["file"]
        clear = options["clear"]
        limit = options["limit"]
        delay = options["delay"]

        if os.path.exists(file_path):
            self._import_from_csv(file_path, clear)
        else:
            self._download_and_enrich(file_path, limit, delay)


# python manage.py sync_dictionary --file=oxford_complete.csv
# python manage.py sync_dictionary --file=oxford_complete.csv --clear ✅
# python manage.py sync_dictionary