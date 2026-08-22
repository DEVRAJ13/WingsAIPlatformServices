import httpx

from app.core.config import settings


class LLMService:

    async def generate(
        self,
        prompt: str,
    ) -> str:

        timeout = httpx.Timeout(
            connect=5.0,
            read=float(settings.ollama_timeout_seconds),
            write=10.0,
            pool=5.0,
        )

        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.ai_temperature,
                "num_predict": settings.ai_max_output_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:

                response = await client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.ReadTimeout as exc:
            raise RuntimeError(
                "LLM generation timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"LLM service request failed: {exc}"
            ) from exc

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return answer