"""Unit tests for vimai.config (F05, F06)."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vimai.config import (
    Config,
    ConfigError,
    _DEFAULT_LANGSMITH_PROJECT,
    load_config,
    load_external_agents_dir,
)


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "vimai.config._DEFAULT_DOTENV_PATHS", (tmp_path / "missing.env",)
    )
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("VIMAI_EXTERNAL_AGENTS_DIR", raising=False)


class TestLoadConfig:
    def test_loads_required_openai_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")

        config = load_config()

        assert config.endpoint == "https://my.openai.azure.com/openai/v1"
        assert config.deployment == "gpt-4o"
        assert not config.api_key

    def test_loads_optional_openai_api_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")  # pragma: allowlist secret

        config = load_config()

        assert config.api_key == "sk-test"  # pragma: allowlist secret

    def test_raises_when_required_vars_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_MODEL", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            load_config()

        message = str(exc_info.value)
        assert "OPENAI_BASE_URL" in message
        assert "OPENAI_MODEL" in message

    def test_strips_whitespace_from_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(
            "OPENAI_BASE_URL", "  https://my.openai.azure.com/openai/v1  "
        )
        monkeypatch.setenv("OPENAI_MODEL", "  gpt-4o-mini  ")
        monkeypatch.setenv("OPENAI_API_KEY", "  sk-test  ")  # pragma: allowlist secret

        config = load_config()

        assert config.endpoint == "https://my.openai.azure.com/openai/v1"
        assert config.deployment == "gpt-4o-mini"
        assert config.api_key == "sk-test"  # pragma: allowlist secret

    def test_loads_openai_vars_from_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "OPENAI_BASE_URL=https://dotenv.openai.azure.com/openai/v1",
                    "OPENAI_MODEL=dotenv-model",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr("vimai.config._DEFAULT_DOTENV_PATHS", (env_file,))

        config = load_config()

        assert config.endpoint == "https://dotenv.openai.azure.com/openai/v1"
        assert config.deployment == "dotenv-model"

    def test_loads_openai_api_key_from_dotenv(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OPENAI_API_KEY=sk-from-dotenv\n",  # pragma: allowlist secret
            encoding="utf-8",
        )
        monkeypatch.setattr("vimai.config._DEFAULT_DOTENV_PATHS", (env_file,))
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")

        config = load_config()

        assert config.api_key == "sk-from-dotenv"  # pragma: allowlist secret

    def test_enables_langsmith_tracing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv(
            "LANGSMITH_API_KEY", "lsv2_test_key"
        )  # pragma: allowlist secret
        monkeypatch.setenv("LANGSMITH_TRACING", "false")
        monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")

        load_config()

        assert os.environ["LANGSMITH_TRACING"] == "true"
        assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
        assert os.environ["LANGSMITH_PROJECT"] == _DEFAULT_LANGSMITH_PROJECT

    def test_langsmith_key_absent_does_not_enable_tracing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")

        load_config()

        assert "LANGSMITH_TRACING" not in os.environ
        assert "LANGCHAIN_TRACING_V2" not in os.environ
        assert "LANGSMITH_PROJECT" not in os.environ

    def test_loads_external_agents_dir_from_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        external_agents_dir = tmp_path / "external-agents"
        monkeypatch.setenv("OPENAI_BASE_URL", "https://my.openai.azure.com/openai/v1")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
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
        config = Config(endpoint="https://ep.com", deployment="dep", api_key="sk")

        assert config.endpoint == "https://ep.com"
        assert config.deployment == "dep"
        assert config.api_key == "sk"  # pragma: allowlist secret
        assert config.external_agents_dir is None

    def test_api_key_optional(self) -> None:
        config = Config(endpoint="https://ep.com", deployment="dep", api_key=None)

        assert config.api_key is None
        assert config.external_agents_dir is None
