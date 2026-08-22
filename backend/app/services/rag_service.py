from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


SYSTEM_PROMPT = """
You are WINGS Enterprise AI, an enterprise IT operations assistant.

Rules:
1. RAG always means Retrieval-Augmented Generation.
2. Answer using the supplied knowledge context.
3. Do not invent facts that are not supported by the context.
4. If the context does not contain enough information, say:
   "I don't have enough information in the available knowledge base."
5. Give concise and professional answers.
6. Do not treat your general model knowledge as company knowledge.
"""


class RAGService:

    def __init__(self, db) -> None:
        self.retrieval_service = RetrievalService(db)
        self.llm_service = LLMService()

    async def query(
        self,
        question: str,
        top_k: int = 3,
    ) -> tuple[str, list[dict]]:

        results = await self.retrieval_service.search(
            question=question,
            limit=top_k,
        )

        if not results:
            return (
                "I don't have enough information in the "
                "available knowledge base.",
                [],
            )

        context_parts: list[str] = []

        for index, result in enumerate(results, start=1):
            context_parts.append(
                f"""
SOURCE {index}
Document: {result["document_title"]}

{result["content"]}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
{SYSTEM_PROMPT}

KNOWLEDGE CONTEXT
=================
{context}

USER QUESTION
=============
{question}

ANSWER ONLY FROM THE KNOWLEDGE CONTEXT:
"""

        answer = await self.llm_service.generate(prompt)

        return answer, results