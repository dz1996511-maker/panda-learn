from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.web.templates import templates
from app.database.models import Document
from app.analysis.summarizer import generate_summary
from app.analysis.concept_extractor import extract_concepts
from app.analysis.relation_finder import find_relations
from app.analysis.report_generator import generate_learning_report

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/", response_class=HTMLResponse)
async def analysis_home(request: Request, db: AsyncSession = Depends(get_db)):
    report = await generate_learning_report(db)

    result = await db.execute(
        __import__("sqlalchemy", fromlist=["select"]).select(Document).order_by(Document.imported_at.desc())
    )
    documents = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="analysis/index.html",
        context={
            "report": report,
            "documents": documents,
        },
    )


@router.post("/summarize/{doc_id}")
async def analyze_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    from app.database.models import AnalysisCache
    import json

    doc = await db.get(Document, doc_id)
    if doc is None:
        return HTMLResponse("文档不存在", status_code=404)

    # Check cache
    result = await db.execute(
        __import__("sqlalchemy", fromlist=["select"]).select(AnalysisCache).where(
            AnalysisCache.document_id == doc_id,
            AnalysisCache.analysis_type == "summary",
        )
    )
    cached = result.scalar_one_or_none()
    if cached:
        return HTMLResponse(cached.result)

    # Generate summary
    if doc.raw_text:
        summary = await generate_summary(doc.raw_text)
        doc.summary = summary

        # Cache it
        cache = AnalysisCache(
            document_id=doc_id,
            analysis_type="summary",
            result=summary,
        )
        db.add(cache)
        await db.commit()

    return RedirectResponse(url=f"/knowledge/{doc_id}", status_code=303)


@router.post("/extract-concepts/{doc_id}")
async def extract_doc_concepts(doc_id: int, db: AsyncSession = Depends(get_db)):
    from app.analysis.concept_extractor import extract_and_save_concepts

    doc = await db.get(Document, doc_id)
    if doc is None or not doc.raw_text:
        return RedirectResponse(url=f"/knowledge/{doc_id}", status_code=303)

    await extract_and_save_concepts(doc.raw_text, doc_id, db)
    return RedirectResponse(url=f"/knowledge/{doc_id}", status_code=303)
