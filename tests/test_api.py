from config import Settings
from src.app_factory import create_app
from tests.fakes import (
    DeterministicAIProvider,
    FakeHistoryRepository,
    FakePromptRepository,
)


def build_client():
    history = FakeHistoryRepository()
    app = create_app(
        Settings(),
        prompt_repository=FakePromptRepository(),
        history_repository=history,
        ai_provider=DeterministicAIProvider(),
    )
    app.config.update(TESTING=True)
    return app.test_client(), history


def test_single_generate_returns_response_and_writes_history():
    client, history = build_client()

    response = client.post("/api/v1/generate", json={"userInput": "What is Flask?"})

    assert response.status_code == 200
    assert response.get_json() == {"response": "AI::Expert mode: What is Flask?"}
    assert len(history.items) == 1
    assert history.items[0]["request_type"] == "single"
    assert history.items[0]["user_input"] == "What is Flask?"


def test_single_generate_rejects_empty_input():
    client, _ = build_client()

    response = client.post("/api/v1/generate", json={"userInput": "   "})

    assert response.status_code == 400
    assert "empty" in response.get_json()["error"]


def test_batch_preserves_input_order_even_when_completion_order_differs():
    client, history = build_client()

    response = client.post(
        "/api/v1/generate/batch",
        json={"userInputs": ["slow first", "fast second", "fast third"]},
    )

    assert response.status_code == 200
    assert response.get_json()["responses"] == [
        "AI::Expert mode: slow first",
        "AI::Expert mode: fast second",
        "AI::Expert mode: fast third",
    ]
    assert len(history.items) == 3
    assert sorted(item["item_index"] for item in history.items) == [0, 1, 2]


def test_batch_rejects_non_list_payload():
    client, _ = build_client()

    response = client.post(
        "/api/v1/generate/batch",
        json={"userInputs": "not-a-list"},
    )

    assert response.status_code == 400
    assert "list" in response.get_json()["error"]
