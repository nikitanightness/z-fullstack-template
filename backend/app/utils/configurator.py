from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class AppConfig(BaseConfig):
    name: str = "backend"
    display_name: str = "Backend"
    version: str = "26.0"

    host: str = Field(alias="APP_HOST", default="0.0.0.0")
    port: int = Field(alias="APP_PORT", default=8000)

    enable_docs: bool = Field(alias="ENABLE_DOCS", default=False)
    enable_proxy_mode: bool = Field(alias="ENABLE_PROXY_MODE", default=False)


class DatabaseConfig(BaseConfig):
    _db_url: PostgresDsn = Field(
        alias="DATABASE_URL",
        default="postgres+asyncpg://postgres:postgres@postgres:5432/database",
    )

    @property
    def db_url(self) -> str:
        return str(self._db_url)


class SecurityConfig(BaseConfig):
    cors_allowed_origins: list[str] = Field(alias="CORS_ALLOWED_ORIGINS", default=["*"])
    trusted_proxy_ips: list[str] = Field(alias="TRUSTED_PROXY_IPS", default=["*"])


class Config(BaseConfig):
    debug: bool = Field(alias="DEBUG", default=False)

    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    security: SecurityConfig = SecurityConfig()


def read_config() -> Config:
    return Config()
