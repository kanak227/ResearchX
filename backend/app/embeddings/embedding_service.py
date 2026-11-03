import numpy as np
from typing import List, Optional
import hashlib
from ..core.config import settings
from ..core.logging import logger

class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dim = 384
        self._model = None
        self._initialized = False

    def _load_model(self):
        if self._initialized:
            return
        try:
            logger.info("Initializing embedding model: %s", self.model_name)
            from sentence_transformers import SentenceTransformer
            # Attempt to load from local cache first to avoid network timeout in offline/sandboxed environments
            try:
                self._model = SentenceTransformer(self.model_name, device="cpu", local_files_only=True)
            except Exception:
                self._model = SentenceTransformer(self.model_name, device="cpu")
            self._initialized = True
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.warning("Could not load sentence-transformers model '%s': %s. Using deterministic fallback embeddings.", self.model_name, e)
            self._model = None
            self._initialized = True

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        self._load_model()
        if self._model is not None:
            try:
                embeddings = self._model.encode(
                    texts,
                    batch_size=16,
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                return embeddings.tolist()
            except Exception as e:
                logger.error("Embedding generation failed, falling back to deterministic projection: %s", e)

        # High-dimensional deterministic projection fallback
        return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic, consistent projection for testing and low-memory CPU environments.
        """
        words = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)
        if not words:
            return vec.tolist()
        
        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

embedding_service = EmbeddingService()
