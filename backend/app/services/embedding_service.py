import httpx

from app.core.config import settings


class EmbeddingService:
    """Generate local embeddings through Ollama."""

    def __init__(self) -> None:
        self.base_url = (
            settings.ollama_base_url.rstrip("/")
        )

        self.model = (
            settings.ollama_embedding_model
        )

        self.timeout = 120.0

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        url = (
            f"{self.base_url}"
            "/api/embeddings"
        )

        payload = {
            "model": self.model,
            "prompt": text,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    url,
                    json=payload,
                )

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama embedding generation timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Unable to connect to Ollama embedding service."
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                "Ollama embedding generation failed. "
                f"HTTP status: {response.status_code}. "
                f"Details: {response.text[:1000]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned invalid embedding JSON."
            ) from exc

        embedding = data.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError(
                "Ollama returned an invalid embedding."
            )

        if not embedding:
            raise RuntimeError(
                "Ollama returned an empty embedding."
            )

        if len(embedding) != 768:
            raise RuntimeError(
                "Invalid embedding dimension. "
                f"Expected 768, got {len(embedding)}."
            )

        return embedding