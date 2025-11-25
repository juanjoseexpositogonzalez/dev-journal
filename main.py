import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    title: str
    content: str
    date: datetime  # ISO format date string


def load_entries():
    """Load journal entries from the JSON file."""
    with DB_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [JournalEntry(**entry) for entry in data]
        except json.JSONDecodeError:
            return []


def save_entries(entries):
    """Save journal entries to the JSON file."""
    for entry in entries:
        entry.date = entry.date.isoformat()  # Convert datetime to ISO string
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(entry) for entry in entries], f, indent=4)


def add_entry(title, content):
    """Create a new journal entry and save it to the JSON file."""
    journal_entry = JournalEntry(
        title=title, content=content, date=datetime.now().isoformat()
    )
    with DB_FILE.open("r+", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(asdict(journal_entry))
        f.seek(0)
        json.dump(data, f, indent=4)


def list_entries(entries):
    """Print all journal entries to the console."""
    for entry in entries:
        print(
            f"📅 {datetime.fromisoformat(entry.date).strftime('%a %d %b %Y, %I:%M%p')}\n📝 {entry.title}\n{entry.content}\n{'-'*40}"
        )


if __name__ == "__main__":
    # quick interactive program (entry point) to validate the above
    title = input("Title: ")
    content = input("Content: ")
    add_entry(title, content)
    print("✅ Entry saved.")
    print("\n📘 Your Journal:")
    list_entries(load_entries())
