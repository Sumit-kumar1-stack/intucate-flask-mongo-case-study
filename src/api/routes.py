from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from src.domain.errors import AIProviderError, PromptNotFoundError, ValidationError


api = Blueprint("api", __name__, url_prefix="/api/v1")


def _service():
    return current_app.extensions["prompt_service"]


@api.post("/generate")
async def generate_single():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        result = await _service().generate_one(body.get("userInput"))
        return jsonify(result), 200
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except PromptNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except AIProviderError as exc:
        return jsonify({"error": str(exc)}), 502


@api.post("/generate/batch")
async def generate_batch():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        result = await _service().generate_many(body.get("userInputs"))
        return jsonify(result), 200
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except PromptNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    except AIProviderError as exc:
        return jsonify({"error": str(exc)}), 502
