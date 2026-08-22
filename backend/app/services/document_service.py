from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.text_chunker import chunk_text


class DocumentService:
    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db
        self.embedding_service = EmbeddingService()

    async def create_document(
        self,
        *,
        title: str,
        content: str,
    ) -> dict:
        title = title.strip()
        content = content.strip()

        if not title:
            raise ValueError(
                "Document title cannot be empty."
            )

        if not content:
            raise ValueError(
                "Document content cannot be empty."
            )

        chunks = chunk_text(
            content,
            chunk_size=800,
            overlap=100,
        )

        if not chunks:
            raise ValueError(
                "Document does not contain usable text."
            )

        document = Document(
            title=title,
            content=content,
        )

        self.db.add(document)

        await self.db.flush()

        try:
            for index, chunk in enumerate(chunks):
                embedding = await (
                    self.embedding_service.embed(chunk)
                )

                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                )

                self.db.add(document_chunk)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return {
            "id": document.id,
            "title": document.title,
            "chunk_count": len(chunks),
            "message": (
                "Document ingested successfully."
            ),
        }
