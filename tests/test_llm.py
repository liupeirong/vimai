"""Unit tests for vimai.llm (F05)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.config import Config
from vimai.llm import _COGNITIVE_SCOPE, build_llm


@pytest.fixture()
def config_without_api_key() -> Config:
    return Config(
        endpoint="https://my.openai.azure.com/openai/v1",
        deployment="gpt-4o",
        api_key=None,
    )


@pytest.fixture()
def config_with_api_key() -> Config:
    return Config(
        endpoint="https://my.openai.azure.com/openai/v1",
        deployment="gpt-4o",
        api_key="sk-test", # pragma: allowlist secret
    )


class TestBuildLlm:
    def test_uses_entra_token_provider_without_api_key(
        self, config_without_api_key: Config
    ) -> None:
        mock_credential = MagicMock()
        mock_token_provider = MagicMock()

        with (
            patch("vimai.llm.DefaultAzureCredential", return_value=mock_credential),
            patch(
                "vimai.llm.get_bearer_token_provider",
                return_value=mock_token_provider,
            ) as mock_get_provider,
            patch("vimai.llm.ChatOpenAI", return_value=MagicMock()) as mock_chat,
        ):
            build_llm(config_without_api_key)

        mock_get_provider.assert_called_once_with(mock_credential, _COGNITIVE_SCOPE)
        mock_chat.assert_called_once_with(
            base_url="https://my.openai.azure.com/openai/v1",
            model="gpt-4o",
            api_key=mock_token_provider,
        )

    def test_uses_openai_api_key_when_provided(
        self, config_with_api_key: Config
    ) -> None:
        with (
            patch("vimai.llm.DefaultAzureCredential") as mock_credential_cls,
            patch("vimai.llm.get_bearer_token_provider") as mock_get_provider,
            patch("vimai.llm.ChatOpenAI", return_value=MagicMock()) as mock_chat,
        ):
            build_llm(config_with_api_key)

        mock_credential_cls.assert_not_called()
        mock_get_provider.assert_not_called()
        mock_chat.assert_called_once_with(
            base_url="https://my.openai.azure.com/openai/v1",
            model="gpt-4o",
            api_key="sk-test", # pragma: allowlist secret
        )
