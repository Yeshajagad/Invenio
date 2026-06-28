import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.document import Document, DocumentChunk, EmbeddingMetadata, ProcessingStatus
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.config import get_settings

settings = get_settings()
embedder = EmbeddingService()
qdrant = QdrantService()


class EmbeddingPipeline:

    async def embed_document(self, doc_id: int, db: AsyncSession) -> dict:
        """Generate embeddings for all chunks of a document."""

        # Ensure Qdrant collection exists
        await qdrant.ensure_collection()

        # Fetch document
        doc_result = await db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = doc_result.scalar_one_or_none()
        if not doc:
            return {"error": f"Document {doc_id} not found"}

        if doc.processing_status != ProcessingStatus.COMPLETED:
            return {"error": "Document must be processed before embedding"}

        # Fetch chunks
        chunks_result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == doc_id)
            .order_by(DocumentChunk.chunk_number)
        )
        chunks = chunks_result.scalars().all()

        if not chunks:
            return {"error": "No chunks found. Run processing first."}

        logger.info(f"🧠 Embedding {len(chunks)} chunks for doc {doc_id}")

        # Generate embeddings in batches
        batch_size = 32
        all_points = []

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.chunk_text for c in batch]
            vectors = embedder.embed_texts(texts)

            for chunk, vector in zip(batch, vectors):
                vector_id = str(uuid.uuid4().int % (2**63))

                all_points.append({
                    "id": int(vector_id),
                    "vector": vector,
                    "payload": {
                        "chunk_id": chunk.id,
                        "document_id": doc_id,
                        "chunk_number": chunk.chunk_number,
                        "chunk_text": chunk.chunk_text,
                        "original_name": doc.original_name,
                        "file_type": doc.file_type,
                    },
                })

                # Save metadata to PostgreSQL
                meta = EmbeddingMetadata(
                    chunk_id=chunk.id,
                    document_id=doc_id,
                    vector_id=vector_id,
                    embedding_model=settings.embedding_model,
                )
                db.add(meta)

        # Upsert to Qdrant
        await qdrant.upsert_vectors(all_points)
        await db.commit()

        logger.info(f"✅ Embedded {len(all_points)} chunks for doc {doc_id}")
        return {
            "doc_id": doc_id,
            "chunks_embedded": len(all_points),
            "model": settings.embedding_model,
            "status": "embedded",
        }

    async def delete_document_embeddings(self, doc_id: int, db: AsyncSession):
        """Remove embeddings from Qdrant for a document."""
        await qdrant.delete_by_document(doc_id)
        logger.info(f"🗑️  Removed embeddings for doc {doc_id}")