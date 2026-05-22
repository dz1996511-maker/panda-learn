"""
知识库 Store API — 管理已上传文件 + 当前激活知识库
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import Document, KnowledgePoint

router = APIRouter(prefix="/api/knowledge-store", tags=["kb-store"])


@router.get("/files")
async def list_files(db: AsyncSession = Depends(get_db)):
    """返回所有已上传文档的列表，供前端 Store 初始化"""
    result = await db.execute(
        select(Document).order_by(Document.imported_at.desc())
    )
    docs = result.scalars().all()
    files = [
        {
            "id": str(doc.id),
            "name": doc.title,
            "timestamp": doc.imported_at.isoformat() if doc.imported_at else None,
            "fileSize": doc.char_count or 0,
            "fileType": doc.file_type or doc.source_type,
            "chunkCount": doc.chunk_count or 0,
        }
        for doc in docs
    ]
    return JSONResponse({"files": files})


@router.get("/active")
async def get_active_info(db: AsyncSession = Depends(get_db)):
    """获取当前可用的知识库信息（返回最新文档）"""
    result = await db.execute(
        select(Document).order_by(Document.imported_at.desc()).limit(1)
    )
    doc = result.scalar_one_or_none()
    if doc:
        return JSONResponse({
            "id": str(doc.id),
            "name": doc.title,
            "exists": True,
        })
    return JSONResponse({"id": None, "name": None, "exists": False})
