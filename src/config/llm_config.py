"""LLM configuration module for OpenRouter integration.

This module provides configuration and factory functions for using OpenRouter
as the LLM provider. OpenRouter supports multiple LLM providers including
OpenAI, Anthropic, and others through a unified API.

Example:
    >>> from src.config.llm_config import create_llm
    >>> llm = create_llm(model="anthropic/claude-3.5-sonnet")
    >>> response = llm.invoke("Hello, world!")
"""

import os

from langchain_openai import ChatOpenAI  # type: ignore[import-not-found]


class ChatOpenRouter(ChatOpenAI):
    """ChatOpenAI client configured for OpenRouter API.

    This class extends ChatOpenAI to use OpenRouter's API endpoint and
    adds required headers for OpenRouter integration.

    OpenRouter is a unified API for multiple LLM providers, allowing you to
    use different models (Claude, GPT, etc.) through a single interface.

    Args:
        api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY env var.
        model: Model identifier (e.g., "anthropic/claude-3.5-sonnet").
        site_url: Your site URL for OpenRouter rate limiting.
        site_name: Your site name for OpenRouter identification.
        **kwargs: Additional arguments passed to ChatOpenAI.

    Attributes:
        api_key: The OpenRouter API key.
        model_name: The model identifier.

    Example:
        >>> llm = ChatOpenRouter(
        ...     api_key="sk-or-...",
        ...     model="anthropic/claude-3.5-sonnet",
        ...     site_url="https://example.com",
        ...     site_name="MyApp"
        ... )
        >>> response = llm.invoke("What is the capital of France?")
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        site_url: str | None = None,
        site_name: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize ChatOpenRouter client.

        Args:
            api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY.
            model: Model identifier. Defaults to OPENROUTER_MODEL.
            site_url: Site URL for OpenRouter. Defaults to OPENROUTER_SITE_URL.
            site_name: Site name for OpenRouter. Defaults to OPENROUTER_SITE_NAME.
            **kwargs: Additional arguments for ChatOpenAI.
        """
        api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        model = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-4.5")
        site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "")
        site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "")

        if not api_key:
            msg = "OPENROUTER_API_KEY not set and no api_key provided"
            raise ValueError(msg)

        # Initialize parent ChatOpenAI with OpenRouter endpoint
        super().__init__(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers=self._build_headers(site_url, site_name),
            **kwargs,
        )

    @staticmethod
    def _build_headers(site_url: str | None, site_name: str | None) -> dict[str, str]:
        """Build HTTP headers required by OpenRouter API.

        OpenRouter requires HTTP-Referer and X-Title headers for rate
        limiting and tracking purposes.

        Args:
            site_url: Your application's URL.
            site_name: Your application's name.

        Returns:
            Dictionary of headers to include in requests.
        """
        headers: dict[str, str] = {}

        if site_url:
            headers["HTTP-Referer"] = site_url

        if site_name:
            headers["X-Title"] = site_name

        return headers


def create_llm(
    model: str | None = None,
    api_key: str | None = None,
    site_url: str | None = None,
    site_name: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    **kwargs,
) -> ChatOpenRouter:
    """Factory function to create a configured LLM instance.

    This function provides a convenient way to create an OpenRouter LLM
    instance with sensible defaults. Configuration can be provided via
    function arguments or environment variables.

    Environment Variables:
        OPENROUTER_API_KEY: OpenRouter API key (required)
        OPENROUTER_MODEL: Model identifier (default: anthropic/claude-3.5-sonnet)
        OPENROUTER_SITE_URL: Your site URL for OpenRouter rate limiting
        OPENROUTER_SITE_NAME: Your site name for OpenRouter identification

    Args:
        model: Model identifier (e.g., "anthropic/claude-3.5-sonnet").
            Defaults to OPENROUTER_MODEL env var or "anthropic/claude-3.5-sonnet".
        api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY env var.
        site_url: Your site URL for OpenRouter. Defaults to OPENROUTER_SITE_URL.
        site_name: Your site name for OpenRouter. Defaults to OPENROUTER_SITE_NAME.
        temperature: Model temperature (0.0-2.0). Defaults to 0.7.
        max_tokens: Maximum tokens in response. Defaults to None (no limit).
        **kwargs: Additional arguments passed to ChatOpenRouter.

    Returns:
        Configured ChatOpenRouter instance ready for use.

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set and not provided.

    Example:
        >>> # Using environment variables
        >>> llm = create_llm()
        >>>
        >>> # Using explicit arguments
        >>> llm = create_llm(
        ...     model="anthropic/claude-3.5-sonnet",
        ...     api_key="sk-or-...",
        ...     temperature=0.5,
        ...     max_tokens=2000
        ... )
        >>>
        >>> response = llm.invoke("Explain quantum computing")
    """
    return ChatOpenRouter(
        api_key=api_key,
        model=model,
        site_url=site_url,
        site_name=site_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
