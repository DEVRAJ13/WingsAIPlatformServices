from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.services.llm_service import LLMService
from app.services.vector_search_service import VectorSearchService


async def knowledge_agent(
    state: AgentState,
    db: AsyncSession,
) -> AgentState:
    question = state.get(
        "question",
        "",
    ).strip()

    # ---------------------------------------------------------
    # VALIDATE QUESTION
    # ---------------------------------------------------------

    if not question:
        return {
            **state,
            "answer": "Please provide a question.",
            "sources": [],
        }

    # ---------------------------------------------------------
    # VECTOR SEARCH
    # ---------------------------------------------------------

    search_service = VectorSearchService(db)

    try:
        results = await search_service.search(
            query=question,
            limit=5,
        )
    except ValueError as exc:
        return {
            **state,
            "answer": str(exc),
            "sources": [],
        }
    except RuntimeError:
        return {
            **state,
            "answer": (
                "The knowledge search service is "
                "currently unavailable."
            ),
            "sources": [],
        }

    # ---------------------------------------------------------
    # NO RELEVANT KNOWLEDGE
    # ---------------------------------------------------------

    if not results:
        return {
            **state,
            "answer": (
                "I could not find relevant information "
                "in the WINGS knowledge base."
            ),
            "sources": [],
        }

    # ---------------------------------------------------------
    # BUILD GROUNDED CONTEXT
    # ---------------------------------------------------------

    context_parts: list[str] = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        context_parts.append(
            f"""
SOURCE {index}

DOCUMENT ID: {result["document_id"]}
DOCUMENT TITLE: {result["document_title"]}
CHUNK ID: {result["chunk_id"]}
CHUNK INDEX: {result["chunk_index"]}
SIMILARITY: {result["similarity"]:.4f}

CONTENT:

{result["content"]}
"""
        )

    context = "\n".join(context_parts)

    # ---------------------------------------------------------
    # GROUNDED LLM PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are the WINGS Enterprise Knowledge Agent.

Answer the user's question using ONLY the supplied
WINGS knowledge-base context.

Rules:

1. Do not invent facts.
2. Do not use outside knowledge.
3. Do not make assumptions that are not supported
   by the knowledge-base context.
4. If the context does not contain enough information,
   clearly say that the WINGS knowledge base does not
   contain enough information.
5. Keep the answer concise and professional.
6. Do not claim that an action was performed.
7. Do not execute tools.
8. Do not create incidents.
9. Do not create Jira or ITSM tickets.
10. Do not make operational changes.
11. Answer the user's actual question directly.

KNOWLEDGE BASE CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    # ---------------------------------------------------------
    # GENERATE ANSWER
    # ---------------------------------------------------------

    llm = LLMService()

    try:
        answer = await llm.generate(prompt)
    except Exception:
        return {
            **state,
            "answer": (
                "The knowledge answer could not be generated "
                "at this time."
            ),
            "sources": [],
        }

    # ---------------------------------------------------------
    # SOURCES
    # ---------------------------------------------------------

    sources = [
        {
            "type": "document",
            "document_id": result["document_id"],
            "document_title": result["document_title"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    # ---------------------------------------------------------
    # FINAL STATE
    # ---------------------------------------------------------

    return {
        **state,
        "answer": answer.strip(),
        "sources": sources,
    }