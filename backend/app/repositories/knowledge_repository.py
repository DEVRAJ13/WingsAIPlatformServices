from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class KnowledgeRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_document(
        self,
        title: str,
        content: str,
    ) -> Document:
        document = Document(
            title=title,
            content=content,
        )

        self.db.add(document)
        await self.db.flush()

        return document

    async def create_chunk(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        embedding: list[float],
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
        )

        self.db.add(chunk)

        return chunk

    async def search_similar_chunks(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float, str]]:
        distance = DocumentChunk.embedding.cosine_distance(
            embedding
        )

        query = (
            select(
                DocumentChunk,
                distance.label("distance"),
                Document.title,
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .order_by(distance)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return result.all()