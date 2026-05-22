"""
练习模块 — 上下文感知的卡片测验
自动基于当前学习内容出题，非聊天模式
"""

import json
import datetime
import random

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db, async_session_factory
from app.database.models import Document, DocumentChunk, KnowledgePoint
from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings
from app.web.templates import templates

router = APIRouter(prefix="/practice", tags=["practice"])

QUIZ_SYSTEM = "你是一个出题老师。请根据提供的资料生成练习题，用中文。"


def _get_api_key() -> str:
    p = settings.llm_provider
    if p == "claude":
        return settings.claude_api_key
    elif p == "openai":
        return settings.openai_api_key
    elif p == "deepseek":
        return settings.deepseek_api_key
    return ""


async def generate_quiz(file_id: int, question_count: int = 5) -> list[dict]:
    """基于文档内容自动生成测验题目"""
    api_key = _get_api_key()
    if not api_key:
        return []

    # 获取文档内容
    async with async_session_factory() as session:
        doc = await session.get(Document, file_id)
        if not doc or not doc.raw_text:
            return []
        text = doc.raw_text[:6000]  # 截取前6000字符

    provider = get_provider(settings.llm_provider, api_key)

    prompt = (
        f"根据以下资料生成 {question_count} 道练习题。\n\n"
        f"资料内容：\n{text}\n\n"
        "请严格按照以下 JSON 格式输出（不要其他内容）：\n"
        '{"questions": [\n'
        '  {\n'
        '    "type": "choice",\n'
        '    "question": "题目内容",\n'
        '    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],\n'
        '    "answer": "A",\n'
        '    "explanation": "解析"\n'
        '  },\n'
        '  {\n'
        '    "type": "judge",\n'
        '    "question": "判断题内容",\n'
        '    "answer": "对",\n'
        '    "explanation": "解析"\n'
        '  },\n'
        '  {\n'
        '    "type": "fill",\n'
        '    "question": "填空题（用____标空白）",\n'
        '    "answer": "正确答案",\n'
        '    "explanation": "解析"\n'
        '  }\n'
        ']}'
    )

    messages = [
        LLMMessage(role=LLMRole.SYSTEM, content=QUIZ_SYSTEM),
        LLMMessage(role=LLMRole.USER, content=prompt),
    ]
    config = LLMConfig(temperature=0.7, max_tokens=4096)

    try:
        response = await provider.chat(messages, config)
        data = json.loads(response.content)
        questions = data.get("questions", [])
        # 限量和打乱
        random.shuffle(questions)
        return questions[:question_count]
    except (json.JSONDecodeError, Exception):
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.content)
        if match:
            try:
                data = json.loads(match.group(1))
                questions = data.get("questions", [])
                random.shuffle(questions)
                return questions[:question_count]
            except Exception:
                pass
        return []


@router.get("/", response_class=HTMLResponse)
async def practice_home(request: Request, db: AsyncSession = Depends(get_db)):
    """练习首页 — 自动基于当前学习上下文出题"""
    # 检查文档数量
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0

    error = request.query_params.get("error", "")
    return templates.TemplateResponse(
        request=request,
        name="practice/index.html",
        context={
            "doc_count": doc_count,
            "error": error,
        },
    )


@router.post("/start")
async def start_quiz(
    file_id: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    """基于指定文档或当前学习上下文生成测验"""
    # 检查 API Key 是否配置
    from app.config import settings as _st
    api_key = _st.deepseek_api_key or _st.claude_api_key or _st.openai_api_key
    if not api_key:
        return RedirectResponse(url="/practice?error=请先在设置页面配置 API Key", status_code=303)

    target_id = file_id

    # 如果没传 file_id，尝试获取最新文档
    if not target_id:
        result = await db.execute(
            select(Document).order_by(Document.imported_at.desc()).limit(1)
        )
        doc = result.scalar_one_or_none()
        if doc:
            target_id = doc.id

    if not target_id:
        return RedirectResponse(url="/practice", status_code=303)

    # 生成题目并存入 session
    questions = await generate_quiz(target_id)

    if not questions:
        return RedirectResponse(url="/practice?error=出题失败，请检查API配置", status_code=303)

    # 存入临时 quiz session（简化处理，直接渲染页面）
    # 用 query param 传递 JSON（短数据可行）
    q_json = json.dumps(questions, ensure_ascii=False)
    return RedirectResponse(url=f"/practice/quiz?q={q_json}", status_code=303)


@router.get("/quiz", response_class=HTMLResponse)
async def show_quiz(request: Request, q: str = ""):
    """显示测验题目"""
    try:
        questions = json.loads(q)
    except Exception:
        return RedirectResponse(url="/practice", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="practice/quiz.html",
        context={
            "questions": questions,
            "total": len(questions),
        },
    )
