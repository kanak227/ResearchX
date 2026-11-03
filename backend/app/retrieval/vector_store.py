import os
import numpy as np
from typing import List, Dict, Any, Optional
from ..core.config import settings
from ..core.logging import logger

COLLECTION_NAME = "researchx_elements"

class LocalVectorStore:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or settings.QDRANT_STORAGE_PATH
        if self.storage_path != ":memory:":
            os.makedirs(self.storage_path, exist_ok=True)
        self.dim = 384
        self.client = None
        self._init_qdrant()

        # In-memory index fallback for instant testing and zero-overhead CPU execution
        self._fallback_vectors: Dict[str, np.ndarray] = {}
        self._fallback_payloads: Dict[str, Dict[str, Any]] = {}

    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            if self.storage_path == ":memory:":
                self.client = QdrantClient(":memory:")
            else:
                self.client = QdrantClient(path=self.storage_path)
            collections = self.client.get_collections().collections
            exists = any(c.name == COLLECTION_NAME for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
                )
                logger.info("Qdrant collection '%s' created at %s", COLLECTION_NAME, self.storage_path)
            else:
                logger.info("Qdrant collection '%s' loaded from %s", COLLECTION_NAME, self.storage_path)
        except Exception as e:
            logger.warning("Could not initialize native QdrantClient: %s. Using in-memory fallback vector store.", e)
            self.client = None

    def upsert_elements(self, elements: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        elements: list of dicts with keys: id, paper_id, element_type, page_number, section_name, content, coords
        embeddings: list of 384d float lists
        """
        if not elements or not embeddings:
            return

        if self.client is not None:
            try:
                from qdrant_client.models import PointStruct
                points = []
                for i, (elem, emb) in enumerate(zip(elements, embeddings)):
                    points.append(PointStruct(
                        id=hash(elem["id"]) & 0x7FFFFFFF,  # positive 32-bit int ID
                        vector=emb,
                        payload=elem
                    ))
                self.client.upsert(collection_name=COLLECTION_NAME, points=points)
                logger.info("Upserted %d points into Qdrant", len(points))
                return
            except Exception as e:
                logger.error("Failed to upsert to Qdrant: %s. Storing in fallback index.", e)

        # Fallback index
        for elem, emb in zip(elements, embeddings):
            self._fallback_vectors[elem["id"]] = np.array(emb, dtype=np.float32)
            self._fallback_payloads[elem["id"]] = elem

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        paper_id: Optional[str] = None,
        element_types: Optional[List[str]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Searches for most similar elements.
        Returns list of dicts with: id, score, payload
        """
        if self.client is not None:
            try:
                from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
                must_conditions = []
                if paper_id:
                    must_conditions.append(FieldCondition(key="paper_id", match=MatchValue(value=paper_id)))
                if element_types:
                    must_conditions.append(FieldCondition(key="element_type", match=MatchAny(any=element_types)))

                query_filter = Filter(must=must_conditions) if must_conditions else None

                if hasattr(self.client, "query_points"):
                    res = self.client.query_points(
                        collection_name=COLLECTION_NAME,
                        query=query_vector,
                        query_filter=query_filter,
                        limit=top_k,
                        score_threshold=score_threshold
                    )
                    results = res.points
                else:
                    results = self.client.search(
                        collection_name=COLLECTION_NAME,
                        query_vector=query_vector,
                        query_filter=query_filter,
                        limit=top_k,
                        score_threshold=score_threshold
                    )
                return [
                    {
                        "id": r.payload.get("id"),
                        "score": round(float(r.score), 4),
                        "payload": r.payload
                    }
                    for r in results
                ]
            except Exception as e:
                logger.error("Qdrant search failed: %s. Using fallback search.", e)

        # Fallback search
        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        scored = []
        for elem_id, vec in self._fallback_vectors.items():
            payload = self._fallback_payloads.get(elem_id, {})
            if paper_id and payload.get("paper_id") != paper_id:
                continue
            if element_types and payload.get("element_type") not in element_types:
                continue

            v_norm = np.linalg.norm(vec)
            sim = float(np.dot(q_vec, vec) / (v_norm + 1e-8)) if v_norm > 0 else 0.0
            if sim >= score_threshold:
                scored.append({
                    "id": elem_id,
                    "score": round(sim, 4),
                    "payload": payload
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

vector_store = LocalVectorStore()
