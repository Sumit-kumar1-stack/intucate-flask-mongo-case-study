from __future__ import annotations

import asyncio
from typing import Protocol

from src.domain.errors import AIProviderError


class AIProvider(Protocol):
    async def generate(self, prompt: str) -> str:
        ...


class MockAIProvider:
    """Local provider used so the project runs without paid AI credentials."""

    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(0.05)
        return f"Mock response generated for: {prompt}"


class OpenAIProvider:
    """Optional provider. Install requirements-openai.txt before enabling it."""

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI support is not installed. Run: pip install -r requirements-openai.txt"
            ) from exc

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(self, prompt: str) -> str:
        try:
            response = await self._client.responses.create(
                model=self._model,
                input=prompt,
            )
            text = response.output_text.strip()
            if not text:
                raise AIProviderError("AI provider returned an empty response")
            return text
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError("AI provider request failed") from exc
