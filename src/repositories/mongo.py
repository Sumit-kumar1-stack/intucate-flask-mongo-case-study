from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database


class MongoConnection:
    def __init__(self, uri: str, database_name: str) -> None:
        self._client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        self._database = self._client[database_name]

    @property
    def database(self) -> Database:
        return self._database

    def ping(self) -> None:
        self._client.admin.command("ping")

    def close(self) -> None:
        self._client.close()


class MongoPromptRepository:
    def __init__(self, database: Database) -> None:
        self._collection = database["prompts"]

    def get_template(self, prompt_id: str) -> str | None:
        document = self._collection.find_one({"_id": prompt_id}, {"template": 1})
        if not document:
            return None
        template = document.get("template")
        return template if isinstance(template, str) else None

    def upsert_default(self, prompt_id: str, template: str) -> None:
        now = datetime.now(timezone.utc)
        self._collection.update_one(
            {"_id": prompt_id},
            {
                "$set": {"template": template, "updated_at": now},
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )


class MongoHistoryRepository:
    def __init__(self, database: Database) -> None:
        self._collection = database["history"]
        self._collection.create_index("request_id")
        self._collection.create_index("created_at")

    def save_pair(self, payload: dict[str, Any]) -> str:
        document = {
            **payload,
            "created_at": datetime.now(timezone.utc),
        }
        result = self._collection.insert_one(document)
        return str(result.inserted_id)
