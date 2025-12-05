from pathlib import Path
from typing import List

import typer
from db import JournalDatabase
from models import JournalEntry
from typing_extensions import Annotated

db = JournalDatabase(Path("journal.json"))

app = typer.Typer()


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
        db.add_entry(title, content, tags)
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
    entries = db.load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return

    if tag:
        # Filtrar por múltiples tags (AND logic: todas las entradas deben tener todos los tags)
        filtered_entries: List[JournalEntry] | None = db.search_entries_by_tags(tag)
        if filtered_entries:
            typer.echo(
                f"🔍 Found {len(filtered_entries)} entries with tags: {', '.join(tag)}"
            )
            db.list_entries()
        else:
            typer.echo(f"❌ No journal entries found with tags: {', '.join(tag)}")
    else:
        db.list_entries()


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
    entries = db.load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return
    db.search_entries(query, tags=tags)


@app.command()
def stats() -> None:
    """Show statistics about the journal."""
    entries = db.load_entries()
    if not entries:
        typer.echo("❌ No journal entries found.")
        return
    typer.echo(f"Total entries: {len(entries)}")
    typer.echo(
        f"Total tags: {len(set([tag for entry in entries for tag in entry.tags]))}"
    )
    typer.echo(f"Most common tag: {db.most_common_tag(entries)}")
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
        db.delete_entry(id)
    except ValueError as e:
        typer.echo(f"❌ Failed to delete journal entry. Reason: {e}")
    else:
        typer.echo(f"🔥 Journal entry '{id}' deleted.")
