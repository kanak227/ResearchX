import re
from typing import List, Dict, Any, Optional
from ..core.logging import logger

class BM25Retriever:
    def __init__(self):
        self.corpus_elements: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25_model = None

    def tokenize(self, text: str) -> List[str]:
        # Lowercase, alphanumeric words, 2+ chars
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        return tokens

    def index_elements(self, elements: List[Dict[str, Any]]):
        """
        Builds or updates the BM25 index over a list of element dicts.
        """
        if not elements:
            return

        self.corpus_elements = elements
        self.tokenized_corpus = [self.tokenize(e.get("content", "")) for e in elements]

        try:
            from rank_bm25 import BM25Okapi
            self.bm25_model = BM25Okapi(self.tokenized_corpus)
            logger.info("BM25 index built successfully with %d elements.", len(elements))
        except Exception as e:
            logger.warning("Could not initialize BM25Okapi: %s. Using heuristic keyword matching.", e)
            self.bm25_model = None

    def search(
        self,
        query: str,
        top_k: int = 5,
        paper_id: Optional[str] = None,
        element_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if not self.corpus_elements:
            return []

        q_tokens = self.tokenize(query)
        if not q_tokens:
            return []

        scored = []

        if self.bm25_model is not None:
            raw_scores = self.bm25_model.get_scores(q_tokens)
            max_s = max(raw_scores) if len(raw_scores) > 0 and max(raw_scores) > 0 else 1.0

            for i, score in enumerate(raw_scores):
                elem = self.corpus_elements[i]
                if paper_id and elem.get("paper_id") != paper_id:
                    continue
                if element_types and elem.get("element_type") not in element_types:
                    continue
                if score > 0:
                    normalized_score = min(score / max_s, 1.0)
                    scored.append({
                        "id": elem.get("id"),
                        "score": round(float(normalized_score), 4),
                        "payload": elem
                    })
        else:
            # Heuristic term overlap fallback
            q_set = set(q_tokens)
            for i, elem in enumerate(self.corpus_elements):
                if paper_id and elem.get("paper_id") != paper_id:
                    continue
                if element_types and elem.get("element_type") not in element_types:
                    continue

                c_tokens = self.tokenized_corpus[i] if i < len(self.tokenized_corpus) else self.tokenize(elem.get("content", ""))
                overlap = sum(1 for t in c_tokens if t in q_set)
                if overlap > 0:
                    score = overlap / max(len(q_set), 1)
                    scored.append({
                        "id": elem.get("id"),
                        "score": round(float(min(score, 1.0)), 4),
                        "payload": elem
                    })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

bm25_retriever = BM25Retriever()

