from dataclasses import dataclass, field
from datetime import datetime
from typing import Final, List
from uuid import uuid4

MAX_TITLE_LENGHT: Final[int] = 50
MAX_CONTENT_LENGHT: Final[int] = 200
DASH_LENGTH: Final[int] = 80


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
