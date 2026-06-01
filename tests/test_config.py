"""Unit tests for vimai.config (F05)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.config import Config, ConfigError, load_config, _DEFAULT_API_VERSION


class TestLoadConfig:
    def test_loads_all_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2025-01-01")

        config = load_config()

        assert config.endpoint == "https://my.openai.azure.com/"
        assert config.deployment == "gpt-4o"
        assert config.api_version == "2025-01-01"

    def test_api_version_defaults_when_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)

        config = load_config()

        assert config.api_version == _DEFAULT_API_VERSION

    def test_api_version_defaults_when_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "   ")

        config = load_config()

        assert config.api_version == _DEFAULT_API_VERSION

    def test_raises_when_endpoint_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        assert "AZURE_OPENAI_ENDPOINT" in str(exc_info.value)

    def test_raises_when_deployment_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        assert "AZURE_OPENAI_DEPLOYMENT" in str(exc_info.value)

    def test_raises_when_both_required_vars_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        message = str(exc_info.value)
        assert "AZURE_OPENAI_ENDPOINT" in message
        assert "AZURE_OPENAI_DEPLOYMENT" in message

    def test_error_message_contains_setup_hint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        assert "vimai" in str(exc_info.value).lower()

    def test_strips_whitespace_from_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "  https://my.openai.azure.com/  ")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "  gpt-4o  ")

        config = load_config()

        assert config.endpoint == "https://my.openai.azure.com/"
        assert config.deployment == "gpt-4o"

    def test_raises_when_endpoint_is_whitespace_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "   ")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        assert "AZURE_OPENAI_ENDPOINT" in str(exc_info.value)


class TestConfig:
    def test_dataclass_fields(self) -> None:
        config = Config(endpoint="https://ep.com", deployment="dep", api_version="v1")

        assert config.endpoint == "https://ep.com"
        assert config.deployment == "dep"
        assert config.api_version == "v1"

    def test_default_api_version(self) -> None:
        config = Config(endpoint="https://ep.com", deployment="dep")

        assert config.api_version == _DEFAULT_API_VERSION
