from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService


class VectorSearchService:
    """
    Semantic search over document chunks stored in pgvector.
    """

    DEFAULT_LIMIT = 5
    MAX_LIMIT = 20
    DEFAULT_MIN_SIMILARITY = 0.50

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    async def search(
        self,
        *,
        query: str,
        limit: int = DEFAULT_LIMIT,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
    ) -> list[dict]:
        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        limit = max(
            1,
            min(limit, self.MAX_LIMIT),
        )

        min_similarity = max(
            0.0,
            min(min_similarity, 1.0),
        )

        # -----------------------------------------------------
        # QUERY EMBEDDING
        # -----------------------------------------------------

        query_embedding = await self.embedding_service.embed(
            query
        )

        # -----------------------------------------------------
        # COSINE DISTANCE / SIMILARITY
        # -----------------------------------------------------

        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        similarity = (
            1 - distance
        ).label("similarity")

        # -----------------------------------------------------
        # VECTOR SEARCH + DOCUMENT METADATA
        # -----------------------------------------------------

        statement = (
            select(
                DocumentChunk.id.label("chunk_id"),
                DocumentChunk.document_id.label(
                    "document_id"
                ),
                DocumentChunk.chunk_index.label(
                    "chunk_index"
                ),
                DocumentChunk.content.label(
                    "content"
                ),
                Document.title.label(
                    "document_title"
                ),
                similarity,
            )
            .join(
                Document,
                Document.id
                == DocumentChunk.document_id,
            )
            .where(
                similarity >= min_similarity,
            )
            .order_by(distance)
            .limit(limit)
        )

        result = await self.db.execute(statement)

        rows = result.all()

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return [
            {
                "chunk_id": row.chunk_id,
                "document_id": row.document_id,
                "document_title": row.document_title,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "similarity": float(
                    row.similarity
                ),
            }
            for row in rows
        ]