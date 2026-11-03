import pytest
from backend.app.reasoning.paper_comparator import paper_comparator
from backend.app.reasoning.research_gap_analyzer import research_gap_analyzer
from backend.app.reasoning.evidence_verifier import evidence_verifier
from backend.app.ingestion.pdf_parser import pdf_parser

def test_evidence_verification():
    mock_evidence = [
        {
            "id": "e1",
            "score": 0.85,
            "payload": {
                "paper_id": "test_p1",
                "paper_title": "Transformer Attention",
                "page_number": 2,
                "section_name": "Results",
                "content": "The big transformer model achieves a state-of-the-art score of 41.8 BLEU on English-to-French.",
                "element_type": "text"
            }
        }
    ]

    answer = "The big transformer model achieves a state-of-the-art score of 41.8 BLEU on English-to-French translation."
    claims, citations, faithfulness = evidence_verifier.verify_response(answer, mock_evidence)

    assert len(claims) > 0
    assert claims[0].status == "verified"
    assert faithfulness > 0.5
    assert len(citations) >= 1
    assert citations[0].page_number == 2

def test_paper_comparison_and_gap_analysis():
    # Ingest Paper 2
    pdf_parser.process_paper("test_p2", "datasets/sample_papers/Paper2_Multimodal_Retrieval_Augmented_Generation.pdf")

    # Cross-Paper Comparison
    comp = paper_comparator.compare_papers(["test_p1", "test_p2"])
    assert comp is not None
    assert len(comp.matrix) >= 5
    csv_str = paper_comparator.export_as_csv(comp)
    assert "Criterion" in csv_str

    # Gap Discovery
    gaps = research_gap_analyzer.analyze_gaps(["test_p1", "test_p2"])
    assert gaps is not None
    assert "Potential Research Gaps Identified Within the Selected Corpus." in gaps.scope_notice
    assert len(gaps.potential_research_questions) > 0

