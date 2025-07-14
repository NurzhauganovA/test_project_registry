from typing import List, Set

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: List[str] = []
    ACTIONS_ON_USERS_KAFKA_TOPIC: str = "auth_service.user.actions"
    KAFKA_GROUP_ID: str = "registry-service-users-group"


class Settings(BaseSettings):
    # FastAPI app params
    APP_PORT: int = 8002
    APP_HOST: str = "localhost"
    PROJECT_NAME: str = "Registry Service [ORKENDEU]"
    PROJECT_VERSION: str = "0.0.2"
    API_PREFIX: str = "/api/v1"
    API_ENABLE_DOCS: bool = True
    BACKEND_CORS_ORIGINS: List[str] = []
    DEBUG: bool = True

    # Database params
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20

    # i18 params
    LANGUAGES: Set[str] = {"ru", "kk", "en"}
    DEFAULT_LANGUAGE: str = "ru"

    # httpx params
    TIMEOUT: int = 5
    MAX_KEEPALIVE_CONNECTIONS: int = 10
    MAX_CONNECTIONS: int = 100

    # Auth Service params
    AUTH_SERVICE_BASE_URL: str = "https://auth-service-app-dev:8001/api/v1"

    # RPN Integration Service params
    RPN_INTEGRATION_SERVICE_BASE_URL: str = "https://rpn-integration-service:8010"

    # Kafka params
    kafka: KafkaSettings = KafkaSettings()

    @field_validator(
        "AUTH_SERVICE_BASE_URL",
        "RPN_INTEGRATION_SERVICE_BASE_URL",
        mode="before",
    )
    def must_be_https(cls, v):
        # if not isinstance(v, str) or not v.startswith("https://"):
        #     raise ValueError(f"{v} must start with 'https://'.")
        return v

    @property
    def DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        validate_environment=True,
    )


project_settings = Settings()
