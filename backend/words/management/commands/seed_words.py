# words/management/commands/seed_words.py
import re
import time
from django.core.management.base import BaseCommand
from words.models import GlobalWord
from words.dictionary_service import fetch_from_open_apis


class Command(BaseCommand):
    help = "Fast, resilient seeding for GlobalWord dictionary from text files"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the text file containing words",
        )
        parser.add_argument(
            "--use-ai",
            action="store_true",
            help="Fallback to Gemini AI if open dictionary lookup fails (requires VPN/Proxy)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.3,
            help="Delay in seconds between requests (default: 0.3s)",
        )

    def _extract_category(self, line: str) -> list[str]:
        cleaned = re.sub(r"[#\-\(\)\d\+]", "", line).strip()
        cleaned = re.sub(r"\bwords\b", "", cleaned, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in re.split(r"[,/&]", cleaned) if p.strip()]
        return parts if parts else ["Everyday Conversation"]

    def handle(self, *args, **options):
        file_path = options["file_path"]
        use_ai = options["use_ai"]
        delay = options["delay"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        current_categories = ["Everyday Conversation"]
        word_items = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("#"):
                current_categories = self._extract_category(line_str)
                continue
            word_items.append((line_str.lower(), list(current_categories)))

        total = len(word_items)
        self.stdout.write(self.style.NOTICE(f"Found {total} words in '{file_path}'. Starting seeding..."))

        added_count = 0
        skipped_count = 0
        failed_count = 0

        for index, (word, categories) in enumerate(word_items, start=1):
            if GlobalWord.objects.filter(word__iexact=word).exists():
                self.stdout.write(f"[{index}/{total}] Skipped '{word}' (already exists).")
                skipped_count += 1
                continue

            self.stdout.write(f"[{index}/{total}] Fetching data for '{word}'...", ending=" ")
            data = fetch_from_open_apis(word)
            if not data and use_ai:
                try:
                    from words.gemini_service import generate_word_info
                    data = generate_word_info(word)
                except Exception:
                    data = None

            if data and data.get("definition"):
                final_categories = list(set(categories + data.get("categories", [])))
                GlobalWord.objects.create(
                    word=data.get("word", word).lower(),
                    definition=data.get("definition", ""),
                    examples=data.get("examples", []),
                    usage_notes=data.get("usage_notes", ""),
                    collocations=data.get("collocations", []),
                    difficulty=data.get("difficulty", "intermediate"),
                    categories=final_categories,
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Saved ({data.get('difficulty', 'intermediate')})"))
                added_count += 1
            else:
                self.stdout.write(self.style.WARNING("✗ Not found / Skipped"))
                failed_count += 1

            time.sleep(delay)

        self.stdout.write("\n" + "=" * 45)
        self.stdout.write(self.style.SUCCESS("Seeding Process Finished!"))
        self.stdout.write(f"Added: {added_count} | Already in DB: {skipped_count} | Failed: {failed_count}")
        self.stdout.write("=" * 45)