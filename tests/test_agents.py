"""Unit tests for generic agent prompt loading (F07)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.agents import AgentNotFoundError, load_agent


class TestLoadAgent:
    def test_reads_user_agent_markdown_as_system_prompt(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "git.md").write_text("You are a Git expert.\n", encoding="utf-8")

        agent = load_agent("git", user_agents_dir=agents_dir)

        assert agent.name == "git"
        assert agent.system_prompt == "You are a Git expert."
        assert agent.source_path == agents_dir / "git.md"
        assert agent.is_builtin is False

    def test_accepts_name_with_leading_at_sign(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "git.md").write_text("Git prompt", encoding="utf-8")

        agent = load_agent("@git", user_agents_dir=agents_dir)

        assert agent.name == "git"
        assert agent.system_prompt == "Git prompt"

    def test_builtin_vi_agent_loads_when_user_file_absent(self, tmp_path: Path) -> None:
        agent = load_agent("vi", user_agents_dir=tmp_path / "missing")

        assert agent.name == "vi"
        assert "Vim expert" in agent.system_prompt
        assert agent.source_path is None
        assert agent.is_builtin is True

    def test_user_agent_overrides_builtin_vi(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "vi.md").write_text("Custom Vim prompt", encoding="utf-8")

        agent = load_agent("vi", user_agents_dir=agents_dir)

        assert agent.system_prompt == "Custom Vim prompt"
        assert agent.source_path == agents_dir / "vi.md"
        assert agent.is_builtin is False

    def test_missing_agent_has_creation_hint(self, tmp_path: Path) -> None:
        with pytest.raises(AgentNotFoundError) as exc_info:
            load_agent("missing", user_agents_dir=tmp_path)

        assert str(exc_info.value) == (
            "No agent found for @missing. Create ~/.vimai/agents/missing.md"
        )

    @pytest.mark.parametrize("name", ["", "   ", "../vi", "vim/help", "vim.help"])
    def test_rejects_invalid_agent_names(self, name: str, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            load_agent(name, user_agents_dir=tmp_path)
