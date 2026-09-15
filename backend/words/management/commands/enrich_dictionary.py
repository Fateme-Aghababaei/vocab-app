# words/management/commands/enrich_dictionary.py
import csv
import json
import time
from django.core.management.base import BaseCommand
from django.db.models import Q
from words.models import GlobalWord
from words.gemini_service import generate_word_info, GeminiError


class Command(BaseCommand):
    help = "Enrich GlobalWord database using Gemini Key-Rotation and export clean CSV for Kaggle"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of words to process in this run (0 = all incomplete words)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=3.0,
            help="Delay in seconds between requests to respect rate limits (default: 3.0s)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update even if the word already has pronunciation and usage notes",
        )
        parser.add_argument(
            "--export",
            type=str,
            default="",
            help="Export the current GlobalWord database to a clean CSV file (e.g. --export=kaggle_oxford.csv)",
        )

    def _export_to_csv(self, file_path: str):
        self.stdout.write(f"\nExporting database to '{file_path}'...")
        words = GlobalWord.objects.all().order_by("word")
        total = words.count()

        fieldnames = [
            "word",
            "pronunciation",
            "difficulty",
            "categories",
            "definition",
            "examples",
            "usage_notes",
            "collocations",
        ]

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for w in words:
                writer.writerow({
                    "word": w.word,
                    "pronunciation": w.pronunciation,
                    "difficulty": w.difficulty,
                    "categories": json.dumps(w.categories, ensure_ascii=False),
                    "definition": w.definition,
                    "examples": json.dumps(w.examples, ensure_ascii=False),
                    "usage_notes": w.usage_notes,
                    "collocations": json.dumps(w.collocations, ensure_ascii=False),
                })

        self.stdout.write(self.style.SUCCESS(f"✓ Successfully exported {total} words to '{file_path}'!"))

    def handle(self, *args, **options):
        export_file = options["export"]
        limit = options["limit"]
        delay = options["delay"]
        force = options["force"]

        if export_file and not options.get("limit") and not options.get("force"):
            self._export_to_csv(export_file)
            return

        if force:
            queryset = GlobalWord.objects.all().order_by("word")
        else:
            queryset = GlobalWord.objects.filter(
                Q(pronunciation="") | Q(usage_notes="") | Q(examples=[])
            ).order_by("word")

        total_pending = queryset.count()
        if total_pending == 0:
            self.stdout.write(self.style.SUCCESS("All words in database are already enriched! Nothing to do."))
            if export_file:
                self._export_to_csv(export_file)
            return

        words_to_process = list(queryset[:limit] if limit > 0 else queryset)
        total = len(words_to_process)

        self.stdout.write(self.style.NOTICE(
            f"Found {total_pending} incomplete words. Starting to enrich {total} words via Gemini..."
        ))

        success_count = 0
        fail_count = 0

        for index, item in enumerate(words_to_process, start=1):
            w_text = item.word
            self.stdout.write(f"[{index}/{total}] Generating rich data for '{w_text}'...", ending=" ")

            try:
                info = generate_word_info(w_text)

                item.pronunciation = info.get("pronunciation") or item.pronunciation
                item.definition = info.get("definition") or item.definition
                item.examples = info.get("examples") or item.examples
                item.usage_notes = info.get("usage_notes") or item.usage_notes
                item.collocations = info.get("collocations") or item.collocations
                item.difficulty = info.get("difficulty") or item.difficulty

                merged_categories = list(set(item.categories + (info.get("categories") or [])))
                item.categories = merged_categories if merged_categories else ["Everyday Conversation"]

                item.save()

                self.stdout.write(self.style.SUCCESS(
                    f"✓ Saved! (IPA: {item.pronunciation} | {len(item.examples)} examples | {item.difficulty})"
                ))
                success_count += 1

            except GeminiError as exc:
                self.stdout.write(self.style.ERROR(f"✗ Gemini Error: {exc}"))
                fail_count += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"✗ Unexpected Error: {exc}"))
                fail_count += 1

            time.sleep(delay)

        self.stdout.write("\n" + "=" * 55)
        self.stdout.write(self.style.SUCCESS("Enrichment run finished!"))
        self.stdout.write(f"Updated: {success_count} | Failed: {fail_count} | Remaining incomplete: {total_pending - success_count}")
        self.stdout.write("=" * 55)

        if export_file:
            self._export_to_csv(export_file)



# python manage.py enrich_dictionary --export=oxford_complete.csv
# python manage.py sync_dictionary --limit=500
