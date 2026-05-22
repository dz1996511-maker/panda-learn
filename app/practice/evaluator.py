"""Answer evaluation for different question types."""

import json
from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings


def evaluate_objective(question_type: str, user_answer: str, correct_answer: str) -> bool:
    """Evaluate objective question types (MC, TF, Fill-blank)."""
    if question_type in ("multiple_choice", "true_false"):
        return user_answer.strip().upper() == correct_answer.strip().upper()
    elif question_type == "fill_blank":
        return user_answer.strip().lower() == correct_answer.strip().lower()
    return False


async def evaluate_short_answer(
    user_answer: str,
    reference_answer: str,
    question_text: str,
) -> dict:
    """Evaluate a short answer using LLM for semantic comparison.

    Returns: {"score": 0-5, "feedback": "评价", "is_correct": bool}
    """
    provider_name = settings.llm_provider
    api_key = _get_api_key(provider_name)
    provider = get_provider(provider_name, api_key)

    prompt = (
        f"题目：{question_text}\n\n"
        f"参考答案：{reference_answer}\n\n"
        f"学生答案：{user_answer}\n\n"
        "请评分（0-5分）并提供中文反馈。"
        '用JSON格式输出：{"score": 3, "feedback": "反馈内容"}'
    )

    messages = [
        LLMMessage(role=LLMRole.SYSTEM, content="你是一个老师，请评估学生的答案。"),
        LLMMessage(role=LLMRole.USER, content=prompt),
    ]
    config = LLMConfig(temperature=0.3, max_tokens=1024)

    response = await provider.chat(messages, config)

    try:
        data = json.loads(response.content)
        data["is_correct"] = data.get("score", 0) >= 3
        return data
    except json.JSONDecodeError:
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                data["is_correct"] = data.get("score", 0) >= 3
                return data
            except json.JSONDecodeError:
                pass
        # Fallback
        return {"score": 0, "feedback": "无法评估", "is_correct": False}


def _get_api_key(provider_name: str) -> str:
    if provider_name == "claude":
        return settings.claude_api_key
    elif provider_name == "openai":
        return settings.openai_api_key
    elif provider_name == "deepseek":
        return settings.deepseek_api_key
    return ""
