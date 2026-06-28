from .documents import router as documents_router
from .processing import router as processing_router
from .embeddings import router as embeddings_router

__all__ = ["documents_router", "processing_router", "embeddings_router"]