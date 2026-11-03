import re
from typing import List, Dict, Any, Set

class EvaluationMetrics:
    @staticmethod
    def precision_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
        if not retrieved_ids or not ground_truth_ids or k <= 0:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for item in top_k if item in ground_truth_ids)
        return round(hits / k, 4)

    @staticmethod
    def recall_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
        if not retrieved_ids or not ground_truth_ids or k <= 0:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for item in top_k if item in ground_truth_ids)
        return round(hits / len(ground_truth_ids), 4)

    @staticmethod
    def mean_reciprocal_rank(retrieved_ids: List[str], ground_truth_ids: Set[str]) -> float:
        if not retrieved_ids or not ground_truth_ids:
            return 0.0
        for rank, item in enumerate(retrieved_ids, start=1):
            if item in ground_truth_ids:
                return round(1.0 / rank, 4)
        return 0.0

    @staticmethod
    def citation_accuracy(predicted_pages: List[int], expected_page: int) -> float:
        """
        Evaluates whether the cited pages encompass the ground-truth evidence page.
        """
        if not predicted_pages:
            return 0.0
        if expected_page in predicted_pages:
            return 1.0
        # Proximity score if within +/- 1 page
        if any(abs(p - expected_page) <= 1 for p in predicted_pages):
            return 0.5
        return 0.0

    @staticmethod
    def lexical_answer_correctness(generated: str, ground_truth: str) -> float:
        """
        Evaluates token F1 overlap and key metric extraction between generated and ground-truth answer.
        """
        if not generated or not ground_truth:
            return 0.0
        
        gen_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", generated.lower()))
        gt_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", ground_truth.lower()))

        if not gt_tokens or not gen_tokens:
            return 0.0

        overlap = len(gen_tokens.intersection(gt_tokens))
        precision = overlap / len(gen_tokens)
        recall = overlap / len(gt_tokens)

        if precision + recall == 0:
            return 0.0

        f1 = 2 * (precision * recall) / (precision + recall)
        return round(f1, 4)

metrics_engine = EvaluationMetrics()

