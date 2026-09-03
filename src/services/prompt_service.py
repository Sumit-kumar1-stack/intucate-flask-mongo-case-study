from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import uuid4

from src.domain.errors import PromptNotFoundError, ValidationError
from src.services.ai_provider import AIProvider


class PromptRepository(Protocol):
    def get_template(self, prompt_id: str) -> str | None:
        ...


class HistoryRepository(Protocol):
    def save_pair(self, payload: dict[str, Any]) -> str:
        ...


@dataclass(frozen=True)
class PromptServiceConfig:
    prompt_id: str
    max_input_chars: int
    max_batch_size: int


class PromptService:
    def __init__(
        self,
        prompt_repository: PromptRepository,
        history_repository: HistoryRepository,
        ai_provider: AIProvider,
        config: PromptServiceConfig,
    ) -> None:
        self._prompts = prompt_repository
        self._history = history_repository
        self._ai = ai_provider
        self._config = config

    def _validate_single(self, value: object) -> str:
        if not isinstance(value, str):
            raise ValidationError("userInput must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValidationError("userInput cannot be empty")
        if len(cleaned) > self._config.max_input_chars:
            raise ValidationError(
                f"userInput cannot exceed {self._config.max_input_chars} characters"
            )
        return cleaned

    def _validate_batch(self, values: object) -> list[str]:
        if not isinstance(values, list):
            raise ValidationError("userInputs must be a list of strings")
        if not values:
            raise ValidationError("userInputs cannot be empty")
        if len(values) > self._config.max_batch_size:
            raise ValidationError(
                f"userInputs cannot contain more than {self._config.max_batch_size} items"
            )
        return [self._validate_single(value) for value in values]

    async def _load_template(self) -> str:
        template = await asyncio.to_thread(
            self._prompts.get_template, self._config.prompt_id
        )
        if template is None:
            raise PromptNotFoundError(
                f"Prompt '{self._config.prompt_id}' was not found in MongoDB"
            )
        if "{{userInput}}" not in template:
            raise ValidationError("Stored prompt template is missing {{userInput}}")
        return template

    @staticmethod
    def _render(template: str, user_input: str) -> str:
        return template.replace("{{userInput}}", user_input)

    async def _process_one(
        self,
        *,
        user_input: str,
        template: str,
        request_id: str,
        request_type: str,
        item_index: int | None,
    ) -> str:
        final_prompt = self._render(template, user_input)
        response = await self._ai.generate(final_prompt)

        await asyncio.to_thread(
            self._history.save_pair,
            {
                "request_id": request_id,
                "request_type": request_type,
                "item_index": item_index,
                "prompt_id": self._config.prompt_id,
                "user_input": user_input,
                "final_prompt": final_prompt,
                "response": response,
            },
        )
        return response

    async def generate_one(self, raw_user_input: object) -> dict[str, str]:
        user_input = self._validate_single(raw_user_input)
        template = await self._load_template()
        request_id = str(uuid4())
        response = await self._process_one(
            user_input=user_input,
            template=template,
            request_id=request_id,
            request_type="single",
            item_index=None,
        )
        return {"response": response}

    async def generate_many(self, raw_user_inputs: object) -> dict[str, list[str]]:
        user_inputs = self._validate_batch(raw_user_inputs)
        template = await self._load_template()
        request_id = str(uuid4())

        tasks = [
            self._process_one(
                user_input=user_input,
                template=template,
                request_id=request_id,
                request_type="batch",
                item_index=index,
            )
            for index, user_input in enumerate(user_inputs)
        ]

        # asyncio.gather executes independent I/O-bound calls concurrently while
        # preserving the order of the input awaitables in its returned result list.
        responses = await asyncio.gather(*tasks)
        return {"responses": responses}
