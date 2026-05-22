import json

from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings

EXTRACT_PROMPT = """你是一个知识提取专家。请从以下文本中提取核心知识点。

对每个知识点输出 JSON 格式（注意是严格的 JSON，不要包含其他内容）：
{{
  "concepts": [
    {{
      "label": "知识点名称（简短中文）",
      "content": "详细解释（中文）",
      "category": "分类（definition/concept/formula/principle/procedure）"
    }}
  ]
}}

文本内容：
"""


async def extract_knowledge_points(text: str) -> list[dict]:
    """Extract knowledge points from text using the configured LLM."""
    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    messages = [
        LLMMessage(role=LLMRole.USER, content=EXTRACT_PROMPT + text),
    ]
    config = LLMConfig(temperature=0.3, max_tokens=4096)

    response = await provider.chat(messages, config)

    try:
        # Try to parse JSON from response
        data = json.loads(response.content)
        return data.get("concepts", [])
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("concepts", [])
            except json.JSONDecodeError:
                pass
        return []


def _get_api_key(provider_name: str) -> str:
    if provider_name == "claude":
        return settings.claude_api_key
    elif provider_name == "openai":
        return settings.openai_api_key
    elif provider_name == "deepseek":
        return settings.deepseek_api_key
    return ""
