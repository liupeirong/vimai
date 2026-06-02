"""Unit tests for vimai.cli (F01, F03)."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.cli import main
from vimai.config import ConfigError


class TestCliMain:
    def test_prints_unicode_response_to_stdout(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "arrows"])

        with (
            patch("vimai.cli.load_config"),
            patch("vimai.cli.invoke_chain", return_value="use → and ← to navigate"),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        assert "→" in capsys.readouterr().out

    def test_exits_0_on_success(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "hello"])

        with (
            patch("vimai.cli.load_config"),
            patch("vimai.cli.invoke_chain", return_value="world"),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "world"

    def test_prints_response_to_stdout(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "what is vim?"])

        with (
            patch("vimai.cli.load_config"),
            patch("vimai.cli.invoke_chain", return_value="Vim is a text editor."),
            pytest.raises(SystemExit),
        ):
            main()

        out = capsys.readouterr().out.strip()
        assert out == "Vim is a text editor."

    def test_exits_1_on_config_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "hello"])

        with (
            patch(
                "vimai.cli.load_config",
                side_effect=ConfigError("Missing AZURE_OPENAI_ENDPOINT"),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
        assert "config error" in capsys.readouterr().err.lower()

    def test_exits_1_on_llm_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "hello"])

        with (
            patch("vimai.cli.load_config"),
            patch(
                "vimai.cli.invoke_chain",
                side_effect=RuntimeError("network error"),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
        assert "vimai error" in capsys.readouterr().err.lower()

    def test_exits_1_with_no_args(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        assert "usage" in capsys.readouterr().err.lower()

    def test_exits_1_with_blank_prompt(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "   "])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


class TestCliSessionFlag:
    def test_with_session_calls_invoke_chain_with_history(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        session = tmp_path / "s.tmp"
        monkeypatch.setattr(sys, "argv", ["vimai", "--session", str(session), "hello"])

        with (
            patch("vimai.cli.load_config"),
            patch(
                "vimai.cli.invoke_chain_with_history", return_value="hi"
            ) as mock_hist,
            patch("vimai.cli.invoke_chain") as mock_single,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_hist.assert_called_once()
        mock_single.assert_not_called()
        assert capsys.readouterr().out.strip() == "hi"

    def test_without_session_calls_invoke_chain(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "hello"])

        with (
            patch("vimai.cli.load_config"),
            patch("vimai.cli.invoke_chain", return_value="world") as mock_single,
            patch("vimai.cli.invoke_chain_with_history") as mock_hist,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_single.assert_called_once()
        mock_hist.assert_not_called()

    def test_session_path_passed_as_path_object(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        session = tmp_path / "s.tmp"
        monkeypatch.setattr(sys, "argv", ["vimai", "--session", str(session), "hello"])

        with (
            patch("vimai.cli.load_config"),
            patch(
                "vimai.cli.invoke_chain_with_history", return_value="ok"
            ) as mock_hist,
            pytest.raises(SystemExit),
        ):
            main()

        _, kwargs = mock_hist.call_args
        # second positional arg is session_path
        call_args = mock_hist.call_args[0]
        assert isinstance(call_args[1], Path)
        assert call_args[1] == session
