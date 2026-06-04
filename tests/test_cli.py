"""Unit tests for vimai.cli (F01, F03, F04, F08)."""

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


class TestCliPromptFile:
    def test_prompt_file_reads_multiline_prompt(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("line one\nline two\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["vimai", "--prompt-file", str(prompt_file)])

        with (
            patch("vimai.cli.load_config"),
            patch("vimai.cli.invoke_chain", return_value="answer") as mock_chain,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_chain.assert_called_once()
        assert mock_chain.call_args[0][1] == "line one\nline two"
        assert capsys.readouterr().out.strip() == "answer"

    def test_prompt_file_errors_are_user_visible(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        missing_prompt = tmp_path / "does-not-exist.txt"
        monkeypatch.setattr(
            sys,
            "argv",
            ["vimai", "--prompt-file", str(missing_prompt)],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        assert "vimai error" in capsys.readouterr().err.lower()


class TestCliSlashCommands:
    """F04: slash commands are dispatched before any LLM call."""

    def test_clear_exits_0_and_keeps_session_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        session = tmp_path / "vimai-session-test.tmp"
        session.write_text("[]")
        monkeypatch.setattr(sys, "argv", ["vimai", "--session", str(session), "/clear"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert "cleared" in capsys.readouterr().out.lower()
        # Session file must be preserved; /purge is responsible for deletion.
        assert session.exists()

    def test_purge_exits_0_and_deletes_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        for i in range(2):
            (tmp_path / f"vimai-session-2026-01-01-12-0{i}-1.tmp").write_text("[]")
        session = tmp_path / "vimai-session-current.tmp"
        monkeypatch.setattr(sys, "argv", ["vimai", "--session", str(session), "/purge"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "purged" in out.lower()
        assert not any(tmp_path.glob("vimai-session-*.tmp"))

    def test_help_exits_0_and_prints_commands(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "/help"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "/clear" in out
        assert "/purge" in out
        assert "/help" in out

    def test_slash_commands_skip_llm(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "/help"])

        with (
            patch("vimai.cli.load_config") as mock_config,
            patch("vimai.cli.invoke_chain") as mock_chain,
            pytest.raises(SystemExit),
        ):
            main()

        mock_config.assert_not_called()
        mock_chain.assert_not_called()

    def test_unknown_slash_command_exits_0_with_error_hint(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "/oops"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "/help" in out.lower()


class TestCliCommandFlag:
    """F04 (fix): --command flag used by Vim plugin to bypass MSYS2 path conversion."""

    def test_command_help(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "--command", "help"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "/clear" in out
        assert "/purge" in out
        assert "/help" in out

    def test_command_clear(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        session = tmp_path / "vimai-session-test.tmp"
        session.write_text("[]")
        monkeypatch.setattr(
            sys, "argv", ["vimai", "--command", "clear", "--session", str(session)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert "cleared" in capsys.readouterr().out.lower()
        # Session file must be preserved; /purge is responsible for deletion.
        assert session.exists()

    def test_command_purge(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        tmp_path: Path,
    ) -> None:
        for i in range(2):
            (tmp_path / f"vimai-session-2026-01-01-12-0{i}-1.tmp").write_text("[]")
        session = tmp_path / "vimai-session-current.tmp"
        monkeypatch.setattr(
            sys, "argv", ["vimai", "--command", "purge", "--session", str(session)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert "purged" in capsys.readouterr().out.lower()

    def test_command_skips_llm(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "--command", "help"])

        with (
            patch("vimai.cli.load_config") as mock_config,
            patch("vimai.cli.invoke_chain") as mock_chain,
            pytest.raises(SystemExit),
        ):
            main()

        mock_config.assert_not_called()
        mock_chain.assert_not_called()

    def test_unknown_command_flag_exits_0_with_hint(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "--command", "oops"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert "/help" in capsys.readouterr().out.lower()


class TestCliAgentRouting:
    """F08: leading @agent prompts are stateless single-turn agent calls."""

    def test_agent_prompt_calls_invoke_agent(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "@vi explain :global"])

        with (
            patch("vimai.cli.load_config", return_value="config") as mock_config,
            patch("vimai.cli.invoke_agent", return_value="agent answer") as mock_agent,
            patch("vimai.cli.invoke_chain") as mock_chain,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_config.assert_called_once()
        mock_agent.assert_called_once_with("config", "vi", "explain :global")
        mock_chain.assert_not_called()
        assert capsys.readouterr().out.strip() == "agent answer"

    def test_agent_prompt_with_session_skips_history(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        session = tmp_path / "vimai-session-test.tmp"
        monkeypatch.setattr(
            sys,
            "argv",
            ["vimai", "--session", str(session), "@git summarize status"],
        )

        with (
            patch("vimai.cli.load_config", return_value="config"),
            patch("vimai.cli.invoke_agent", return_value="ok") as mock_agent,
            patch("vimai.cli.invoke_chain_with_history") as mock_history,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_agent.assert_called_once_with("config", "git", "summarize status")
        mock_history.assert_not_called()
        assert not session.exists()

    def test_agent_prompt_file_reads_prompt_after_agent_name(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        prompt_file = tmp_path / "agent-prompt.txt"
        prompt_file.write_text(
            "@vi\nexplain registers\nwith examples", encoding="utf-8"
        )
        monkeypatch.setattr(sys, "argv", ["vimai", "--prompt-file", str(prompt_file)])

        with (
            patch("vimai.cli.load_config", return_value="config"),
            patch("vimai.cli.invoke_agent", return_value="ok") as mock_agent,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_agent.assert_called_once_with(
            "config", "vi", "explain registers\nwith examples"
        )

    def test_agent_prompt_without_body_prints_usage(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["vimai", "@vi"])

        with (
            patch("vimai.cli.load_config") as mock_config,
            patch("vimai.cli.invoke_agent") as mock_agent,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
        mock_config.assert_not_called()
        mock_agent.assert_not_called()
        assert "@<agent> <prompt>" in capsys.readouterr().err
