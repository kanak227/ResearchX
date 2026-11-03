from typing import List, Dict, Any, Optional
from ..core.config import settings
from ..core.logging import logger

class Reranker:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.RERANKER_MODEL_NAME
        self.enabled = settings.ENABLE_RERANKER
        self._model = None
        self._initialized = False

    def _load_model(self):
        if self._initialized or not self.enabled:
            return
        try:
            from sentence_transformers import CrossEncoder
            logger.info("Initializing CrossEncoder reranker: %s", self.model_name)
            self._model = CrossEncoder(self.model_name, device="cpu")
            self._initialized = True
            logger.info("Reranker loaded successfully.")
        except Exception as e:
            logger.warning("Could not load CrossEncoder '%s': %s. Using heuristic reranking.", self.model_name, e)
            self._model = None
            self._initialized = True

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        if not self.enabled:
            return candidates[:top_k]

        self._load_model()
        if self._model is not None:
            try:
                pairs = [(query, c["payload"].get("content", "")) for c in candidates]
                scores = self._model.predict(pairs)
                for i, s in enumerate(scores):
                    candidates[i]["rerank_score"] = round(float(s), 4)
                candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
                return candidates[:top_k]
            except Exception as e:
                logger.error("Reranking failed: %s. Using original candidate order.", e)

        # Heuristic reranking: reward matching of critical terms and section relevance
        query_words = set(query.lower().split())
        for c in candidates:
            content = c["payload"].get("content", "").lower()
            section = c["payload"].get("section_name", "").lower()
            
            # Count exact word hits
            word_hits = sum(1 for w in query_words if w in content)
            section_hit = 1.0 if any(w in section for w in query_words) else 0.0
            
            # Combine original score with word overlap bonus
            original_score = c.get("score", 0.5)
            bonus = (word_hits / max(len(query_words), 1)) * 0.3 + (section_hit * 0.1)
            c["rerank_score"] = round(float(original_score + bonus), 4)

        candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        return candidates[:top_k]

reranker = Reranker()

