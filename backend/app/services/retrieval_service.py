from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self, db: AsyncSession) -> None:
        self.repository = KnowledgeRepository(db)
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        question: str,
        limit: int = 5,
    ) -> list[dict]:

        embedding = await self.embedding_service.embed(
            question
        )

        results = await self.repository.search_similar_chunks(
            embedding=embedding,
            limit=limit,
        )

        return [
            {
                "document_id": chunk.document_id,
                "document_title": title,
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": float(distance),
            }
            for chunk, distance, title in results
        ]