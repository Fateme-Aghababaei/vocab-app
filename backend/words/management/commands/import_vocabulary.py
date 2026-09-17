import csv
import json

from django.core.management.base import BaseCommand

from words.models import GlobalWord, Difficulty


DEFAULT_FILE = "words.csv"


class Command(BaseCommand):
    help = "Import and sync vocabulary data from a CSV file into GlobalWord."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=DEFAULT_FILE,
            help=f"Path to vocabulary CSV file (default: {DEFAULT_FILE})",
        )

    def _parse_list_field(self, raw_value):
        if not raw_value:
            return []

        value = str(raw_value).strip()

        if not value:
            return []

        # Try JSON first.
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = json.loads(value)

                if isinstance(parsed, list):
                    return [
                        str(item).strip()
                        for item in parsed
                        if str(item).strip()
                    ]
            except (json.JSONDecodeError, TypeError):
                pass

        # Support semicolon-separated values.
        if ";" in value:
            return [
                item.strip()
                for item in value.split(";")
                if item.strip()
            ]

        # Support comma-separated values.
        if "," in value:
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return [value]

    def _clean_difficulty(self, raw_difficulty):
        value = str(raw_difficulty or "").lower().strip()

        if any(level in value for level in ["a1", "a2", "beginner"]):
            return Difficulty.BEGINNER

        if any(level in value for level in ["c1", "c2", "advanced"]):
            return Difficulty.ADVANCED

        return Difficulty.INTERMEDIATE

    def handle(self, *args, **options):
        file_path = options["file"]

        self.stdout.write(
            self.style.NOTICE(
                f"\nReading vocabulary from '{file_path}'..."
            )
        )

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8-sig",
                errors="ignore",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                if not reader.fieldnames:
                    self.stderr.write(
                        self.style.ERROR("CSV file has no header.")
                    )
                    return

                self.stdout.write(
                    f"CSV columns: {', '.join(reader.fieldnames)}"
                )

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for row_number, row in enumerate(reader, start=2):
                    word = row.get("word", "").strip().lower()

                    if not word:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_number}: skipped because word is empty."
                            )
                        )
                        continue

                    data = {
                        "pronunciation": row.get(
                            "pronunciation", ""
                        ).strip(),

                        "definition": row.get(
                            "definition", ""
                        ).strip(),

                        "examples": self._parse_list_field(
                            row.get("examples")
                        ),

                        "usage_notes": row.get(
                            "usage_notes", ""
                        ).strip(),

                        "collocations": self._parse_list_field(
                            row.get("collocations")
                        ),

                        "difficulty": self._clean_difficulty(
                            row.get("difficulty", "intermediate")
                        ),

                        "categories": (
                            self._parse_list_field(
                                row.get("categories")
                            )
                            or ["Everyday Conversation"]
                        ),
                    }

                    obj, created = GlobalWord.objects.update_or_create(
                        word=word,
                        defaults=data,
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Created: {word}"
                            )
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"↻ Updated: {word}"
                            )
                        )

        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(
                    f"CSV file not found: '{file_path}'"
                )
            )
            return

        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(
                    f"Import failed: {exc}"
                )
            )
            return

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("Vocabulary sync completed!")
        )
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped: {skipped_count}")
        self.stdout.write(
            f"Total words in database: {GlobalWord.objects.count()}"
        )
        self.stdout.write("=" * 60)