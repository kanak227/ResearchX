from typing import List, Dict, Any, Optional
from ..core.config import settings
from ..core.logging import logger
from ..embeddings.embedding_service import embedding_service
from .vector_store import vector_store
from .bm25_retriever import bm25_retriever
from .reranker import reranker

class HybridRetriever:
    def __init__(self):
        self.bm25_weight = settings.BM25_WEIGHT
        self.dense_weight = settings.DENSE_WEIGHT

    def retrieve(
        self,
        query: str,
        mode: str = "multimodal",  # "text_only", "hybrid", "multimodal"
        top_k: int = 5,
        paper_id: Optional[str] = None,
        apply_reranker: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Executes retrieval according to the selected configuration:
        - text_only: Dense vector retrieval strictly over text elements
        - hybrid: Dense + BM25 combined over text elements
        - multimodal: Dense + BM25 across text, tables, figures, equations + reranking
        """
        logger.info("Executing retrieval query: '%s' [Mode: %s, Paper: %s]", query, mode, paper_id)

        # 1. Determine allowed element types
        if mode == "text_only":
            element_types = ["text"]
        elif mode == "hybrid":
            element_types = ["text"]
        else:  # multimodal
            element_types = ["text", "table", "figure", "equation"]

        # 2. Dense retrieval
        query_vec = embedding_service.embed_query(query)
        dense_results = vector_store.search(
            query_vector=query_vec,
            top_k=top_k * 2,
            paper_id=paper_id,
            element_types=element_types
        )

        if mode == "text_only":
            # Direct dense results
            return dense_results[:top_k]

        # 3. BM25 Sparse retrieval
        bm25_results = bm25_retriever.search(
            query=query,
            top_k=top_k * 2,
            paper_id=paper_id,
            element_types=element_types
        )

        # 4. Fusion (RRF + Score Combination)
        combined_dict: Dict[str, Dict[str, Any]] = {}

        # Add dense results
        for rank, r in enumerate(dense_results):
            eid = r["id"]
            rrf_dense = 1.0 / (60.0 + rank + 1.0)
            combined_dict[eid] = {
                "id": eid,
                "dense_score": r["score"],
                "bm25_score": 0.0,
                "rrf_score": rrf_dense * self.dense_weight,
                "payload": r["payload"]
            }

        # Add BM25 results
        for rank, r in enumerate(bm25_results):
            eid = r["id"]
            rrf_bm25 = 1.0 / (60.0 + rank + 1.0)
            if eid in combined_dict:
                combined_dict[eid]["bm25_score"] = r["score"]
                combined_dict[eid]["rrf_score"] += rrf_bm25 * self.bm25_weight
            else:
                combined_dict[eid] = {
                    "id": eid,
                    "dense_score": 0.0,
                    "bm25_score": r["score"],
                    "rrf_score": rrf_bm25 * self.bm25_weight,
                    "payload": r["payload"]
                }

        # Compute composite score
        fused_candidates = []
        for eid, item in combined_dict.items():
            composite_score = (
                item["dense_score"] * self.dense_weight +
                item["bm25_score"] * self.bm25_weight
            )
            item["score"] = round(float(composite_score), 4)
            fused_candidates.append(item)

        # Sort by composite / RRF score
        fused_candidates.sort(key=lambda x: x["rrf_score"], reverse=True)

        # 5. Apply Cross-Encoder Reranking if enabled
        if apply_reranker and len(fused_candidates) > 1:
            reranked = reranker.rerank(
                query=query,
                candidates=fused_candidates[:top_k * 2],
                top_k=top_k
            )
            return reranked

        return fused_candidates[:top_k]

hybrid_retriever = HybridRetriever()

