import os
import time
from django.core.management.base import BaseCommand
from words.models import GlobalWord
from words.gemini_service import generate_word_info, GeminiError


class Command(BaseCommand):
    help = "Seed the GlobalWord dictionary from a plain text file (one word per line)"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the text file containing words (one per line)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.5,
            help="Delay in seconds between AI requests to respect rate limits (default: 1.5s)",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        delay = options["delay"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        words = [line.strip() for line in raw_lines if line.strip() and not line.startswith("#")]
        total = len(words)
        self.stdout.write(self.style.NOTICE(f"Found {total} words in '{file_path}'. Starting seeding..."))

        added_count = 0
        skipped_count = 0
        failed_count = 0

        for index, word in enumerate(words, start=1):
            normalized_word = word.lower()

            # ۱. بررسی اینکه کلمه از قبل در دیتابیس هست یا نه
            if GlobalWord.objects.filter(word__iexact=normalized_word).exists():
                self.stdout.write(f"[{index}/{total}] Skipped '{word}' (already exists).")
                skipped_count += 1
                continue

            self.stdout.write(f"[{index}/{total}] Generating info for '{word}' via AI...", ending=" ")

            # ۲. دریافت اطلاعات از جمنای
            try:
                info = generate_word_info(word)
                GlobalWord.objects.create(
                    word=normalized_word,
                    definition=info.get("definition", ""),
                    examples=info.get("examples", []),
                    usage_notes=info.get("usage_notes", ""),
                    collocations=info.get("collocations", []),
                    difficulty=info.get("difficulty", "intermediate"),
                    categories=info.get("categories", []),
                )
                self.stdout.write(self.style.SUCCESS("✓ Saved!"))
                added_count += 1
            except GeminiError as exc:
                self.stdout.write(self.style.ERROR(f"✗ Failed ({exc})"))
                failed_count += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"✗ Unexpected error ({exc})"))
                failed_count += 1

            # وقفه کوتاه برای احترام به سقف نرخ درخواست‌ها
            time.sleep(delay)

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS(f"Seeding completed!"))
        self.stdout.write(f"Added: {added_count} | Skipped: {skipped_count} | Failed: {failed_count}")
        self.stdout.write("=" * 40)