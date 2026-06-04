"""Azure OpenAI LLM setup using Entra ID authentication (F05)."""

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import ChatOpenAI

from .config import Config

_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def build_llm(config: Config) -> ChatOpenAI:
    """Create a ChatOpenAI instance for Azure AI Foundry's openai/v1 API.

    Uses DefaultAzureCredential + get_bearer_token_provider so any standard
    Azure auth method works (az login, managed identity, environment
    credentials, etc.). No API key is required.

    The base URL is constructed as ``{endpoint}/openai/v1/``, which routes
    requests through the Azure AI Foundry unified endpoint and supports all
    deployed models (OpenAI, Llama, DeepSeek, Mistral, Phi, etc.).

    Args:
        config: Validated configuration from load_config().

    Returns:
        A configured ChatOpenAI instance ready for invocation.
    """
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, _COGNITIVE_SCOPE)
    base_url = config.endpoint.rstrip("/") + "/openai/v1/"
    return ChatOpenAI(
        base_url=base_url,
        model=config.deployment,
        api_key=token_provider,
    )
