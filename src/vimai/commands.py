"""Slash-command handlers for F04 (/clear, /purge, /help).

These commands are dispatched from cli.main() before any LLM call is made.
Each handler returns a plain-text string that cli.main() prints to stdout.
"""

import glob
import os
import tempfile
from pathlib import Path

HELP_TEXT = """\
vimai commands:
  /clear   End the current session (deletes the session file)
  /purge   Delete all vimai session files from the system temp directory
  /help    Show this help message
  <prompt> Send a prompt to the LLM"""


def cmd_clear(session_path: Path | None) -> str:
    """Delete the active session file and return a confirmation message."""
    if session_path is None or not session_path.exists():
        return "No active session to clear."
    session_path.unlink()
    return "Session cleared."


def cmd_purge(tmpdir: str | None = None) -> str:
    """Delete all vimai-session-*.tmp files from tmpdir (default: system temp)."""
    base = tmpdir or tempfile.gettempdir()
    pattern = os.path.join(base, "vimai-session-*.tmp")
    files = glob.glob(pattern)
    deleted = 0
    for f in files:
        try:
            os.unlink(f)
            deleted += 1
        except OSError:
            pass
    if deleted == 0:
        return "No session files found."
    noun = "file" if deleted == 1 else "files"
    return f"Purged {deleted} session {noun}."


def cmd_help() -> str:
    """Return the help text listing all slash commands."""
    return HELP_TEXT


def handle_command(prompt: str, session_path: Path | None = None) -> str | None:
    """If prompt is a slash command, handle it and return output string.

    Returns None if the prompt is not a slash command (normal LLM prompt).
    Unknown slash commands return an error message referencing /help.
    """
    stripped = prompt.strip()
    if not stripped.startswith("/"):
        return None

    cmd = stripped.split()[0].lower()

    if cmd == "/clear":
        return cmd_clear(session_path)
    if cmd == "/purge":
        return cmd_purge(str(session_path.parent) if session_path else None)
    if cmd == "/help":
        return cmd_help()

    return f"Unknown command: {stripped}. Type /help for available commands."
