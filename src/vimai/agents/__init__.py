"""Agent prompt loading and external runner support for vimai."""

from .external import (
    EXTERNAL_AGENT_TIMEOUT_SECONDS,
    ExternalAgentError,
    invoke_external_agent,
)
from .loader import Agent, AgentNotFoundError, load_agent, normalize_agent_name

__all__ = [
    "Agent",
    "AgentNotFoundError",
    "EXTERNAL_AGENT_TIMEOUT_SECONDS",
    "ExternalAgentError",
    "invoke_external_agent",
    "load_agent",
    "normalize_agent_name",
]
