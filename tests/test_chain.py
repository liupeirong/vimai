"""Unit tests for vimai.chain (F01, F03, F07)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.chain import invoke_agent, invoke_chain, invoke_chain_with_history
from vimai.config import Config


@pytest.fixture()
def config() -> Config:
    return Config(
        endpoint="https://my.openai.azure.com/",
        deployment="gpt-4o",
        api_version="2024-05-01-preview",
    )


class TestInvokeChain:
    def test_returns_response_string(self, config: Config) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Hello from LLM")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            result = invoke_chain(config, "hello")

        assert result == "Hello from LLM"

    def test_sends_human_message_with_prompt(self, config: Config) -> None:
        from langchain_core.messages import HumanMessage

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="ok")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain(config, "what is vim?")

        args, _ = mock_llm.invoke.call_args
        messages = args[0]
        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "what is vim?"

    def test_uses_config_to_build_llm(self, config: Config) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="ok")

        with patch("vimai.chain.build_llm", return_value=mock_llm) as mock_build:
            invoke_chain(config, "hello")

        mock_build.assert_called_once_with(config)

    def test_propagates_llm_exception(self, config: Config) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = RuntimeError("Azure auth failed")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            with pytest.raises(RuntimeError, match="Azure auth failed"):
                invoke_chain(config, "hello")

    def test_content_coerced_to_string(self, config: Config) -> None:
        mock_llm = MagicMock()
        # content could be a non-string (e.g. list for multi-modal) – coerce it
        mock_llm.invoke.return_value = MagicMock(content=42)

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            result = invoke_chain(config, "hello")

        assert result == "42"


class TestInvokeChainWithHistory:
    def test_returns_response_string(self, config: Config, tmp_path: Path) -> None:
        session = tmp_path / "s.tmp"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="answer")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            result = invoke_chain_with_history(config, session, "question")

        assert result == "answer"

    def test_empty_session_sends_single_human_message(
        self, config: Config, tmp_path: Path
    ) -> None:
        from langchain_core.messages import HumanMessage

        session = tmp_path / "s.tmp"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="ok")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain_with_history(config, session, "hello")

        args, _ = mock_llm.invoke.call_args
        messages = args[0]
        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "hello"

    def test_existing_history_prepended_to_messages(
        self, config: Config, tmp_path: Path
    ) -> None:
        import json
        from langchain_core.messages import AIMessage, HumanMessage

        session = tmp_path / "s.tmp"
        session.write_text(
            json.dumps(
                [
                    {"role": "user", "content": "first", "timestamp": "t1"},
                    {"role": "assistant", "content": "reply", "timestamp": "t2"},
                ]
            ),
            encoding="utf-8",
        )

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="ok")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain_with_history(config, session, "second")

        args, _ = mock_llm.invoke.call_args
        messages = args[0]
        assert len(messages) == 3
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "first"
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "reply"
        assert isinstance(messages[2], HumanMessage)
        assert messages[2].content == "second"

    def test_saves_both_turns_to_session_file(
        self, config: Config, tmp_path: Path
    ) -> None:
        import json

        session = tmp_path / "s.tmp"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="the answer")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain_with_history(config, session, "the question")

        assert session.exists()
        raw = json.loads(session.read_text(encoding="utf-8"))
        assert len(raw) == 2
        assert raw[0]["role"] == "user"
        assert raw[0]["content"] == "the question"
        assert raw[1]["role"] == "assistant"
        assert raw[1]["content"] == "the answer"

    def test_accumulates_history_across_calls(
        self, config: Config, tmp_path: Path
    ) -> None:
        import json

        session = tmp_path / "s.tmp"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="a1")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain_with_history(config, session, "q1")

        mock_llm.invoke.return_value = MagicMock(content="a2")
        with patch("vimai.chain.build_llm", return_value=mock_llm):
            invoke_chain_with_history(config, session, "q2")

        raw = json.loads(session.read_text(encoding="utf-8"))
        assert len(raw) == 4
        assert raw[0]["content"] == "q1"
        assert raw[1]["content"] == "a1"
        assert raw[2]["content"] == "q2"
        assert raw[3]["content"] == "a2"

    def test_propagates_llm_exception(self, config: Config, tmp_path: Path) -> None:
        session = tmp_path / "s.tmp"
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = RuntimeError("network error")

        with patch("vimai.chain.build_llm", return_value=mock_llm):
            with pytest.raises(RuntimeError, match="network error"):
                invoke_chain_with_history(config, session, "hello")


class TestInvokeAgent:
    def test_sends_system_prompt_then_human_prompt(self, config: Config) -> None:
        from langchain_core.messages import HumanMessage, SystemMessage

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="agent answer")

        with (
            patch("vimai.chain.build_llm", return_value=mock_llm),
            patch("vimai.chain.load_agent") as mock_load_agent,
        ):
            mock_load_agent.return_value = MagicMock(
                system_prompt="You are a Vim expert."
            )
            result = invoke_agent(config, "vi", "explain :global")

        assert result == "agent answer"
        args, _ = mock_llm.invoke.call_args
        messages = args[0]
        assert len(messages) == 2
        assert isinstance(messages[0], SystemMessage)
        assert messages[0].content == "You are a Vim expert."
        assert isinstance(messages[1], HumanMessage)
        assert messages[1].content == "explain :global"

    def test_uses_config_to_build_llm(self, config: Config) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="ok")

        with (
            patch("vimai.chain.build_llm", return_value=mock_llm) as mock_build,
            patch("vimai.chain.load_agent") as mock_load_agent,
        ):
            mock_load_agent.return_value = MagicMock(system_prompt="Prompt")
            invoke_agent(config, "git", "status help")

        mock_build.assert_called_once_with(config)
        mock_load_agent.assert_called_once_with("git")

    def test_propagates_agent_loader_error(self, config: Config) -> None:
        with patch(
            "vimai.chain.load_agent", side_effect=RuntimeError("No agent found")
        ):
            with pytest.raises(RuntimeError, match="No agent found"):
                invoke_agent(config, "missing", "hello")
