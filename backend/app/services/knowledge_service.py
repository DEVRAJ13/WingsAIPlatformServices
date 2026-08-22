from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from app.services.embedding_service import EmbeddingService
from app.services.text_chunker import chunk_text


class KnowledgeService:

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.repository = KnowledgeRepository(db)
        self.embedding_service = EmbeddingService()
        self.db = db

    async def ingest_document(
        self,
        title: str,
        content: str,
    ) -> tuple[int, int]:

        chunks = chunk_text(content)

        if not chunks:
            raise ValueError(
                "Document does not contain usable text."
            )

        document = await self.repository.create_document(
            title=title,
            content=content,
        )

        for index, chunk_content in enumerate(chunks):
            embedding = await self.embedding_service.embed(
                chunk_content
            )

            if len(embedding) != 768:
                raise RuntimeError(
                    "Unexpected embedding dimension: "
                    f"{len(embedding)}. Expected 768."
                )

            await self.repository.create_chunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_content,
                embedding=embedding,
            )

        await self.db.commit()

        return document.id, len(chunks)