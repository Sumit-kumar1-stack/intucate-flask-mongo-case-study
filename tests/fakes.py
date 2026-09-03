from __future__ import annotations

import asyncio
from typing import Any


class FakePromptRepository:
    def __init__(self, template: str | None = None) -> None:
        self.template = template or "Expert mode: {{userInput}}"

    def get_template(self, prompt_id: str) -> str | None:
        return self.template


class FakeHistoryRepository:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def save_pair(self, payload: dict[str, Any]) -> str:
        self.items.append(payload.copy())
        return str(len(self.items))


class DeterministicAIProvider:
    async def generate(self, prompt: str) -> str:
        # Make the first input slower to prove that gather still preserves order.
        delay = 0.05 if "slow" in prompt else 0.005
        await asyncio.sleep(delay)
        return f"AI::{prompt}"
