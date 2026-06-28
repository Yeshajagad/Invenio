from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from loguru import logger
from app.config import get_settings

settings = get_settings()


class QdrantService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection = settings.qdrant_collection
        self.vector_size = 384  # BAAI/bge-small-en-v1.5 dimension

    async def ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            await self.client.get_collection(self.collection)
            logger.info(f"✅ Qdrant collection '{self.collection}' exists")
        except Exception:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"🆕 Created Qdrant collection '{self.collection}'")

    async def upsert_vectors(self, points: list[dict]):
        """Insert or update vectors in Qdrant."""
        qdrant_points = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        await self.client.upsert(
            collection_name=self.collection,
            points=qdrant_points,
        )
        logger.info(f"📌 Upserted {len(qdrant_points)} vectors to Qdrant")

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        doc_id: int | None = None,
    ) -> list[dict]:
        """Search for similar vectors."""
        search_filter = None
        if doc_id:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=doc_id),
                    )
                ]
            )

        results = await self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )

        return [
            {
                "chunk_id": r.payload.get("chunk_id"),
                "document_id": r.payload.get("document_id"),
                "chunk_text": r.payload.get("chunk_text"),
                "chunk_number": r.payload.get("chunk_number"),
                "original_name": r.payload.get("original_name"),
                "score": r.score,
            }
            for r in results
        ]

    async def delete_by_document(self, doc_id: int):
        """Remove all vectors for a document."""
        from qdrant_client.models import FilterSelector
        await self.client.delete(
            collection_name=self.collection,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                )
            ),
        )
        logger.info(f"🗑️  Deleted Qdrant vectors for doc {doc_id}")

    async def collection_info(self) -> dict:
        """Get collection stats."""
        info = await self.client.get_collection(self.collection)
        return {
            "name": self.collection,
            "vectors_count": info.vectors_count,
            "status": str(info.status),
        }