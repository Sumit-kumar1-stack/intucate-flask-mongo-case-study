from __future__ import annotations

from dataclasses import dataclass, field
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = field(
        default_factory=lambda: os.getenv("MONGO_URI", "mongodb://localhost:27017")
    )
    mongo_db_name: str = field(
        default_factory=lambda: os.getenv("MONGO_DB_NAME", "intucate_case_study")
    )
    prompt_id: str = field(
        default_factory=lambda: os.getenv("PROMPT_ID", "Education_Prompt")
    )
    ai_provider: str = field(
        default_factory=lambda: os.getenv("AI_PROVIDER", "mock").lower()
    )
    openai_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    )
    host: str = field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "5000")))
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "0") == "1")
    max_input_chars: int = field(
        default_factory=lambda: int(os.getenv("MAX_INPUT_CHARS", "4000"))
    )
    max_batch_size: int = field(
        default_factory=lambda: int(os.getenv("MAX_BATCH_SIZE", "25"))
    )


settings = Settings()
