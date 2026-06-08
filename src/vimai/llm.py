"""Azure OpenAI LLM setup using Entra ID authentication (F05)."""

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import ChatOpenAI

from .config import Config

_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def build_llm(config: Config) -> ChatOpenAI:
    """Create a ChatOpenAI instance for OpenAI compatible API.

    If api key is not provided, uses DefaultAzureCredential + get_bearer_token_provider
      so any standard Azure auth method works (az login, managed identity, environment
    credentials, etc.).

    Args:
        config: Validated configuration from load_config().

    Returns:
        A configured ChatOpenAI instance ready for invocation.
    """
    if not config.api_key:
        credential = DefaultAzureCredential()
        api_key = get_bearer_token_provider(credential, _COGNITIVE_SCOPE)
    else:
        api_key = config.api_key

    return ChatOpenAI(
        base_url=config.endpoint,
        model=config.deployment,
        api_key=api_key,
    )
