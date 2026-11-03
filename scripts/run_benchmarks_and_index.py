import os
import sys

sys.path.insert(0, os.path.abspath("."))

import json
import time

from backend.app.core.logging import logger
from backend.app.database.repository import db_repo
from backend.app.api.routes.ingestion import _ingest_and_index
from backend.app.evaluation.benchmark import benchmark_runner

def main():
    logger.info("=== RESEARCHX BENCHMARK & INGESTION PIPELINE ===")

    sample_papers = [
        ("paper_attn", "datasets/sample_papers/Paper1_Transformer_Attention_Mechanisms.pdf"),
        ("paper_rag", "datasets/sample_papers/Paper2_Multimodal_Retrieval_Augmented_Generation.pdf"),
        ("paper_fact", "datasets/sample_papers/Paper3_Evidence_Grounded_Fact_Verification.pdf")
    ]

    # 1. Ingest all 3 papers
    for pid, fpath in sample_papers:
        if os.path.exists(fpath):
            logger.info("Ingesting and indexing %s (%s)...", pid, fpath)
            _ingest_and_index(pid, fpath)
        else:
            logger.error("Sample paper file not found: %s", fpath)

    # 2. Run all 4 benchmark experiments
    experiments = [
        "exp_a_text_only",
        "exp_b_hybrid",
        "exp_c_multimodal",
        "exp_d_multimodal_rerank"
    ]

    benchmark_results = {}
    for exp_id in experiments:
        logger.info("\n--- Running Experiment: %s ---", exp_id)
        t0 = time.time()
        record = benchmark_runner.run_experiment(exp_id, top_k=5)
        elapsed = round(time.time() - t0, 2)
        benchmark_results[exp_id] = {
            "config_name": record.config_name,
            "precision_at_k": record.precision_at_k,
            "recall_at_k": record.recall_at_k,
            "mrr": record.mrr,
            "answer_correctness": record.answer_correctness,
            "citation_accuracy": record.citation_accuracy,
            "faithfulness": record.faithfulness,
            "avg_response_latency": record.avg_response_latency,
            "avg_retrieval_latency": record.avg_retrieval_latency,
            "sample_count": record.sample_count,
            "elapsed_seconds": elapsed
        }
        logger.info(
            "Exp %s finished in %ss: P@5=%.3f, R@5=%.3f, MRR=%.3f, Correctness=%.3f, Faithfulness=%.3f",
            exp_id, elapsed, record.precision_at_k, record.recall_at_k, record.mrr,
            record.answer_correctness, record.faithfulness
        )

    # 3. Print final comparative table
    print("\n" + "=" * 95)
    print("RESEARCHX BENCHMARK EXPERIMENTAL RESULTS SUMMARY")
    print("=" * 95)
    header = f"{'Experiment':<26} | {'P@5':<6} | {'R@5':<6} | {'MRR':<6} | {'Corr':<6} | {'Faith':<6} | {'CiteAcc':<7} | {'Retr(ms)':<8}"
    print(header)
    print("-" * 95)
    for exp_id, res in benchmark_results.items():
        row = (
            f"{res['config_name']:<26} | "
            f"{res['precision_at_k']:<6.3f} | "
            f"{res['recall_at_k']:<6.3f} | "
            f"{res['mrr']:<6.3f} | "
            f"{res['answer_correctness']:<6.3f} | "
            f"{res['faithfulness']:<6.3f} | "
            f"{res['citation_accuracy']:<7.3f} | "
            f"{res['avg_retrieval_latency']*1000:<8.1f}"
        )
        print(row)
    print("=" * 95)

    # Save to disk for paper/report inclusion
    out_file = "data/benchmarks/benchmark_summary.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)
    logger.info("Benchmark summary saved to %s", out_file)

if __name__ == "__main__":
    main()
