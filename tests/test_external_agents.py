"""Unit tests for external agent command runners (F09)."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.agents import ExternalAgentError, invoke_external_agent


class TestInvokeExternalAgent:
    def test_discovers_run_agent_wrapper(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        wrapper = agents_dir / "git" / "run-agent"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("#!/bin/sh\n", encoding="utf-8")

        with patch("vimai.agents.external.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="ok", stderr=""
            )
            invoke_external_agent(agents_dir, "git", "status")

        assert mock_run.call_args[0][0][0] == str(wrapper)

    def test_discovers_windows_bat_wrapper(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        wrapper = agents_dir / "git" / "run-agent.bat"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("@echo off\n", encoding="utf-8")

        with (
            patch("vimai.agents.external.os.name", "nt"),
            patch("vimai.agents.external.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="ok", stderr=""
            )
            invoke_external_agent(agents_dir, "git", "status")

        assert mock_run.call_args[0][0][0] == str(wrapper)

    def test_prefers_extensionless_wrapper_on_windows(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        agent_dir = agents_dir / "git"
        agent_dir.mkdir(parents=True)
        preferred = agent_dir / "run-agent"
        preferred.write_text("#!/bin/sh\n", encoding="utf-8")
        (agent_dir / "run-agent.bat").write_text("@echo off\n", encoding="utf-8")

        with (
            patch("vimai.agents.external.os.name", "nt"),
            patch("vimai.agents.external.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="ok", stderr=""
            )
            invoke_external_agent(agents_dir, "git", "status")

        assert mock_run.call_args[0][0][0] == str(preferred)

    def test_passes_prompt_via_utf8_prompt_file(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        wrapper = agents_dir / "git" / "run-agent"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("#!/bin/sh\n", encoding="utf-8")
        prompt_paths: list[Path] = []
        prompt_contents: list[str] = []

        def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
            prompt_path = Path(args[args.index("--prompt-file") + 1])
            prompt_paths.append(prompt_path)
            prompt_contents.append(prompt_path.read_text(encoding="utf-8"))
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="answer", stderr=""
            )

        with patch("vimai.agents.external.subprocess.run", side_effect=fake_run):
            result = invoke_external_agent(agents_dir, "git", "line one\nline two")

        assert result == "answer"
        assert prompt_contents == ["line one\nline two"]
        assert prompt_paths
        assert not prompt_paths[0].exists()

    def test_captures_stdout_and_stderr(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        wrapper = agents_dir / "git" / "run-agent"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("#!/bin/sh\n", encoding="utf-8")

        with patch("vimai.agents.external.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="stdout\n", stderr="stderr\n"
            )
            result = invoke_external_agent(agents_dir, "git", "status")

        assert result == "stdout\nstderr"

    def test_non_zero_exit_is_user_visible(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "external-agents"
        wrapper = agents_dir / "git" / "run-agent"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("#!/bin/sh\n", encoding="utf-8")

        with patch("vimai.agents.external.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=2, stdout="", stderr="bad args"
            )

            with pytest.raises(ExternalAgentError) as exc_info:
                invoke_external_agent(agents_dir, "git", "status")

        assert "exited with code 2" in str(exc_info.value)
        assert "bad args" in str(exc_info.value)

    def test_missing_wrapper_has_clear_error(self, tmp_path: Path) -> None:
        with pytest.raises(ExternalAgentError) as exc_info:
            invoke_external_agent(tmp_path, "missing", "hello")

        assert "run-agent wrapper" in str(exc_info.value)
        assert str(tmp_path / "missing" / "run-agent") in str(exc_info.value)
