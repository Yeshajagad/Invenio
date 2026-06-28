from sentence_transformers import SentenceTransformer
from loguru import logger
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    _model = None

    def _load_model(self):
        if self._model is None:
            logger.info(f"🔄 Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            logger.info("✅ Embedding model loaded")
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        model = self._load_model()
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        model = self._load_model()
        embedding = model.encode(
            query,
            normalize_embeddings=True,
        )
        return embedding.tolist()