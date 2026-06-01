"""Environment variable loading and validation for vimai (F05)."""

import os
from dataclasses import dataclass, field

_DEFAULT_API_VERSION = "2024-05-01-preview"


class ConfigError(Exception):
    """Raised when required environment variables are missing or invalid."""


@dataclass
class Config:
    """Validated configuration loaded from environment variables."""

    endpoint: str
    deployment: str
    api_version: str = field(default=_DEFAULT_API_VERSION)


def load_config() -> Config:
    """Load and validate configuration from environment variables.

    Required vars:
        AZURE_OPENAI_ENDPOINT   - Azure OpenAI resource endpoint URL
        AZURE_OPENAI_DEPLOYMENT - Model deployment name

    Optional vars:
        AZURE_OPENAI_API_VERSION - API version (default: 2024-05-01-preview)

    Raises:
        ConfigError: If any required variable is missing.
    """
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

    return Config(endpoint=endpoint, deployment=deployment, api_version=api_version)
