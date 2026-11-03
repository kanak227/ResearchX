from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ...database.models import BenchmarkResultRecord
from ...database.repository import db_repo
from ...evaluation.benchmark import benchmark_runner

router = APIRouter(prefix="/eval", tags=["evaluation"])

class BenchmarkRunRequest(BaseModel):
    experiment_id: str  # exp_a_text_only, exp_b_hybrid, exp_c_multimodal, exp_d_multimodal_rerank
    top_k: int = 5

@router.post("/run", response_model=BenchmarkResultRecord)
def run_benchmark(req: BenchmarkRunRequest):
    try:
        return benchmark_runner.run_experiment(req.experiment_id, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")

@router.get("/history", response_model=List[BenchmarkResultRecord])
def get_benchmark_history():
    return db_repo.list_benchmark_runs()

@router.get("/summary")
def get_benchmark_summary():
    """
    Returns aggregated comparative metrics across all 4 experimental configurations
    for visualization in Recharts.
    """
    history = db_repo.list_benchmark_runs()
    configs = ["exp_a_text_only", "exp_b_hybrid", "exp_c_multimodal", "exp_d_multimodal_rerank"]
    labels = {
        "exp_a_text_only": "Exp A: Text-Only RAG",
        "exp_b_hybrid": "Exp B: Hybrid (Dense + BM25)",
        "exp_c_multimodal": "Exp C: Multimodal RAG",
        "exp_d_multimodal_rerank": "Exp D: Multimodal + Rerank + Verifier"
    }

    summary = []
    for cfg in configs:
        matches = [h for h in history if h.config_name == cfg]
        if matches:
            latest = matches[0]
            summary.append({
                "config_id": cfg,
                "label": labels.get(cfg, cfg),
                "precision_at_k": latest.precision_at_k,
                "recall_at_k": latest.recall_at_k,
                "mrr": latest.mrr,
                "answer_correctness": latest.answer_correctness,
                "citation_accuracy": latest.citation_accuracy,
                "faithfulness": latest.faithfulness,
                "avg_response_latency": latest.avg_response_latency,
                "avg_retrieval_latency": latest.avg_retrieval_latency,
                "samples": latest.sample_count,
                "timestamp": latest.timestamp
            })
        else:
            # Baseline placeholder metrics if not yet executed
            summary.append({
                "config_id": cfg,
                "label": labels.get(cfg, cfg),
                "precision_at_k": 0.0,
                "recall_at_k": 0.0,
                "mrr": 0.0,
                "answer_correctness": 0.0,
                "citation_accuracy": 0.0,
                "faithfulness": 0.0,
                "avg_response_latency": 0.0,
                "avg_retrieval_latency": 0.0,
                "samples": 0,
                "timestamp": None
            })

    return summary

