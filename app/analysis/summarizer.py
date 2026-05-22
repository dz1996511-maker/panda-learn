from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings

SUMMARY_PROMPT = """请用中文总结以下文本的核心内容，包括：
1. 主要内容概述（3-5句话）
2. 关键论点或发现（列表形式）
3. 适用场景或意义

文本内容：
"""


async def generate_summary(text: str) -> str:
    """Generate a Chinese summary of the given text."""
    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    # Truncate if too long
    max_chars = 15000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[内容已截断]"

    messages = [
        LLMMessage(role=LLMRole.USER, content=SUMMARY_PROMPT + text),
    ]
    config = LLMConfig(temperature=0.3, max_tokens=2048)

    response = await provider.chat(messages, config)
    return response.content


def _get_api_key(provider_name: str) -> str:
    if provider_name == "claude":
        return settings.claude_api_key
    elif provider_name == "openai":
        return settings.openai_api_key
    elif provider_name == "deepseek":
        return settings.deepseek_api_key
    return ""
