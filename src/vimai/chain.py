"""Single-turn LangChain invocation against Azure OpenAI (F01)."""

from langchain_core.messages import HumanMessage

from .config import Config
from .llm import build_llm


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
