from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "production"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/iris_rag"
    SQLITE_URL: str = "sqlite:///iris_rag.db"
    APP_TITLE: str = "Iris RAG API"
    APP_VERSION: str = "1.0.0"

    def get_database_url(self) -> str:
        if self.ENV == "development":
            return self.SQLITE_URL
        return self.DATABASE_URL

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
