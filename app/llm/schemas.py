from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]  # [{"role": "user", "content": "..."}]
    system: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    model: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    content: str
    model: str
    usage_input_tokens: int = 0
    usage_output_tokens: int = 0
    finish_reason: str | None = None


class EmbeddingRequest(BaseModel):
    texts: list[str]
    model: str | None = None


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    usage_total_tokens: int = 0
