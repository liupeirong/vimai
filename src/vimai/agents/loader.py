"""Load named agent system prompts from user files or bundled defaults."""

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
import re

_AGENT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_BUILTIN_AGENT_PACKAGE = "vimai.builtin_agents"


class AgentNotFoundError(Exception):
    """Raised when no user-defined or built-in agent prompt exists."""


@dataclass(frozen=True)
class Agent:
    """A loaded agent system prompt."""

    name: str
    system_prompt: str
    source_path: Path | None
    is_builtin: bool


def default_user_agents_dir() -> Path:
    """Return the default directory for user-defined agent prompt files."""
    return Path.home() / ".vimai" / "agents"


def load_agent(name: str, *, user_agents_dir: Path | str | None = None) -> Agent:
    """Load a named agent from ~/.vimai/agents or bundled defaults.

    User-defined agents override bundled agents with the same name.

    Args:
        name: Agent name without the leading @.
        user_agents_dir: Optional override for tests or alternate runtimes.

    Returns:
        The loaded agent prompt and source metadata.

    Raises:
        ValueError: If *name* is empty or contains path separators/special chars.
        AgentNotFoundError: If no matching prompt file exists.
    """
    agent_name = normalize_agent_name(name)
    agents_dir = (
        Path(user_agents_dir)
        if user_agents_dir is not None
        else default_user_agents_dir()
    )

    user_agent_path = agents_dir / f"{agent_name}.md"
    if user_agent_path.is_file():
        return Agent(
            name=agent_name,
            system_prompt=user_agent_path.read_text(encoding="utf-8").strip(),
            source_path=user_agent_path,
            is_builtin=False,
        )

    builtin_prompt = _read_builtin_agent(agent_name)
    if builtin_prompt is not None:
        return Agent(
            name=agent_name,
            system_prompt=builtin_prompt.strip(),
            source_path=None,
            is_builtin=True,
        )

    raise AgentNotFoundError(
        f"No agent found for @{agent_name}. Create ~/.vimai/agents/{agent_name}.md"
    )


def normalize_agent_name(name: str) -> str:
    """Return a validated agent name without a leading @."""
    agent_name = name.strip().removeprefix("@")
    if not agent_name:
        raise ValueError("Agent name must not be empty.")
    if not _AGENT_NAME_RE.fullmatch(agent_name):
        raise ValueError(
            "Agent name must contain only letters, numbers, underscores, or hyphens."
        )
    return agent_name


def _read_builtin_agent(agent_name: str) -> str | None:
    resource = resources.files(_BUILTIN_AGENT_PACKAGE).joinpath(f"{agent_name}.md")
    if not resource.is_file():
        return None
    return resource.read_text(encoding="utf-8")
