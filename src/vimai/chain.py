"""LangChain invocation against Azure OpenAI (F01, F03, F07)."""

from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from .agents import Agent, load_agent
from .config import Config
from .llm import build_llm
from .session import SessionEntry, load_session, save_session


def invoke_chain(config: Config, prompt: str) -> str:
    """Send a single-turn prompt to Azure OpenAI and return the response text.

    Args:
        config: Validated configuration from load_config().
        prompt: The user's prompt text.

    Returns:
        The LLM response as a plain string.

    Raises:
        Any exception raised by the underlying LLM client (e.g. auth failure,
        network error) is propagated to the caller.
    """
    llm = build_llm(config)
    response = llm.invoke([HumanMessage(content=prompt)])
    return str(response.content)


def invoke_chain_with_history(
    config: Config, session_path: Path | str, prompt: str
) -> str:
    """Send a prompt to Azure OpenAI with prior session history, then persist both turns.

    Loads existing history from *session_path* (if any), appends the new user
    prompt, calls the LLM, appends the assistant reply, and saves the updated
    history back to *session_path*.

    Args:
        config: Validated configuration from load_config().
        session_path: Path to the session JSON file (created on first call).
        prompt: The user's prompt text.

    Returns:
        The LLM response as a plain string.

    Raises:
        Any exception raised by the underlying LLM client is propagated.
    """
    from datetime import datetime, timezone

    llm = build_llm(config)
    history = load_session(session_path)

    messages: list[BaseMessage] = []
    for entry in history:
        if entry.role == "user":
            messages.append(HumanMessage(content=entry.content))
        elif entry.role == "assistant":
            messages.append(AIMessage(content=entry.content))
    messages.append(HumanMessage(content=prompt))

    response = llm.invoke(messages)
    response_text = str(response.content)

    now = datetime.now(tz=timezone.utc).isoformat()
    history.append(SessionEntry("user", prompt, now))
    history.append(SessionEntry("assistant", response_text, now))
    save_session(session_path, history)

    return response_text


def invoke_agent(config: Config, agent_name: str, prompt: str) -> str:
    """Send a stateless single-turn prompt using a named agent system prompt.

    Args:
        config: Validated configuration from load_config().
        agent_name: Agent name without the leading @.
        prompt: The user's prompt text.

    Returns:
        The LLM response as a plain string.

    Raises:
        AgentNotFoundError: If no matching user or built-in agent prompt exists.
        Any exception raised by the underlying LLM client is propagated.
    """
    agent = load_agent(agent_name)
    return invoke_loaded_agent(config, agent, prompt)


def invoke_loaded_agent(config: Config, agent: Agent, prompt: str) -> str:
    """Send a stateless single-turn prompt using an already loaded agent."""
    llm = build_llm(config)
    response = llm.invoke(
        [
            SystemMessage(content=agent.system_prompt),
            HumanMessage(content=prompt),
        ]
    )
    return str(response.content)
