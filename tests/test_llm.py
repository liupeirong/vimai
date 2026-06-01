"""Unit tests for vimai.llm (F05)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.config import Config
from vimai.llm import build_llm, _COGNITIVE_SCOPE


@pytest.fixture()
def config() -> Config:
    return Config(
        endpoint="https://my.openai.azure.com/",
        deployment="gpt-4o",
        api_version="2024-05-01-preview",
    )


class TestBuildLlm:
    def test_returns_azure_chat_openai(self, config: Config) -> None:
        from langchain_openai import AzureChatOpenAI

        mock_credential = MagicMock()
        mock_token_provider = MagicMock()

        with (
            patch("vimai.llm.DefaultAzureCredential", return_value=mock_credential),
            patch(
                "vimai.llm.get_bearer_token_provider",
                return_value=mock_token_provider,
            ),
        ):
            llm = build_llm(config)

        assert isinstance(llm, AzureChatOpenAI)

    def test_uses_default_azure_credential(self, config: Config) -> None:
        mock_credential = MagicMock()

        with (
            patch(
                "vimai.llm.DefaultAzureCredential", return_value=mock_credential
            ) as mock_cls,
            patch("vimai.llm.get_bearer_token_provider", return_value=MagicMock()),
        ):
            build_llm(config)

        mock_cls.assert_called_once_with()

    def test_requests_cognitive_scope(self, config: Config) -> None:
        mock_credential = MagicMock()

        with (
            patch("vimai.llm.DefaultAzureCredential", return_value=mock_credential),
            patch(
                "vimai.llm.get_bearer_token_provider", return_value=MagicMock()
            ) as mock_gbt,
        ):
            build_llm(config)

        mock_gbt.assert_called_once_with(mock_credential, _COGNITIVE_SCOPE)

    def test_passes_config_values_to_llm(self, config: Config) -> None:
        mock_token_provider = MagicMock()

        with (
            patch("vimai.llm.DefaultAzureCredential", return_value=MagicMock()),
            patch(
                "vimai.llm.get_bearer_token_provider", return_value=mock_token_provider
            ),
        ):
            llm = build_llm(config)

        assert llm.azure_endpoint == config.endpoint
        assert llm.deployment_name == config.deployment
        assert llm.openai_api_version == config.api_version

    def test_no_api_key_used(self, config: Config) -> None:
        with (
            patch("vimai.llm.DefaultAzureCredential", return_value=MagicMock()),
            patch("vimai.llm.get_bearer_token_provider", return_value=MagicMock()),
        ):
            llm = build_llm(config)

        # api_key should not be set to a real secret value
        api_key_value = llm.openai_api_key
        secret_value = api_key_value.get_secret_value() if api_key_value else None
        assert secret_value != "some-secret-key"
