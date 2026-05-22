import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.connection import get_db
from app.knowledge.ingestion import ingest_text, ingest_file, list_documents, delete_document
from app.utils.file_utils import is_supported_file
from app.web.templates import templates

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/", response_class=HTMLResponse)
async def knowledge_list(request: Request, db: AsyncSession = Depends(get_db)):
    docs = await list_documents(db)
    return templates.TemplateResponse(
        request=request,
        name="knowledge/list.html",
        context={"documents": docs},
    )


@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="knowledge/upload.html",
        context={},
    )


@router.post("/upload")
async def upload_file(
    request: Request,
    db: AsyncSession = Depends(get_db),
    file: UploadFile | None = File(None),
    title: str = Form(""),
    text_content: str = Form(""),
    tags: str = Form(""),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    if file and file.filename:
        if not is_supported_file(file.filename):
            return templates.TemplateResponse(
                request=request,
                name="knowledge/upload.html",
                context={"error": f"不支持的文件类型: {file.filename}"},
            )
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = upload_dir / safe_name
        content = await file.read()
        file_path.write_bytes(content)

        doc_title = title or Path(file.filename).stem
        doc = await ingest_file(db, str(file_path), title=doc_title, tags=tag_list)
    elif text_content.strip():
        doc_title = title or "粘贴文本"
        doc = await ingest_text(db, doc_title, text_content, tags=tag_list)
    else:
        return templates.TemplateResponse(
            request=request,
            name="knowledge/upload.html",
            context={"error": "请选择文件或输入文本内容"},
        )

    # 清除该文档的块缓存
    try:
        from app.web.routes.chat_routes import invalidate_chunk_cache
        invalidate_chunk_cache(doc.id)
    except Exception:
        pass
    return templates.TemplateResponse(
        request=request,
        name="knowledge/upload.html",
        context={"success": True},
    )


@router.get("/{doc_id}", response_class=HTMLResponse)
async def knowledge_detail(request: Request, doc_id: int, db: AsyncSession = Depends(get_db)):
    doc = await db.get(__import__("app.database.models", fromlist=["Document"]).Document, doc_id)
    if not doc:
        return templates.TemplateResponse(
            request=request,
            name="knowledge/list.html",
            context={"error": "文档不存在"},
        )
    return templates.TemplateResponse(
        request=request,
        name="knowledge/detail.html",
        context={"doc": doc},
    )


@router.post("/{doc_id}/delete")
async def delete_doc(doc_id: int, db: AsyncSession = Depends(get_db)):
    try:
        from app.web.routes.chat_routes import invalidate_chunk_cache
        invalidate_chunk_cache(doc_id)
    except Exception:
        pass
    await delete_document(db, doc_id)
    return RedirectResponse(url="/knowledge", status_code=303)
