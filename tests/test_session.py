"""Unit tests for vimai.session (F03)."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.session import SessionEntry, load_session, new_session_path, save_session


class TestNewSessionPath:
    def test_path_is_under_tmpdir(self, tmp_path: Path) -> None:
        p = new_session_path(str(tmp_path))
        assert p.parent == tmp_path

    def test_path_matches_naming_pattern(self, tmp_path: Path) -> None:
        p = new_session_path(str(tmp_path))
        assert re.match(
            r"vimai-session-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d+\.tmp",
            p.name,
        )

    def test_path_uses_system_tmpdir_when_not_specified(self) -> None:
        import tempfile

        p = new_session_path()
        assert p.parent == Path(tempfile.gettempdir())

    def test_path_is_not_created(self, tmp_path: Path) -> None:
        p = new_session_path(str(tmp_path))
        assert not p.exists()


class TestLoadSession:
    def test_returns_empty_list_for_missing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "no-such-file.tmp"
        assert load_session(p) == []

    def test_loads_entries_from_json_file(self, tmp_path: Path) -> None:
        data = [
            {
                "role": "user",
                "content": "hello",
                "timestamp": "2026-01-01T00:00:00+00:00",
            },
            {
                "role": "assistant",
                "content": "hi",
                "timestamp": "2026-01-01T00:00:01+00:00",
            },
        ]
        p = tmp_path / "session.tmp"
        p.write_text(json.dumps(data), encoding="utf-8")

        entries = load_session(p)

        assert len(entries) == 2
        assert entries[0].role == "user"
        assert entries[0].content == "hello"
        assert entries[1].role == "assistant"
        assert entries[1].content == "hi"

    def test_accepts_str_path(self, tmp_path: Path) -> None:
        p = tmp_path / "session.tmp"
        p.write_text(json.dumps([]), encoding="utf-8")
        assert load_session(str(p)) == []


class TestSaveSession:
    def test_creates_file_with_entries(self, tmp_path: Path) -> None:
        p = tmp_path / "session.tmp"
        entries = [SessionEntry("user", "test prompt", "2026-01-01T00:00:00+00:00")]
        save_session(p, entries)

        assert p.exists()
        raw = json.loads(p.read_text(encoding="utf-8"))
        assert raw == [
            {
                "role": "user",
                "content": "test prompt",
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        ]

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "session.tmp"
        p.write_text(
            json.dumps([{"role": "user", "content": "old", "timestamp": "x"}]),
            encoding="utf-8",
        )

        save_session(p, [SessionEntry("assistant", "new", "y")])

        raw = json.loads(p.read_text(encoding="utf-8"))
        assert len(raw) == 1
        assert raw[0]["content"] == "new"

    def test_roundtrip_preserves_all_fields(self, tmp_path: Path) -> None:
        p = tmp_path / "session.tmp"
        original = [
            SessionEntry("user", "q1", "ts1"),
            SessionEntry("assistant", "a1", "ts2"),
        ]
        save_session(p, original)
        loaded = load_session(p)

        assert loaded == original

    def test_accepts_str_path(self, tmp_path: Path) -> None:
        p = tmp_path / "session.tmp"
        save_session(str(p), [])
        assert p.exists()


class TestSessionEntryFromDict:
    def test_from_dict_populates_fields(self) -> None:
        data = {"role": "user", "content": "hello", "timestamp": "ts"}
        entry = SessionEntry.from_dict(data)
        assert entry.role == "user"
        assert entry.content == "hello"
        assert entry.timestamp == "ts"

    def test_to_dict_roundtrip(self) -> None:
        entry = SessionEntry("assistant", "response", "2026-01-01T00:00:00+00:00")
        assert entry.to_dict() == {
            "role": "assistant",
            "content": "response",
            "timestamp": "2026-01-01T00:00:00+00:00",
        }
