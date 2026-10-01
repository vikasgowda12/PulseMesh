from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://pulsemesh:pulsemesh_dev@localhost:5433/pulsemesh"
    KAFKA_BOOTSTRAP_SERVERS: str = ""
    KAFKA_TOPIC: str = "incident-events"
    FRONTEND_URLS: str = "http://localhost:5173,http://127.0.0.1:5173"
    GRPC_HOST: str = "127.0.0.1"
    GRPC_PORT: int = 50051

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
