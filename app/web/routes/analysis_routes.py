"""
分析模块 — 文档摘要 / 概念提取 / 学习报告
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import Document, AnalysisCache
from app.web.templates import templates
from app.analysis.summarizer import generate_summary
from app.analysis.concept_extractor import extract_and_save_concepts
from app.analysis.relation_finder import find_relations
from app.analysis.report_generator import generate_learning_report
from app.config import settings

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _has_api_key() -> bool:
    return bool(settings.deepseek_api_key or settings.claude_api_key or settings.openai_api_key)


@router.get("/", response_class=HTMLResponse)
async def analysis_home(request: Request, db: AsyncSession = Depends(get_db)):
    report = await generate_learning_report(db)

    result = await db.execute(
        select(Document).order_by(Document.imported_at.desc())
    )
    documents = result.scalars().all()

    error = request.query_params.get("error", "")

    return templates.TemplateResponse(
        request=request,
        name="analysis/index.html",
        context={
            "report": report,
            "documents": documents,
            "error": error,
            "has_api_key": _has_api_key(),
        },
    )


@router.post("/summarize/{doc_id}")
async def analyze_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    if not _has_api_key():
        return RedirectResponse(
            url=f"/analysis?error=请先在设置页面配置 API Key",
            status_code=303,
        )

    doc = await db.get(Document, doc_id)
    if doc is None:
        return RedirectResponse(url="/analysis", status_code=303)

    # 检查缓存
    result = await db.execute(
        select(AnalysisCache).where(
            AnalysisCache.document_id == doc_id,
            AnalysisCache.analysis_type == "summary",
        )
    )
    cached = result.scalar_one_or_none()
    if cached:
        return RedirectResponse(url=f"/knowledge/{doc_id}", status_code=303)

    # 生成摘要
    if not doc.raw_text:
        return RedirectResponse(
            url=f"/analysis?error=文档内容为空，无法生成摘要",
            status_code=303,
        )

    try:
        summary = await generate_summary(doc.raw_text)
        doc.summary = summary

        cache = AnalysisCache(
            document_id=doc_id,
            analysis_type="summary",
            result=summary,
        )
        db.add(cache)
        await db.commit()
        return RedirectResponse(url=f"/knowledge/{doc_id}", status_code=303)
    except Exception as e:
        return RedirectResponse(
            url=f"/analysis?error=生成摘要失败：{str(e)[:50]}",
            status_code=303,
        )


@router.post("/extract-concepts/{doc_id}")
async def extract_doc_concepts(doc_id: int, db: AsyncSession = Depends(get_db)):
    if not _has_api_key():
        return RedirectResponse(
            url=f"/analysis?error=请先在设置页面配置 API Key",
            status_code=303,
        )

    doc = await db.get(Document, doc_id)
    if doc is None or not doc.raw_text:
        return RedirectResponse(url="/analysis", status_code=303)

    try:
        await extract_and_save_concepts(doc.raw_text, doc_id, db)
        return RedirectResponse(
            url="/learning/?extracted=1",
            status_code=303,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/analysis?error=概念提取失败：{str(e)[:50]}",
            status_code=303,
        )
