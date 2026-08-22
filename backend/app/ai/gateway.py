import asyncio

from app.ai.client import OllamaClient
from app.ai.config import (
    AI_MAX_OUTPUT_TOKENS,
    AI_MAX_PROMPT_LENGTH,
    AI_TEMPERATURE,
    ALLOWED_AI_MODEL,
)
from app.ai.prompts.chat import SYSTEM_PROMPT


class AIGateway:
    def __init__(self) -> None:
        self.client = OllamaClient()

        # One LLM generation at a time.
        # Protects the 2-OCPU Always-Free VM.
        self._semaphore = asyncio.Semaphore(1)

    async def generate(
        self,
        message: str,
    ) -> str:
        normalized_message = message.strip()

        if not normalized_message:
            raise ValueError(
                "AI message cannot be empty."
            )

        if len(normalized_message) > AI_MAX_PROMPT_LENGTH:
            raise ValueError(
                "AI message exceeds the maximum allowed length."
            )

        async with self._semaphore:
            return await self.client.chat(
                model=ALLOWED_AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": normalized_message,
                    },
                ],
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_OUTPUT_TOKENS,
            )