import json

from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings


async def find_relations(concepts: list[dict], db_session) -> list[dict]:
    """Find relationships between a list of concepts using LLM.

    concepts: list of {"id": int, "label": str}
    Returns: list of {"source_id": int, "target_id": int, "relation_type": str, "description": str}
    """
    if len(concepts) < 2:
        return []

    concept_list = "\n".join(f"{c['id']}. {c['label']}" for c in concepts)

    prompt = (
        "分析以下知识点之间的关系，找出它们之间的关联（如前提条件、相关、相似、矛盾等）。\n\n"
        f"知识点列表：\n{concept_list}\n\n"
        '输出JSON格式：{{"relations": ['
        '{{"source_id": 1, "target_id": 2, "relation_type": "prerequisite", "description": "说明"}}'
        "]}}"
    )

    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    messages = [
        LLMMessage(role=LLMRole.USER, content=prompt),
    ]
    config = LLMConfig(temperature=0.3, max_tokens=4096)

    response = await provider.chat(messages, config)

    try:
        data = json.loads(response.content)
        relations = data.get("relations", [])
    except json.JSONDecodeError:
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                relations = data.get("relations", [])
            except json.JSONDecodeError:
                relations = []
        else:
            relations = []

    # Save to database
    from app.database.models import ConceptRelation
    saved = []
    for rel in relations:
        cr = ConceptRelation(
            source_id=rel["source_id"],
            target_id=rel["target_id"],
            relation_type=rel.get("relation_type", "related"),
            description=rel.get("description", ""),
        )
        db_session.add(cr)
        saved.append({
            "source_id": rel["source_id"],
            "target_id": rel["target_id"],
            "relation_type": rel.get("relation_type", "related"),
            "description": rel.get("description", ""),
        })

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
