"""Environment variable loading and validation for vimai (F05, F06)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

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


def _load_dotenv_files(paths: tuple[Path, ...] | None = None) -> None:
    """Load .env files without overriding existing environment variables."""
    env_paths = (
        paths if paths is not None else (Path.cwd() / ".env", *_DEFAULT_DOTENV_PATHS)
    )
    loaded: set[Path] = set()
    for path in env_paths:
        resolved = path.resolve()
        if resolved in loaded or not resolved.exists():
            continue
        loaded.add(resolved)
        load_dotenv(dotenv_path=resolved, override=False)


def _configure_langsmith_tracing() -> None:
    """Enable LangSmith tracing only when the user provides an API key."""
    if not os.environ.get("LANGSMITH_API_KEY", "").strip():
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT", _DEFAULT_LANGSMITH_PROJECT)


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Required vars:
        AZURE_OPENAI_ENDPOINT   - Azure OpenAI resource endpoint URL
        AZURE_OPENAI_DEPLOYMENT - Model deployment name

    Optional vars:
        AZURE_OPENAI_API_VERSION - API version (default: 2024-05-01-preview)
        LANGSMITH_API_KEY        - LangSmith API key for tracing
        LANGSMITH_PROJECT        - LangSmith project name (default: vimai)

    Raises:
        ConfigError: If any required variable is missing.
    """
    _load_dotenv_files()

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "").strip()

    missing = [
        name
        for name, value in [
            ("AZURE_OPENAI_ENDPOINT", endpoint),
            ("AZURE_OPENAI_DEPLOYMENT", deployment),
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

    _configure_langsmith_tracing()

    return Config(endpoint=endpoint, deployment=deployment, api_version=api_version)
