from config import settings
from src.app_factory import create_app


app = create_app(settings)


if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
