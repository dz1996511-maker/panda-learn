from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.models import SettingsModel
from app.config import settings as app_settings
from app.web.templates import templates

router = APIRouter(prefix="/settings", tags=["settings"])


async def _set_setting(db: AsyncSession, key: str, value: str):
    result = await db.get(SettingsModel, key)
    if result:
        result.value = value
    else:
        db.add(SettingsModel(key=key, value=value))
    await db.commit()


@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings/index.html",
        context={
            "deepseek_api_key": app_settings.deepseek_api_key,
            "deepseek_model": app_settings.deepseek_model,
        },
    )


@router.post("/save")
async def save_settings(
    llm_provider: str = Form("deepseek"),
    claude_api_key: str = Form(""),
    claude_model: str = Form(""),
    openai_api_key: str = Form(""),
    openai_model: str = Form(""),
    deepseek_api_key: str = Form(""),
    deepseek_model: str = Form("deepseek-chat"),
    db: AsyncSession = Depends(get_db),
):
    await _set_setting(db, "llm_provider", "deepseek")
    await _set_setting(db, "deepseek_api_key", deepseek_api_key)
    await _set_setting(db, "deepseek_model", deepseek_model)

    app_settings.llm_provider = "deepseek"
    if deepseek_api_key:
        app_settings.deepseek_api_key = deepseek_api_key
    app_settings.deepseek_model = deepseek_model

    return RedirectResponse(url="/settings", status_code=303)
