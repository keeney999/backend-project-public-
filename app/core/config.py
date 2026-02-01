from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator, ValidationInfo


class Settings(BaseSettings):
    """Настройки приложения."""

    PROJECT_NAME: str = "FastAPI Notes API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Собирает DSN для подключения к PostgreSQL."""
        if isinstance(v, str):
            return v

        data = info.data
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_SERVER"),
            path=f"{data.get('POSTGRES_DB') or ''}",
        ))

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()