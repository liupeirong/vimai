"""Unit tests for vimai.config (F05, F06)."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.config import (
    Config,
    ConfigError,
    load_config,
    load_external_agents_dir,
    _DEFAULT_API_VERSION,
    _DEFAULT_LANGSMITH_PROJECT,
)


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "vimai.config._DEFAULT_DOTENV_PATHS", (tmp_path / "missing.env",)
    )
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("VIMAI_EXTERNAL_AGENTS_DIR", raising=False)


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
        monkeypatch.setenv("LANGSMITH_API_KEY", "  lsv2_test_key  ")

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

    def test_loads_langsmith_key_from_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text('LANGSMITH_API_KEY="lsv2_from_dotenv"\n', encoding="utf-8")
        monkeypatch.setattr("vimai.config._DEFAULT_DOTENV_PATHS", (env_file,))
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)

        load_config()

        assert os.environ["LANGSMITH_API_KEY"] == "lsv2_from_dotenv"

    def test_loads_azure_vars_from_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "AZURE_OPENAI_ENDPOINT=https://dotenv.openai.azure.com/",
                    "AZURE_OPENAI_DEPLOYMENT=dotenv-deployment",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr("vimai.config._DEFAULT_DOTENV_PATHS", (env_file,))

        config = load_config()

        assert config.endpoint == "https://dotenv.openai.azure.com/"
        assert config.deployment == "dotenv-deployment"

    def test_enables_langsmith_tracing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.setenv("LANGSMITH_API_KEY", "lsv2_test_key")
        monkeypatch.setenv("LANGSMITH_TRACING", "false")
        monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

        load_config()

        assert os.environ["LANGSMITH_TRACING"] == "true"
        assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
        assert os.environ["LANGSMITH_PROJECT"] == _DEFAULT_LANGSMITH_PROJECT

    def test_langsmith_key_absent_does_not_enable_tracing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        config = load_config()

        assert config.deployment == "gpt-4o"
        assert "LANGSMITH_TRACING" not in os.environ
        assert "LANGCHAIN_TRACING_V2" not in os.environ
        assert "LANGSMITH_PROJECT" not in os.environ

    def test_loads_external_agents_dir_from_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        external_agents_dir = tmp_path / "external-agents"
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com/")
        monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        monkeypatch.setenv("VIMAI_EXTERNAL_AGENTS_DIR", str(external_agents_dir))

        config = load_config()

        assert config.external_agents_dir == external_agents_dir

    def test_load_external_agents_dir_reads_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        external_agents_dir = tmp_path / "external-agents"
        env_file = tmp_path / ".env"
        env_file.write_text(
            f"VIMAI_EXTERNAL_AGENTS_DIR={external_agents_dir}\n", encoding="utf-8"
        )
        monkeypatch.setattr("vimai.config._DEFAULT_DOTENV_PATHS", (env_file,))

        assert load_external_agents_dir() == external_agents_dir

    def test_load_external_agents_dir_requires_env_var(self) -> None:
        with pytest.raises(ConfigError) as exc_info:
            load_external_agents_dir()

        assert "VIMAI_EXTERNAL_AGENTS_DIR" in str(exc_info.value)


class TestConfig:
    def test_dataclass_fields(self) -> None:
        config = Config(endpoint="https://ep.com", deployment="dep", api_version="v1")

        assert config.endpoint == "https://ep.com"
        assert config.deployment == "dep"
        assert config.api_version == "v1"
        assert not hasattr(config, "langsmith_api_key")

    def test_default_api_version(self) -> None:
        config = Config(endpoint="https://ep.com", deployment="dep")

        assert config.api_version == _DEFAULT_API_VERSION
        assert config.external_agents_dir is None
