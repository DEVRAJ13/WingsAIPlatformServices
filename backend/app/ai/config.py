import os


# =========================================================
# OLLAMA
# =========================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://ollama:11434",
).rstrip("/")


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:1.5b",
)


OLLAMA_TIMEOUT_SECONDS = float(
    os.getenv(
        "OLLAMA_TIMEOUT_SECONDS",
        "120",
    )
)


# =========================================================
# AI GENERATION
# =========================================================

AI_MAX_PROMPT_LENGTH = int(
    os.getenv(
        "AI_MAX_PROMPT_LENGTH",
        "4000",
    )
)


AI_MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "AI_MAX_OUTPUT_TOKENS",
        "128",
    )
)


AI_TEMPERATURE = float(
    os.getenv(
        "AI_TEMPERATURE",
        "0.1",
    )
)


# =========================================================
# MODEL SECURITY
# =========================================================

# The client cannot select an arbitrary model.
# WINGS is locked to the approved local model.

ALLOWED_AI_MODEL = "qwen2.5:1.5b"


# =========================================================
# ITSM / JIRA
# =========================================================

JIRA_BASE_URL = os.getenv(
    "JIRA_BASE_URL",
    "",
).rstrip("/")


JIRA_EMAIL = os.getenv(
    "JIRA_EMAIL",
    "",
)


JIRA_API_TOKEN = os.getenv(
    "JIRA_API_TOKEN",
    "")


JIRA_PROJECT_KEY = os.getenv(
    "JIRA_PROJECT_KEY",
    "",
)