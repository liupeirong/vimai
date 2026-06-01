"""Unit tests for vimai.chain (F01)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.chain import invoke_chain
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
