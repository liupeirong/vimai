"""Environment variable loading and validation for vimai (F05, F06)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

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
    api_key: str | None = None
    external_agents_dir: Path | None = None


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


def _external_agents_dir_from_env() -> Path | None:
    raw_dir = os.environ.get("VIMAI_EXTERNAL_AGENTS_DIR", "").strip()
    return Path(raw_dir).expanduser() if raw_dir else None


def load_external_agents_dir() -> Path:
    """Load and validate the external agents directory from environment/.env."""
    _load_dotenv_files()
    external_agents_dir = _external_agents_dir_from_env()
    if external_agents_dir is None:
        raise ConfigError(
            "Missing VIMAI_EXTERNAL_AGENTS_DIR. Set it to the directory "
            "containing external agent subdirectories."
        )
    return external_agents_dir


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Required vars:
        OPENAI_BASE_URL - OpenAI compatible resource endpoint URL
        OPENAI_MODEL - Model deployment name

    Optional vars:
        OPENAI_API_KEY           - If not using Entra ID auth
        LANGSMITH_API_KEY        - LangSmith API key for tracing
        LANGSMITH_PROJECT        - LangSmith project name (default: vimai)
        VIMAI_EXTERNAL_AGENTS_DIR - Parent directory for external agent wrappers

    Raises:
        ConfigError: If any required variable is missing.
    """
    _load_dotenv_files()

    endpoint = os.environ.get("OPENAI_BASE_URL", "").strip()
    deployment = os.environ.get("OPENAI_MODEL", "").strip()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip() or None

    missing = [
        name
        for name, value in [
            ("OPENAI_BASE_URL", endpoint),
            ("OPENAI_MODEL", deployment),
        ]
        if not value
    ]
    if missing:
        raise ConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Set them before running vimai."
        )

    _configure_langsmith_tracing()

    return Config(
        endpoint=endpoint,
        deployment=deployment,
        api_key=api_key,
        external_agents_dir=_external_agents_dir_from_env(),
    )
