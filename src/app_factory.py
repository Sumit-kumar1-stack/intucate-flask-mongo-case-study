from __future__ import annotations

from flask import Flask, jsonify

from config import Settings
from src.api.routes import api
from src.repositories.mongo import (
    MongoConnection,
    MongoHistoryRepository,
    MongoPromptRepository,
)
from src.services.ai_provider import AIProvider, MockAIProvider, OpenAIProvider
from src.services.prompt_service import PromptService, PromptServiceConfig


def build_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "mock":
        return MockAIProvider()
    if settings.ai_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    raise RuntimeError("AI_PROVIDER must be either 'mock' or 'openai'")


def create_app(
    settings: Settings,
    *,
    prompt_repository=None,
    history_repository=None,
    ai_provider: AIProvider | None = None,
    mongo_connection: MongoConnection | None = None,
) -> Flask:
    app = Flask(__name__)

    connection = mongo_connection
    if prompt_repository is None or history_repository is None:
        connection = connection or MongoConnection(
            settings.mongo_uri, settings.mongo_db_name
        )
        prompt_repository = prompt_repository or MongoPromptRepository(
            connection.database
        )
        history_repository = history_repository or MongoHistoryRepository(
            connection.database
        )

    provider = ai_provider or build_ai_provider(settings)

    app.extensions["prompt_service"] = PromptService(
        prompt_repository,
        history_repository,
        provider,
        PromptServiceConfig(
            prompt_id=settings.prompt_id,
            max_input_chars=settings.max_input_chars,
            max_batch_size=settings.max_batch_size,
        ),
    )
    if connection is not None:
        app.extensions["mongo_connection"] = connection

    app.register_blueprint(api)

    @app.get("/health")
    def health():
        mongo = app.extensions.get("mongo_connection")
        if mongo is None:
            return jsonify({"status": "ok", "database": "injected-test-repository"})
        try:
            mongo.ping()
            return jsonify({"status": "ok", "database": "reachable"}), 200
        except Exception:
            return jsonify({"status": "degraded", "database": "unreachable"}), 503

    return app
