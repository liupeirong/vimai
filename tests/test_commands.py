"""Unit tests for F04 slash-command handlers (commands.py)."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.commands import (
    HELP_TEXT,
    cmd_clear,
    cmd_help,
    cmd_purge,
    handle_command,
)


# ── cmd_clear ────────────────────────────────────────────────────────────────


def test_clear_deletes_existing_file(tmp_path):
    session = tmp_path / "vimai-session-test.tmp"
    session.write_text("[]")
    result = cmd_clear(session)
    assert result == "Session cleared."
    assert not session.exists()


def test_clear_no_session_path():
    result = cmd_clear(None)
    assert result == "No active session to clear."


def test_clear_missing_file(tmp_path):
    session = tmp_path / "nonexistent.tmp"
    result = cmd_clear(session)
    assert result == "No active session to clear."


# ── cmd_purge ────────────────────────────────────────────────────────────────


def test_purge_deletes_all_session_files(tmp_path):
    for i in range(3):
        (tmp_path / f"vimai-session-2026-01-01-12-0{i}-999.tmp").write_text("[]")
    # Add a non-session file to verify it is not deleted.
    other = tmp_path / "other.txt"
    other.write_text("keep me")

    result = cmd_purge(str(tmp_path))
    assert result == "Purged 3 session files."
    assert other.exists()
    remaining = list(tmp_path.glob("vimai-session-*.tmp"))
    assert remaining == []


def test_purge_single_file_uses_singular(tmp_path):
    (tmp_path / "vimai-session-2026-01-01-12-00-1.tmp").write_text("[]")
    result = cmd_purge(str(tmp_path))
    assert result == "Purged 1 session file."


def test_purge_no_files(tmp_path):
    result = cmd_purge(str(tmp_path))
    assert result == "No session files found."


def test_purge_defaults_to_system_tmpdir(monkeypatch, tmp_path):
    """cmd_purge() with no argument uses tempfile.gettempdir()."""
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    (tmp_path / "vimai-session-2026-01-01-12-00-1.tmp").write_text("[]")
    result = cmd_purge()
    assert "Purged 1" in result


# ── cmd_help ─────────────────────────────────────────────────────────────────


def test_help_contains_all_commands():
    text = cmd_help()
    assert "/clear" in text
    assert "/purge" in text
    assert "/help" in text


def test_help_returns_help_text_constant():
    assert cmd_help() == HELP_TEXT


# ── handle_command ────────────────────────────────────────────────────────────


def test_handle_clear_routes_to_cmd_clear(tmp_path):
    session = tmp_path / "s.tmp"
    session.write_text("[]")
    result = handle_command("/clear", session)
    assert result == "Session cleared."
    assert not session.exists()


def test_handle_purge_routes_to_cmd_purge(tmp_path):
    (tmp_path / "vimai-session-2026-01-01-12-00-1.tmp").write_text("[]")
    session = tmp_path / "vimai-session-2026-01-01-12-00-99.tmp"
    result = handle_command("/purge", session)
    assert "Purged" in result


def test_handle_help_routes_to_cmd_help():
    result = handle_command("/help")
    assert result == HELP_TEXT


def test_handle_command_case_insensitive():
    assert handle_command("/HELP") == HELP_TEXT
    assert handle_command("/Help") == HELP_TEXT


def test_handle_unknown_command_references_help():
    result = handle_command("/unknown")
    assert result is not None
    assert "/help" in result.lower()
    assert "unknown" in result.lower()


def test_handle_non_command_returns_none():
    assert handle_command("hello world") is None
    assert handle_command("what is vim?") is None


def test_handle_empty_string_returns_none():
    # Whitespace-only prompts are filtered in cli.main before handle_command;
    # the function itself treats them as non-commands.
    assert handle_command("   ") is None


def test_handle_purge_uses_session_parent_dir(tmp_path):
    (tmp_path / "vimai-session-2026-01-01-12-00-1.tmp").write_text("[]")
    session = tmp_path / "vimai-session-current.tmp"
    result = handle_command("/purge", session)
    assert "Purged" in result
