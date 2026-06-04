"""Environment variable loading and validation for vimai (F05, F06)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_API_VERSION = "2024-05-01-preview"
_DEFAULT_LANGSMITH_PROJECT = "vimai"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DOTENV_PATHS = (_PROJECT_ROOT / ".env",)


class ConfigError(Exception):
    """Raised when required environment variables are missing or invalid."""


@dataclass
class Config:
    """Validated configuration loaded from environment variables."""

    endpoint: str
    deployment: str
    api_version: str = field(default=_DEFAULT_API_VERSION)


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _load_dotenv_files(paths: tuple[Path, ...] | None = None) -> None:
    """Load KEY=VALUE pairs from .env files without overriding existing env vars."""
    env_paths = (
        paths if paths is not None else (Path.cwd() / ".env", *_DEFAULT_DOTENV_PATHS)
    )
    loaded: set[Path] = set()
    for path in env_paths:
        resolved = path.resolve()
        if resolved in loaded or not resolved.exists():
            continue
        loaded.add(resolved)

        for line_number, raw_line in enumerate(
            resolved.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line.removeprefix("export ").strip()
            if "=" not in line:
                raise ConfigError(
                    f"Invalid .env entry in {resolved} line {line_number}: "
                    "expected KEY=VALUE."
                )

            key, value = line.split("=", maxsplit=1)
            key = key.strip()
            if not key or any(char.isspace() for char in key):
                raise ConfigError(
                    f"Invalid .env key in {resolved} line {line_number}: "
                    "expected KEY=VALUE."
                )
            os.environ.setdefault(key, _strip_quotes(value.strip()))


def _enable_langsmith_tracing() -> None:
    """Ensure LangChain/LangSmith tracing is enabled for every LLM call."""
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT", _DEFAULT_LANGSMITH_PROJECT)


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Required vars:
        AZURE_OPENAI_ENDPOINT   - Azure OpenAI resource endpoint URL
        AZURE_OPENAI_DEPLOYMENT - Model deployment name
        LANGSMITH_API_KEY       - LangSmith API key for required tracing

    Optional vars:
        AZURE_OPENAI_API_VERSION - API version (default: 2024-05-01-preview)
        LANGSMITH_PROJECT        - LangSmith project name (default: vimai)

    Raises:
        ConfigError: If any required variable is missing.
    """
    _load_dotenv_files()

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "").strip()
    langsmith_api_key = os.environ.get("LANGSMITH_API_KEY", "").strip()

    missing = [
        name
        for name, value in [
            ("AZURE_OPENAI_ENDPOINT", endpoint),
            ("AZURE_OPENAI_DEPLOYMENT", deployment),
            ("LANGSMITH_API_KEY", langsmith_api_key),
        ]
        if not value
    ]
    if missing:
        raise ConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Set them before running vimai."
        )

    api_version = (
        os.environ.get("AZURE_OPENAI_API_VERSION", "").strip() or _DEFAULT_API_VERSION
    )

    _enable_langsmith_tracing()

    return Config(endpoint=endpoint, deployment=deployment, api_version=api_version)
