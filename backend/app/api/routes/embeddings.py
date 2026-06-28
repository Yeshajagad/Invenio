from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.embedding_pipeline import EmbeddingPipeline
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/api/embeddings", tags=["Embeddings"])
pipeline = EmbeddingPipeline()
qdrant = QdrantService()


@router.post("/{doc_id}")
async def embed_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Generate and store embeddings for a document."""
    return await pipeline.embed_document(doc_id, db)


@router.get("/collection/info")
async def collection_info():
    """Get Qdrant collection stats."""
    return await qdrant.collection_info()


@router.delete("/{doc_id}")
async def delete_embeddings(doc_id: int, db: AsyncSession = Depends(get_db)):
    """Delete all embeddings for a document."""
    await pipeline.delete_document_embeddings(doc_id, db)
    return {"message": f"Embeddings deleted for document {doc_id}"}