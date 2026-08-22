from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    # =========================================================
    # APPLICATION
    # =========================================================

    app_name: str = "WINGS AI Platform"

    app_env: str = "development"

    app_version: str = "1.0.0"

    debug: bool = True

    # =========================================================
    # DATABASE
    # =========================================================

    database_url: str

    # =========================================================
    # JWT
    # =========================================================

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = 30

    # =========================================================
    # AI / OLLAMA
    # =========================================================

    ollama_base_url: str = "http://ollama:11434"

    ollama_model: str = "qwen2.5:1.5b"

    ollama_embedding_model: str = "nomic-embed-text"

    # Local CPU model can take longer.
    ollama_timeout_seconds: int = 120

    # =========================================================
    # AI PROTECTION
    # =========================================================

    ai_max_prompt_length: int = 4000

    ai_max_output_tokens: int = 128

    ai_temperature: float = 0.1

    # Model is intentionally fixed.
    # Clients cannot select arbitrary models.
    allowed_ai_model: str = "qwen2.5:1.5b"

    # =========================================================
    # JIRA
    # =========================================================

    jira_base_url: str | None = None

    jira_email: str | None = None

    jira_api_token: str | None = None

    jira_project_key: str | None = None

    # =========================================================
    # SERVICENOW
    # =========================================================

    servicenow_base_url: str | None = None

    servicenow_username: str | None = None

    servicenow_password: str | None = None

    # =========================================================
    # REMEDY
    # =========================================================

    remedy_base_url: str | None = None

    remedy_username: str | None = None

    remedy_password: str | None = None

    # =========================================================
    # CONFIGURATION
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()