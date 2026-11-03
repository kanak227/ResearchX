import pytest
import os
from backend.app.ingestion.pdf_parser import pdf_parser
from backend.app.database.repository import db_repo

def test_validate_and_parse_pdf():
    pdf_path = "datasets/sample_papers/Paper1_Transformer_Attention_Mechanisms.pdf"
    assert os.path.exists(pdf_path), "Sample PDF should exist"
    assert pdf_parser.validate_pdf(pdf_path) is True

    paper_id = "test_p1"
    summary = pdf_parser.process_paper(paper_id, pdf_path)
    
    assert summary["status"] == "completed"
    assert summary["page_count"] == 2
    assert summary["total_elements"] > 0
    assert summary["total_figures"] >= 1
    assert summary["total_equations"] >= 1

    # Check database persistence
    paper = db_repo.get_paper(paper_id)
    assert paper is not None
    assert "Attention" in paper.title

    elements = db_repo.get_elements_by_paper(paper_id)
    assert len(elements) == summary["total_elements"]

    # Verify element attributes
    for e in elements:
        assert e.paper_id == paper_id
        assert e.page_number in [1, 2]
        assert e.element_type in ["text", "table", "figure", "equation"]
        assert len(e.content) > 0

