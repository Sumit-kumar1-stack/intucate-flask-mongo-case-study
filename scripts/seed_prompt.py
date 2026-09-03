from config import settings
from src.repositories.mongo import MongoConnection, MongoPromptRepository


DEFAULT_TEMPLATE = (
    "You are an expert in education domain. "
    "Answer the following: {{userInput}}"
)


def main() -> None:
    connection = MongoConnection(settings.mongo_uri, settings.mongo_db_name)
    try:
        connection.ping()
        repository = MongoPromptRepository(connection.database)
        repository.upsert_default(settings.prompt_id, DEFAULT_TEMPLATE)
        print(f"Seeded prompt: {settings.prompt_id}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
