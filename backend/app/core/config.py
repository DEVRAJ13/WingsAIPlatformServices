from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "WINGS AI Platform"
    app_env: str = "development"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    rbac_bootstrap_admin_email: str | None = None

    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:1.5b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout_seconds: int = 120
    ollama_keep_alive: str = "5m"
    ollama_num_parallel: int = 1
    ollama_max_loaded_models: int = 1

    ai_max_prompt_length: int = 4000
    ai_max_output_tokens: int = 128
    ai_temperature: float = 0.1
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1024
    allowed_ai_model: str = "qwen2.5:1.5b"
    max_agent_steps: int = 5

    rag_top_k: int = 3
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 100
    rag_min_similarity: float = 0.5

    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str | None = None

    servicenow_base_url: str | None = None
    servicenow_username: str | None = None
    servicenow_password: str | None = None

    remedy_base_url: str | None = None
    remedy_username: str | None = None
    remedy_password: str | None = None

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
