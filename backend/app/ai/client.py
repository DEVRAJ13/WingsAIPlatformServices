import httpx

from app.ai.config import (
    OLLAMA_BASE_URL,
    OLLAMA_TIMEOUT_SECONDS,
)


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = OLLAMA_BASE_URL

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = {
            "model": model,
            "stream": False,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        timeout = httpx.Timeout(
            OLLAMA_TIMEOUT_SECONDS,
            connect=5.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        message = data.get("message") or {}
        content = message.get("content")

        if not content:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return content.strip()