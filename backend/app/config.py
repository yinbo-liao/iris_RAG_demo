from pathlib import Path

from pydantic_settings import BaseSettings

# Anchor .env to the package's parent (backend/.env) rather than the process CWD,
# so running uvicorn from the repo root still picks up the development settings.
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    ENV: str = "production"
    DATABASE_URL: str = ""
    SQLITE_URL: str = "sqlite:///iris_rag.db"
    APP_TITLE: str = "Iris RAG API"
    APP_VERSION: str = "1.0.0"

    def get_database_url(self) -> str:
        if self.ENV == "development":
            return self.SQLITE_URL
        if not self.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL must be set when ENV is not 'development'. "
                "Set it via the environment or backend/.env."
            )
        return self.DATABASE_URL

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
