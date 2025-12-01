import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path
from typing import Final, List
from uuid import uuid4

import typer
from typing_extensions import Annotated

DB_FILE = Path("journal.json")
DB_FILE.touch(exist_ok=True)
DASH_LENGTH: Final[int] = 80
MAX_TITLE_LENGHT: Final[int] = 50
MAX_CONTENT_LENGHT: Final[int] = 200
CLOSE_MATCH_CUTOFF: Final[float] = 0.5
CLOSE_MATCH_MAX_RESULTS: Final[int] = 10

LINE_SEPARATOR: Final[str] = "-" * DASH_LENGTH
LINE_SEPARATOR_DOUBLE: Final[str] = "=" * DASH_LENGTH


app = typer.Typer()


# 📝 Define a JournalEntry class with title, content, and date
@dataclass
class JournalEntry:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = field(default="")
    content: str = field(default="")
    date: str = field(default=datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

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
        tags = ", ".join(self.tags) if self.tags else "No tags"
        return f"{'-'*DASH_LENGTH}\n📝 {title}. -- 📅 {date}\nTags: {tags}\n{'-'*DASH_LENGTH}\n{content}"


def load_entries() -> List[JournalEntry]:
    """Load journal entries from the JSON file."""
    entries: List[JournalEntry] = []
    with DB_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [JournalEntry(**entry) for entry in data]
        except json.JSONDecodeError:
            return entries


def save_entries(entries: List[JournalEntry]) -> None:
    """Save journal entries to the JSON file."""
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(entry) for entry in entries], f, indent=4)


def get_existing_ids(entries: List[JournalEntry]) -> List[str]:
    """Get all existing IDs from the journal entries."""
    return [entry.id for entry in entries]


def add_entry(title: str, content: str, tags: List[str] | None = None) -> None:
    """Create a new journal entry and save it to the JSON file."""
    entries = load_entries()
    existing_ids = get_existing_ids(entries)
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
    save_entries(entries)


def list_entries(entries: List[JournalEntry]) -> None:
    """Print all journal entries to the console."""
    for entry in entries:
        print(entry.summary)
    print(f"{'-'*DASH_LENGTH}\nTotal entries: {len(entries)}")


def search_entries_by_tags(
    entries: List[JournalEntry], tags: List[str]
) -> List[JournalEntry]:
    """Filter entries that contain all specified tags."""
    if not tags:
        return entries

    # Normalizar tags a minúsculas para comparación case-insensitive
    tags_lower = [tag.lower().strip() for tag in tags]

    # Filtrar entradas que contengan TODOS los tags especificados
    filtered: List[JournalEntry] = []
    for entry in entries:
        entry_tags_lower = [t.lower() for t in entry.tags]
        if any(tag in entry_tags_lower for tag in tags_lower):
            filtered.append(entry)  # type: ignore

    return filtered


def search_entries(entries: List[JournalEntry], query: str, tags: bool = False) -> None:
    """Search for journal entries by title or content."""
    if tags:
        # Buscar por tags
        found_entries = [
            entry
            for entry in entries
            if query.lower() in [t.lower() for t in entry.tags]
        ]
        if found_entries:
            typer.echo(f"\n{LINE_SEPARATOR_DOUBLE}")
            typer.echo(f"🔍 Found entries with tag '{query}'")
            list_entries(found_entries)
            typer.echo(f"{LINE_SEPARATOR_DOUBLE}")
        else:
            typer.echo(f"❌ No journal entries found with tag '{query}'")
    else:
        # Buscar por título
        # found_entries = [
        #     entry for entry in entries if query.lower() in entry.title.lower()
        # ]
        found_entries = get_close_matches(
            query,
            [entry.title for entry in entries],
            n=CLOSE_MATCH_MAX_RESULTS,
            cutoff=CLOSE_MATCH_CUTOFF,
        )
        if found_entries:
            typer.echo(f"\n{LINE_SEPARATOR_DOUBLE}")
            typer.echo(
                f"🔍 Found entries with title '{query}': {', '.join(found_entries)}"
            )
            typer.echo(f"{LINE_SEPARATOR_DOUBLE}")
        else:
            typer.echo(f"❌ No journal entries found with title '{query}'")


def most_common_tag(entries: List[JournalEntry]) -> str:
    """Return the most common tag in the journal."""
    return Counter(tag for entry in entries for tag in entry.tags).most_common(1)[0][0]


def delete_entry(id: str) -> None:
    """Delete a journal entry by ID."""
    entries = load_entries()
    existing_ids = get_existing_ids(entries)
    if id not in existing_ids:
        raise ValueError(f"Entry with ID '{id}' not found.")
    entries = [entry for entry in entries if entry.id != id]
    save_entries(entries)


@app.command()
def add(
    title: Annotated[str, typer.Argument(..., help="Title of the journal entry")],
    content: Annotated[str, typer.Argument(..., help="Content of the journal entry")],
    tags: Annotated[
        List[str] | None, typer.Option("--tags", help="Tags (comma separated)")
    ] = [],
) -> None:
    """Add a new journal entry."""
    try:
        add_entry(title, content, tags)
    except ValueError as e:
        typer.echo(f"❌ Failed to add journal entry. Reason: {e}")


@app.command()
def list(
    tag: Annotated[
        List[str] | None,
        typer.Option(
            "--tag", help="Filter entries by tags (can be used multiple times)"
        ),
    ] = None,
) -> None:
    """List all journal entries, optionally filtered by tags."""
    entries = load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return

    if tag:
        # Filtrar por múltiples tags (AND logic: todas las entradas deben tener todos los tags)
        filtered_entries = search_entries_by_tags(entries, tag)
        if filtered_entries:
            typer.echo(
                f"🔍 Found {len(filtered_entries)} entries with tags: {', '.join(tag)}"
            )
            list_entries(filtered_entries)
        else:
            typer.echo(f"❌ No journal entries found with tags: {', '.join(tag)}")
    else:
        list_entries(entries)


@app.command()
def populate() -> None:
    """Populate the journal with predefined entries."""
    from populate_dev_journal import CONTENTS, TAGS, TITLES

    for title, content, tags in zip(TITLES, CONTENTS, TAGS, strict=True):  # type: ignore
        try:
            add(title, content, tags.split(",") if tags else [])
        except ValueError as e:
            typer.echo(f"❌ Failed to add journal entry '{title}'. Reason: {e}")
        else:
            typer.echo(f"🔥 Journal entry '{title}' saved.")


@app.command()
def search(
    query: Annotated[str, typer.Argument(..., help="Search query")],
    tags: Annotated[bool, typer.Option("--tags", help="Search in tags")] = False,
) -> None:
    """Search for journal entries by title or content."""
    entries = load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return
    search_entries(entries, query, tags=tags)


@app.command()
def stats() -> None:
    """Show statistics about the journal."""
    entries = load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return
    typer.echo(f"Total entries: {len(entries)}")
    typer.echo(
        f"Total tags: {len(set([tag for entry in entries for tag in entry.tags]))}"
    )
    typer.echo(f"Most common tag: {most_common_tag(entries)}")
    typer.echo(f"Total words: {sum([len(entry.content.split()) for entry in entries])}")
    typer.echo(
        f"Average words per entry: {sum([len(entry.content.split()) for entry in entries]) / len(entries)}"
    )


@app.command()
def delete(
    id: Annotated[str, typer.Argument(..., help="ID of the journal entry to delete")],
) -> None:
    """Delete a journal entry by ID."""
    try:
        delete_entry(id)
    except ValueError as e:
        typer.echo(f"❌ Failed to delete journal entry. Reason: {e}")
    else:
        typer.echo(f"🔥 Journal entry '{id}' deleted.")


if __name__ == "__main__":
    app()
