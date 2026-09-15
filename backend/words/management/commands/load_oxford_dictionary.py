# words/management/commands/load_oxford_dictionary.py
import csv
import io
import os
import urllib.request
from django.core.management.base import BaseCommand
from words.models import GlobalWord, Difficulty

OXFORD_CSV_URL = "https://raw.githubusercontent.com/ciwga/Oxford3000_Vocab/main/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv"


class Command(BaseCommand):
    help = "Loads complete Oxford 3000 vocabulary with definitions, examples and collocations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="",
            help="Path to local CSV or JSON file (optional)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing words first",
        )

    def _map_difficulty(self, raw_val: str) -> str:
        val = str(raw_val).lower().strip()
        if any(x in val for x in ["a1", "a2", "beginner", "easy"]):
            return Difficulty.BEGINNER
        elif any(x in val for x in ["c1", "c2", "advanced", "hard"]):
            return Difficulty.ADVANCED
        return Difficulty.INTERMEDIATE

    def handle(self, *args, **options):
        file_path = options["file"]
        clear_first = options["clear"]

        if clear_first:
            self.stdout.write("Clearing existing GlobalWord table...")
            GlobalWord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Table cleared."))

        csv_content = ""

        if file_path and os.path.exists(file_path):
            self.stdout.write(f"Reading from local file: {file_path}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                csv_content = f.read()
        else:
            self.stdout.write("Downloading Oxford 3000 dataset (~1.5 MB)...")
            try:
                req = urllib.request.Request(
                    OXFORD_CSV_URL,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    csv_content = resp.read().decode("utf-8", errors="ignore")
                self.stdout.write(self.style.SUCCESS("Download finished!"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Download failed: {e}"))
                self.stdout.write(self.style.WARNING(
                    "\nIf your internet blocked raw.githubusercontent.com:\n"
                    "1. Open this link in your browser: " + OXFORD_CSV_URL + "\n"
                    "2. Press Ctrl+S and save it as 'oxford3000.csv' in the 'backend' folder.\n"
                    "3. Run: python manage.py load_oxford_dictionary --file=oxford3000.csv\n"
                ))
                return

        reader = csv.DictReader(io.StringIO(csv_content))
        objects_to_create = []
        seen = set(GlobalWord.objects.values_list("word", flat=True))

        for row in reader:
            word = ""
            definition = ""
            example = ""
            collocations = []
            difficulty = Difficulty.INTERMEDIATE

            for k, v in row.items():
                if not k or not v:
                    continue
                k_lower = k.lower().strip()
                v_clean = v.strip()

                if k_lower in ["word", "vocabulary", "term", "headword"]:
                    word = v_clean.lower()
                elif k_lower in ["definition", "meaning", "definitions"]:
                    definition = v_clean
                elif k_lower in ["example", "example sentence", "examples", "sentence"]:
                    example = v_clean
                elif k_lower in ["collocations", "collocation", "common collocations"]:
                    collocations = [c.strip() for c in v_clean.split(";") if c.strip()]
                    if not collocations:
                        collocations = [c.strip() for c in v_clean.split(",") if c.strip()]
                elif k_lower in ["level", "difficulty", "cefr"]:
                    difficulty = self._map_difficulty(v_clean)

            if not word or not definition or len(definition) < 6 or word in seen:
                continue

            examples_list = [example] if example else []

            seen.add(word)
            objects_to_create.append(
                GlobalWord(
                    word=word,
                    pronunciation="",
                    definition=definition,
                    examples=examples_list[:3],
                    usage_notes="",
                    collocations=collocations[:5],
                    difficulty=difficulty,
                    categories=["Everyday Conversation"],
                )
            )

        self.stdout.write(f"Validated {len(objects_to_create)} real Oxford cards. Inserting into database...")

        GlobalWord.objects.bulk_create(objects_to_create, batch_size=1000, ignore_conflicts=True)

        self.stdout.write("=" * 55)
        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(objects_to_create)} full Oxford cards!"))
        self.stdout.write(self.style.SUCCESS(f"Total words in GlobalWord: {GlobalWord.objects.count()}"))
        self.stdout.write("=" * 55)