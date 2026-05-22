from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import KnowledgePoint, LearningSession, MasteryRecord
from app.learning.engine import (
    start_learning_session,
    end_learning_session,
    record_review,
    get_due_knowledge_points,
)
from app.web.templates import templates

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/", response_class=HTMLResponse)
async def learning_home(request: Request, db: AsyncSession = Depends(get_db)):
    from app.database.models import Document
    from sqlalchemy import func

    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    kp_count = (await db.execute(select(func.count(KnowledgePoint.id)))).scalar() or 0

    result = await db.execute(
        select(KnowledgePoint).order_by(KnowledgePoint.created_at.desc())
    )
    kps = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="learning/index.html",
        context={
            "doc_count": doc_count,
            "kp_count": kp_count,
            "knowledge_points": kps,
        },
    )


@router.get("/start/{kp_id}", response_class=HTMLResponse)
async def learning_session(request: Request, kp_id: int, db: AsyncSession = Depends(get_db)):
    # 检查 API Key 是否配置
    from app.config import settings as _st
    api_key = _st.deepseek_api_key or _st.claude_api_key or _st.openai_api_key
    if not api_key:
        return templates.TemplateResponse(
            request=request,
            name="learning/session.html",
            context={"error": "no_api_key", "knowledge_point": {"id": kp_id, "label": ""}},
        )
    try:
        result = await start_learning_session(db, kp_id)
        return templates.TemplateResponse(
            request=request,
            name="learning/session.html",
            context=result,
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="learning/session.html",
            context={"error": str(e), "knowledge_point": {"id": kp_id, "label": ""}},
        )


@router.post("/end-session")
async def end_session(
    session_id: int = Form(...),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await end_learning_session(db, session_id, notes=notes)
    return RedirectResponse(url="/learning", status_code=303)


@router.post("/review")
async def review_knowledge_point(
    knowledge_point_id: int = Form(...),
    quality: int = Form(...),
    session_id: int = Form(0),
    response_time_ms: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    await record_review(
        db,
        knowledge_point_id=knowledge_point_id,
        quality=quality,
        session_id=session_id if session_id else None,
        response_time_ms=response_time_ms if response_time_ms else None,
    )
    return RedirectResponse(url="/learning", status_code=303)
