"""
聊天 API — 基于知识库的问答
用户提问 → 搜索激活知识库 → LLM 回答
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db, async_session_factory
from app.database.models import DocumentChunk
from app.knowledge.vector_store import VectorStore
from app.llm.base import LLMMessage, LLMConfig, LLMRole
from app.llm.factory import get_provider
from app.config import settings


import time
from collections import OrderedDict

# ─── 文档块内存缓存（避免重复查库） ───
_chunk_cache = OrderedDict()  # {doc_id: {chunks: [...], timestamp: float}}
_CACHE_TTL = 300  # 5 分钟过期

async def _get_cached_chunks(document_id: int | None) -> list:
    """获取文档块，优先从内存缓存读取"""
    now = time.time()

    # 全局搜索（无 document_id）：查 DB
    if document_id is None:
        async with async_session_factory() as session:
            result = await session.execute(select(DocumentChunk).limit(50))
            return result.scalars().all()

    # 按文档缓存
    cache_key = f'doc_{document_id}'
    entry = _chunk_cache.get(cache_key)
    if entry and (now - entry['timestamp']) < _CACHE_TTL:
        return entry['chunks']

    # 缓存未命中，查 DB
    async with async_session_factory() as session:
        result = await session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id).limit(50)
        )
        chunks = result.scalars().all()

    _chunk_cache[cache_key] = {'chunks': chunks, 'timestamp': now}
    if len(_chunk_cache) > 50:  # 最多缓存 50 个文档
        _chunk_cache.popitem(last=False)
    return chunks

def invalidate_chunk_cache(document_id: int | None = None):
    """文档更新时清除缓存"""
    if document_id is None:
        _chunk_cache.clear()
    else:
        _chunk_cache.pop(f'doc_{document_id}', None)

router = APIRouter(prefix="/api", tags=["chat"])

CHAT_SYSTEM = """你是熊猫学习助手，一个基于知识库的 AI 导师。
请用中文回答用户的问题，基于提供的参考资料。
如果资料不足以回答问题，诚实地告诉用户你不知道。
回答要简洁易懂，适当举例说明。"""


def _get_api_key() -> str:
    p = settings.llm_provider
    if p == "claude":
        return settings.claude_api_key
    elif p == "openai":
        return settings.openai_api_key
    elif p == "deepseek":
        return settings.deepseek_api_key
    return ""


async def search_chunks(query: str, max_results: int = 5, document_id: int | None = None) -> list[str]:
    """搜索知识库中的相关文本块，可限定在指定文档内搜索"""

    # 从缓存获取文档块
    chunks = await _get_cached_chunks(document_id)

    # 尝试向量搜索
    provider_name = settings.llm_provider
    api_key = _get_api_key()
    if api_key:
        try:
            provider = get_provider(provider_name, api_key)
            embedding = await provider.embed([query])
            vs = VectorStore()
            filter_dict = {"document_id": document_id} if document_id else None
            results = vs.semantic_search(embedding[0], top_k=max_results, filter=filter_dict)
            if results:
                return [r["content"] for r in results]
        except (NotImplementedError, Exception):
            pass

    # 降级：关键词匹配搜索（从缓存读取）
    keywords = [w for w in query.split() if len(w) > 1]

    if keywords:
        scored = []
        for c in chunks:
            score = sum(1 for kw in keywords if kw.lower() in c.content.lower())
            if score > 0:
                scored.append((score, c.content))
        scored.sort(key=lambda x: -x[0])
        if scored:
            return [c for _, c in scored[:max_results]]

    return [c.content for c in chunks[:max_results]]


@router.post("/chat")
async def chat(
    message: str = Form(...),
    knowledge_base_id: str = Form(""),
):
    """处理聊天消息，按激活知识库范围搜索并回答"""
    if not message.strip():
        return HTMLResponse("")

    api_key = _get_api_key()
    if not api_key:
        return HTMLResponse(
            '<div class="chat-message bot"><div class="msg-label">🐼 熊猫</div>'
            '⚠️ 请先在设置页面配置 API Key 并保存</div>'
        )

    # 解析知识库 ID（限定搜索范围到指定文档）
    doc_id = int(knowledge_base_id) if knowledge_base_id and knowledge_base_id.isdigit() else None

    # 搜索激活的知识库
    contexts = await search_chunks(message, document_id=doc_id)
    context_text = "\n\n".join(contexts[:3]) if contexts else ""

    # 构建 prompt，提示用户当前问了哪个知识库
    context_hint = ""
    if doc_id:
        from app.database.connection import async_session_factory
        from app.database.models import Document
        async with async_session_factory() as session:
            doc = await session.get(Document, doc_id)
            if doc:
                context_hint = f"（搜索范围：{doc.title}）"

    if context_text:
        user_prompt = f"基于以下资料回答用户问题：\n\n{context_text[:6000]}\n\n问题：{message}"
    else:
        user_prompt = f"回答用户问题：{message}"

    # 调用 LLM
    try:
        provider = get_provider(settings.llm_provider, api_key)
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content=CHAT_SYSTEM),
            LLMMessage(role=LLMRole.USER, content=user_prompt),
        ]
        config = LLMConfig(temperature=0.7, max_tokens=2048)
        response = await provider.chat(messages, config)

        answer_html = response.content.replace("\n", "<br>")
        return HTMLResponse(
            f'<div class="chat-message user"><div class="msg-label">你{context_hint}</div>{message}</div>'
            f'<div class="chat-message bot"><div class="msg-label">🐼 熊猫</div>{answer_html}</div>'
        )
    except Exception as e:
        return HTMLResponse(
            f'<div class="chat-message bot"><div class="msg-label">🐼 熊猫</div>'
            f'出错了：{str(e)}</div>'
        )
