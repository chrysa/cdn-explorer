"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "cdn-explorer"
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Demo mode — serve fixture data from the crawler so the app is fully
    # explorable without reaching any real CDN. A "DEMO" banner is shown in the
    # UI while enabled. Off by default; never enable in production.
    demo_mode: bool = False


settings = Settings()
