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

import uuid
import time

# 内存题目存储（避免 URL 传 JSON 的脆弱性）
_quiz_store = {}  # {quiz_id: {questions: [...], timestamp: float}}
_QUIZ_TTL = 600  # 10 分钟过期

def _clean_old_quizzes():
    now = time.time()
    expired = [k for k, v in _quiz_store.items() if now - v['timestamp'] > _QUIZ_TTL]
    for k in expired:
        _quiz_store.pop(k, None)

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

    # 存入内存存储
    _clean_old_quizzes()
    quiz_id = uuid.uuid4().hex[:12]
    _quiz_store[quiz_id] = {'questions': questions, 'timestamp': time.time()}
    return RedirectResponse(url=f"/practice/quiz/{quiz_id}", status_code=303)


@router.get("/quiz/{quiz_id}", response_class=HTMLResponse)
async def show_quiz(request: Request, quiz_id: str):
    """显示测验题目"""
    entry = _quiz_store.get(quiz_id)
    if not entry:
        return RedirectResponse(url="/practice?error=题目已过期，请重新出题", status_code=303)
    questions = entry['questions']

    return templates.TemplateResponse(
        request=request,
        name="practice/quiz.html",
        context={
            "questions": questions,
            "total": len(questions),
        },
    )
