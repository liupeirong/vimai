"""Azure OpenAI LLM setup using Entra ID authentication (F05)."""

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI

from .config import Config

_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def build_llm(config: Config) -> AzureChatOpenAI:
    """Create an AzureChatOpenAI instance authenticated via Entra ID.

    Uses DefaultAzureCredential so any standard Azure auth method works
    (az login, managed identity, environment credentials, etc.).
    No API key is required.

    Args:
        config: Validated configuration from load_config().

    Returns:
        A configured AzureChatOpenAI instance ready for invocation.
    """
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        _COGNITIVE_SCOPE,
    )
    return AzureChatOpenAI(
        azure_endpoint=config.endpoint,
        azure_deployment=config.deployment,
        api_version=config.api_version,
        azure_ad_token_provider=token_provider,
    )
