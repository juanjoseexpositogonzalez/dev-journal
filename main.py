import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, List, Sized

import typer
from typing_extensions import Annotated

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)
DASH_LENTGH: Final[int] = 80
MAX_TITLE_LENGHT: Final[int] = 50
MAX_CONTENT_LENGHT: Final[int] = 200

app = typer.Typer()


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    title: str
    content: str
    tags: str
    date: datetime

    def __post_init__(self):
        if len(self.title) > MAX_TITLE_LENGHT:
            raise ValueError(f"Title cannot exceed {MAX_TITLE_LENGHT} characters.")
        if len(self.content) > MAX_CONTENT_LENGHT:
            raise ValueError(f"Content cannot exceed {MAX_CONTENT_LENGHT} characters.")

    @property
    def summary(self) -> str:
        """Return a formatted string representation of the journal entry."""
        date = self.date
        title = self.title.upper()
        content = self.content
        tags = self.tags if self.tags != "" else "No tags"
        return f"{'-'*DASH_LENTGH}\n📝 {title}. -- 📅 {date}\nTags: {tags}\n{'-'*DASH_LENTGH}\n{content}"


def load_entries() -> Sized[JournalEntry]:
    """Load journal entries from the JSON file."""
    with DB_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [JournalEntry(**entry) for entry in data]
        except json.JSONDecodeError:
            return []


def save_entries(entries: Sized[JournalEntry]) -> None:
    """Save journal entries to the JSON file."""
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(entry) for entry in entries], f, indent=4)


def add_entry(title: str, content: str, tags: str = "") -> None:
    """Create a new journal entry and save it to the JSON file."""
    entries = load_entries()
    journal_entry = JournalEntry(
        title=title, content=content, date=datetime.now().isoformat(), tags=tags
    )
    entries.append(journal_entry)
    save_entries(entries)


def list_entries(entries: Sized[JournalEntry]) -> None:
    """Print all journal entries to the console."""
    for entry in entries:
        print(entry.summary)
    print(f"{'-'*DASH_LENTGH}\nTotal entries: {len(entries)}")


@app.command()
def add(
    title: Annotated[str, typer.Argument(..., help="Title of the journal entry")],
    content: Annotated[str, typer.Argument(..., help="Content of the journal entry")],
    tags: Annotated[List[str], typer.Option(help="Tags (comma separated)")] = None,
) -> None:
    """Add a new journal entry."""
    try:
        add_entry(title, content, tags)
    except ValueError as e:
        typer.echo(f"❌ Failed to add journal entry. Reason: {e}")
    else:
        typer.echo("🔥 Journal entry saved.")


@app.command()
def list() -> None:
    """List all journal entries."""
    entries = load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return
    list_entries(entries)


@app.command()
def populate() -> None:
    """Populate the journal with predefined entries."""
    from populate_dev_journal import CONTENTS, TAGS, TITLES

    for title, content, tags in zip(TITLES, CONTENTS, TAGS):
        try:
            add_entry(title, content, tags)
        except ValueError as e:
            typer.echo(f"❌ Failed to add journal entry '{title}'. Reason: {e}")
        else:
            typer.echo(f"🔥 Journal entry '{title}' saved.")


if __name__ == "__main__":
    app()
