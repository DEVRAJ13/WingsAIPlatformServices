import time
import httpx

from app.core.config import settings
from app.services.workflow_service import WorkflowService


class LLMService:
    def __init__(self, db=None) -> None:
        self.db = db

    async def generate(
        self,
        prompt: str,
        *,
        workflow_id: str | None = None,
        user_id: int | None = None,
        agent_name: str | None = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("LLM prompt cannot be empty.")

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
            "keep_alive": settings.ollama_keep_alive,
            "options": {
                "temperature": settings.llm_temperature,
                "num_predict": settings.llm_max_tokens,
            },
        }

        started = time.perf_counter()
        input_tokens = output_tokens = total_tokens = 0
        status = "SUCCESS"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            answer = str(data.get("response", "")).strip()
            input_tokens = int(data.get("prompt_eval_count") or 0)
            output_tokens = int(data.get("eval_count") or 0)
            total_tokens = input_tokens + output_tokens

            if not answer:
                raise RuntimeError("LLM returned an empty response.")

            return answer

        except httpx.ReadTimeout as exc:
            status = "TIMEOUT"
            raise RuntimeError("LLM generation timed out.") from exc
        except httpx.HTTPError as exc:
            status = "ERROR"
            raise RuntimeError(f"LLM service request failed: {exc}") from exc
        finally:
            if self.db is not None:
                try:
                    await WorkflowService(self.db).record_llm_usage(
                        workflow_id=workflow_id,
                        user_id=user_id,
                        agent_name=agent_name,
                        model_name=settings.ollama_model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                        latency_ms=(time.perf_counter() - started) * 1000,
                        status=status,
                    )
                except Exception:
                    # Observability must never break the AI request.
                    pass
