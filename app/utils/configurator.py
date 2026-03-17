from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class AppConfig(BaseConfig):
    name: str = "z-api"
    display_name: str = "Z API"
    version: str = "26.0.1"

    host: str = Field(alias="APP_HOST", default="0.0.0.0")
    port: int = Field(alias="APP_PORT", default=8000)

    enable_docs: bool = Field(alias="APP_ENABLE_DOCS", default=False)

    proxy_mode: bool = Field(alias="APP_ENABLE_PROXY_MODE", default=False)
    trusted_proxy_ips: list[str] = Field(alias="APP_TRUSTED_PROXY_IPS", default=["*"])


class SecurityConfig(BaseConfig):
    cors_allowed_origins: list[str] = Field(alias="CORS_ALLOWED_ORIGINS", default=["*"])


class Config(BaseConfig):
    debug: bool = Field(alias="DEBUG", default=False)

    app: AppConfig = AppConfig()
    security: SecurityConfig = SecurityConfig()


def read_config() -> Config:
    return Config()
