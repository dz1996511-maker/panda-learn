from typing import AsyncIterator

from openai import AsyncOpenAI

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, LLMConfig, LLMRole


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, default_model: str | None = None):
        super().__init__(api_key, default_model)
        self._client = AsyncOpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def chat(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> LLMResponse:
        cfg = config or LLMConfig()
        model = cfg.model or self.default_model or "gpt-4o"

        openai_messages = []
        if cfg.system_prompt:
            openai_messages.append({"role": "system", "content": cfg.system_prompt})
        openai_messages.extend(
            {"role": m.role.value, "content": m.content}
            for m in messages
        )

        resp = await self._client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )

        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=resp.model,
            usage_input_tokens=resp.usage.prompt_tokens if resp.usage else 0,
            usage_output_tokens=resp.usage.completion_tokens if resp.usage else 0,
            finish_reason=choice.finish_reason,
        )

    async def chat_stream(self, messages: list[LLMMessage], config: LLMConfig | None = None) -> AsyncIterator[str]:
        cfg = config or LLMConfig()
        model = cfg.model or self.default_model or "gpt-4o"

        openai_messages = []
        if cfg.system_prompt:
            openai_messages.append({"role": "system", "content": cfg.system_prompt})
        openai_messages.extend(
            {"role": m.role.value, "content": m.content}
            for m in messages
        )

        stream = await self._client.chat.completions.create(
            model=model,
            messages=openai_messages,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def embed(self, texts: list[str]) -> list[list[float]]:
        model = "text-embedding-3-small"
        resp = await self._client.embeddings.create(
            model=model,
            input=texts,
        )
        return [item.embedding for item in resp.data]
