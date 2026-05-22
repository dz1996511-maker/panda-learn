from app.llm.base import BaseLLMProvider

_providers: dict[str, type[BaseLLMProvider]] = {}


def register_provider(name: str, provider_cls: type[BaseLLMProvider]) -> None:
    """Register an LLM provider class under the given name."""
    _providers[name] = provider_cls


def get_provider(provider_name: str, api_key: str, default_model: str | None = None) -> BaseLLMProvider:
    """Get an LLM provider instance by name."""
    cls = _providers.get(provider_name)
    if cls is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {list(_providers.keys())}"
        )
    return cls(api_key=api_key, default_model=default_model)


def list_providers() -> list[str]:
    """List all registered provider names."""
    return list(_providers.keys())


# Late imports to avoid circular dependencies
from app.llm.providers.claude_provider import ClaudeProvider  # noqa: E402
from app.llm.providers.openai_provider import OpenAIProvider  # noqa: E402
from app.llm.providers.deepseek_provider import DeepSeekProvider  # noqa: E402

register_provider("claude", ClaudeProvider)
register_provider("openai", OpenAIProvider)
register_provider("deepseek", DeepSeekProvider)
