"""Session management for vimai (F03).

A session is a JSON file persisted to the system temp directory.
Each entry records one message turn: {"role", "content", "timestamp"}.

The session file is written after every turn, so it survives Vim exit
without a separate flush step.
"""

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class SessionEntry:
    """A single message turn in a session."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "SessionEntry":
        return cls(
            role=data["role"], content=data["content"], timestamp=data["timestamp"]
        )


def new_session_path(tmpdir: str | None = None) -> Path:
    """Return a new unique session file path (file is not created).

    Pattern: vimai-session-YYYY-MM-DD-HH-MM-<pid>.tmp
    """
    base = Path(tmpdir) if tmpdir else Path(tempfile.gettempdir())
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d-%H-%M")
    pid = os.getpid()
    return base / f"vimai-session-{now}-{pid}.tmp"


def load_session(path: Path | str) -> list[SessionEntry]:
    """Load session entries from a JSON file.

    Returns an empty list if the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        raw: list[dict[str, str]] = json.load(f)
    return [SessionEntry.from_dict(entry) for entry in raw]


def save_session(path: Path | str, entries: list[SessionEntry]) -> None:
    """Write session entries to a JSON file, creating or overwriting it."""
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)
