from contextlib import asynccontextmanager
from pathlib import Path

import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import init_db, get_db
from app.database.models import Document, KnowledgePoint, SpacedRepetition, SettingsModel
from app.web.routes import knowledge_routes, learning_routes, practice_routes, analysis_routes, settings_routes, chat_routes, kb_store_routes
from app.web.templates import templates
from app.config import settings as app_settings


async def load_settings_from_db():
    """从数据库加载持久化的设置到内存配置（重启不丢失）"""
    from app.database.connection import async_session_factory
    async with async_session_factory() as session:
        result = await session.execute(select(SettingsModel))
        for row in result.scalars().all():
            key = row.key
            val = row.value
            if hasattr(app_settings, key):
                setattr(app_settings, key, val)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await load_settings_from_db()
    yield


app = FastAPI(title="熊猫学习", lifespan=lifespan)

# Static files
static_dir = Path(__file__).parent / "web" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routes
app.include_router(knowledge_routes.router)
app.include_router(learning_routes.router)
app.include_router(practice_routes.router)
app.include_router(analysis_routes.router)
app.include_router(settings_routes.router)
app.include_router(chat_routes.router)
app.include_router(kb_store_routes.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/check-api-key")
async def check_api_key():
    """检查是否配置了 API Key（前端用来显示横幅）"""
    has_key = bool(app_settings.deepseek_api_key or app_settings.claude_api_key or app_settings.openai_api_key)
    return JSONResponse({"configured": has_key})


@app.get("/api/stats")
async def api_stats(db: AsyncSession = Depends(get_db)):
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    kp_count = (await db.execute(select(func.count(KnowledgePoint.id)))).scalar() or 0
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    due_count = (await db.execute(
        select(func.count(SpacedRepetition.id)).where(SpacedRepetition.next_review_at <= now)
    )).scalar() or 0
    return JSONResponse({
        "document_count": doc_count,
        "knowledge_point_count": kp_count,
        "due_count": due_count,
    })

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_msg = str(exc)
    print(f"[ERROR] {error_msg}")
    traceback.print_exc()
    return HTMLResponse(
        f'<div style="padding:40px;background:#080808;color:#e0e0e0;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:sans-serif;">'
        f'<div style="font-size:48px;margin-bottom:16px;">🐼</div>'
        f'<h2 style="color:#ff6b6b;margin-bottom:8px;">出错了</h2>'
        f'<p style="color:#888;margin-bottom:20px;max-width:400px;text-align:center;">{error_msg}</p>'
        f'<a href="/" class="btn" style="color:#4fc3f7;">← 返回首页</a>'
        f'</div>',
        status_code=500,
    )

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        status_code=404,
    )
