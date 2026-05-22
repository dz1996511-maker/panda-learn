import json

from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings

CONCEPT_EXTRACT_PROMPT = """请从以下文本中提取核心概念和知识点，输出严格的JSON格式：

{
  "concepts": [
    {
      "name": "概念名称",
      "definition": "定义解释",
      "importance": 0.8,
      "related_terms": ["术语1", "术语2"]
    }
  ]
}

文本：
"""


async def extract_concepts(text: str) -> list[dict]:
    """Extract key concepts with definitions from text."""
    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    if len(text) > 12000:
        text = text[:12000] + "\n\n[内容已截断]"

    messages = [
        LLMMessage(role=LLMRole.USER, content=CONCEPT_EXTRACT_PROMPT + text),
    ]
    config = LLMConfig(temperature=0.3, max_tokens=4096)

    response = await provider.chat(messages, config)

    try:
        data = json.loads(response.content)
        return data.get("concepts", [])
    except json.JSONDecodeError:
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("concepts", [])
            except json.JSONDecodeError:
                pass
        return []


async def extract_and_save_concepts(text: str, document_id: int, db_session) -> list:
    """Extract concepts and save them as knowledge points."""
    from app.database.models import KnowledgePoint
    concepts = await extract_concepts(text)
    saved = []
    for c in concepts:
        kp = KnowledgePoint(
            document_id=document_id,
            label=c.get("name", "未命名"),
            content=c.get("definition", ""),
            category="concept",
        )
        db_session.add(kp)
        saved.append(kp)
    await db_session.commit()
    return saved


def _get_api_key(provider_name: str) -> str:
    if provider_name == "claude":
        return settings.claude_api_key
    elif provider_name == "openai":
        return settings.openai_api_key
    elif provider_name == "deepseek":
        return settings.deepseek_api_key
    return ""
