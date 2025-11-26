import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    title: str
    content: str
    date: datetime

    @property
    def summary(self) -> str:
        """Return a formatted string representation of the journal entry."""
        return f"📅 {datetime.fromisoformat(self.date).strftime('%a %d %b %Y, %I:%M%p')}\n📝 {self.title}\n{self.content}\n{'-'*40}"


def load_entries() -> List[JournalEntry]:
    """Load journal entries from the JSON file."""
    with DB_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [JournalEntry(**entry) for entry in data]
        except json.JSONDecodeError:
            return []


def save_entries(entries: Iterable[JournalEntry]) -> None:
    """Save journal entries to the JSON file."""
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(entry) for entry in entries], f, indent=4)


def add_entry(title: str, content: str) -> None:
    """Create a new journal entry and save it to the JSON file."""
    entries = load_entries()
    journal_entry = JournalEntry(
        title=title, content=content, date=datetime.now().isoformat()
    )
    entries.append(journal_entry)
    save_entries(entries)


def list_entries(entries: Iterable[JournalEntry]) -> None:
    """Print all journal entries to the console."""
    for entry in entries:
        print(entry.summary)


if __name__ == "__main__":
    # quick interactive program (entry point) to validate the above
    title = input("Title: ")
    content = input("Content: ")
    add_entry(title, content)
    print("✅ Entry saved.")
    print("\n📘 Your Journal:")
    list_entries(load_entries())
