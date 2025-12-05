import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Final, List
from uuid import uuid4

from models import JournalEntry

DB_FILE = Path("journal.json")
DASH_LENGTH: Final[int] = 80


class JournalDatabase:
    def __init__(self, db_file: Path):
        self.db_file = db_file
        if not self.db_file.exists():
            self.db_file.touch(exist_ok=True)

    def load_entries(self) -> List[JournalEntry]:
        """Load journal entries from the JSON file."""
        entries: List[JournalEntry] = []
        with self.db_file.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return [JournalEntry(**entry) for entry in data]
            except json.JSONDecodeError:
                return entries

    def save_entries(self, entries: List[JournalEntry]) -> None:
        """Save journal entries to the JSON file."""
        with self.db_file.open("w", encoding="utf-8") as f:
            json.dump([asdict(entry) for entry in entries], f, indent=4)

    def get_existing_ids(self, entries: List[JournalEntry]) -> List[str]:
        """Get all existing IDs from the journal entries."""
        return [entry.id for entry in entries]

    def add_entry(
        self, title: str, content: str, tags: List[str] | None = None
    ) -> None:
        """Create a new journal entry and save it to the JSON file."""
        entries = self.load_entries()
        existing_ids = self.get_existing_ids(entries)
        if existing_ids:
            new_id = str(uuid4())
            while new_id in existing_ids:
                new_id = str(uuid4())
        else:
            new_id = str(uuid4())
        tags = [tag.strip() for tag in tags] if tags else []  # type: ignore
        journal_entry = JournalEntry(
            id=new_id,
            title=title,
            content=content,
            date=datetime.now().isoformat(),
            tags=tags,
        )
        entries.append(journal_entry)
        self.save_entries(entries)

    def list_entries(self) -> None:
        """Print all journal entries to the console."""
        entries = self.load_entries()
        for entry in entries:
            print(entry.summary)
        print(f"{'-'*DASH_LENGTH}\nTotal entries: {len(entries)}")

    def search_entries_by_tags(self, tags: List[str]) -> List[JournalEntry] | None:
        """Filter entries that contain all specified tags."""
        entries = self.load_entries()
        if not tags:
            return entries
        # return [entry for entry in entries if all(tag in entry.tags for tag in tags)]

    def search_entries(self, query: str, tags: bool = False) -> List[JournalEntry]:
        """Search for journal entries by title or content."""
        if tags:
            # Buscar por tags
            return [
                entry
                for entry in self.load_entries()
                if query.lower() in [t.lower() for t in entry.tags]
            ]
        else:
            return [
                entry
                for entry in self.load_entries()
                if query.lower() in entry.title.lower()
            ]

    def most_common_tag(self, entries: List[JournalEntry]) -> str:
        """Return the most common tag in the journal."""
        return Counter(tag for entry in entries for tag in entry.tags).most_common(1)[
            0
        ][0]

    def delete_entry(self, id: str) -> None:
        """Delete a journal entry by ID."""
        entries = self.load_entries()
        existing_ids = self.get_existing_ids(entries)
        if id not in existing_ids:
            raise ValueError(f"Entry with ID '{id}' not found.")
        entries = [entry for entry in entries if entry.id != id]
        self.save_entries(entries)
