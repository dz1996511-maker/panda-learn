from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator


class LLMRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    role: LLMRole
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    usage_input_tokens: int
    usage_output_tokens: int
    finish_reason: str | None = None


@dataclass
class LLMConfig:
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str | None = None
    stream: bool = False


class BaseLLMProvider(ABC):
    """Abstract interface all LLM providers must implement."""

    def __init__(self, api_key: str, default_model: str | None = None):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    async def chat(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> LLMResponse:
        """Send a chat request and return the full response."""
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> AsyncIterator[str]:
        """Yield content chunks as they arrive."""
        ...
        yield  # pragma: no cover

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for the given texts."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...
