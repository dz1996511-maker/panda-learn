import json
import random

from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings
from app.practice.templates import QuestionType, QUESTION_TEMPLATES, DEFAULT_TYPE_WEIGHTS


async def generate_question(
    knowledge_point_label: str,
    knowledge_point_content: str,
    question_type: QuestionType | None = None,
) -> dict | None:
    """Generate a practice question for a knowledge point using LLM.

    Returns a dict with keys: question, options (optional), answer, explanation
    """
    if question_type is None:
        question_type = random.choices(
            list(DEFAULT_TYPE_WEIGHTS.keys()),
            weights=list(DEFAULT_TYPE_WEIGHTS.values()),
        )[0]

    template = QUESTION_TEMPLATES[question_type]

    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    prompt = (
        f"知识点：{knowledge_point_label}\n\n"
        f"内容：{knowledge_point_content[:3000]}\n\n"
        f"{template}"
    )

    messages = [
        LLMMessage(role=LLMRole.SYSTEM, content="你是一个出题老师。请根据知识点生成练习题。"),
        LLMMessage(role=LLMRole.USER, content=prompt),
    ]
    config = LLMConfig(temperature=0.7, max_tokens=2048)

    response = await provider.chat(messages, config)

    try:
        # Try to extract JSON
        data = json.loads(response.content)
        data["question_type"] = question_type.value
        return data
    except json.JSONDecodeError:
        # Try to extract from markdown code block
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                data["question_type"] = question_type.value
                return data
            except json.JSONDecodeError:
                pass
        return None


async def batch_generate_questions(
    knowledge_point_label: str,
    knowledge_point_content: str,
    count: int = 5,
) -> list[dict]:
    """Generate multiple questions for a knowledge point."""
    questions = []
    for _ in range(count):
        q = await generate_question(knowledge_point_label, knowledge_point_content)
        if q:
            questions.append(q)
    return questions


def _get_api_key(provider_name: str) -> str:
    if provider_name == "claude":
        return settings.claude_api_key
    elif provider_name == "openai":
        return settings.openai_api_key
    elif provider_name == "deepseek":
        return settings.deepseek_api_key
    return ""
