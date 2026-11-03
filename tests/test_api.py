import pytest
from backend.app.main import health_check
from backend.app.api.routes.papers import list_papers, get_paper, get_paper_elements
from backend.app.api.routes.chat import ask_research_assistant, ChatRequest
from backend.app.api.routes.evaluation import get_benchmark_summary
from backend.app.api.routes.graph import get_knowledge_graph
from backend.app.api.routes.comparison import generate_comparison, CompareRequest
from backend.app.api.routes.research_gaps import analyze_research_gaps, GapAnalysisRequest
from backend.app.database.repository import db_repo
from backend.app.api.routes.ingestion import _ingest_and_index

@pytest.fixture(scope="module", autouse=True)
def setup_test_papers():
    # Ingest test papers if not present
    p1 = db_repo.get_paper("paper_attn")
    if not p1:
        _ingest_and_index("paper_attn", "datasets/sample_papers/Paper1_Transformer_Attention_Mechanisms.pdf")
    p2 = db_repo.get_paper("paper_rag")
    if not p2:
        _ingest_and_index("paper_rag", "datasets/sample_papers/Paper2_Multimodal_Retrieval_Augmented_Generation.pdf")

def test_health_check():
    res = health_check()
    assert res["status"] == "healthy"
    assert "environment" in res
    assert "database" in res
    assert "vector_store" in res

def test_list_papers():
    papers = list_papers()
    assert isinstance(papers, list)
    assert len(papers) >= 2
    paper_ids = [p.id for p in papers]
    assert "paper_attn" in paper_ids

def test_paper_elements():
    elements = get_paper_elements("paper_attn")
    assert isinstance(elements, list)
    assert len(elements) > 0
    # Verify presence of multimodal elements
    types = set(e.element_type for e in elements)
    assert "text" in types

def test_chat_multimodal_retrieval():
    req = ChatRequest(
        query="What is the computational complexity of self-attention?",
        paper_id="paper_attn",
        retrieval_mode="multimodal",
        top_k=3,
        enable_verification=True
    )
    res = ask_research_assistant(req)
    assert res.answer is not None
    assert len(res.answer) > 0
    assert isinstance(res.claims, list)
    assert isinstance(res.citations, list)

def test_benchmark_summary():
    summary = get_benchmark_summary()
    assert isinstance(summary, list)
    assert len(summary) == 4
    config_ids = [s["config_id"] for s in summary]
    assert "exp_a_text_only" in config_ids
    assert "exp_d_multimodal_rerank" in config_ids

def test_knowledge_graph():
    graph = get_knowledge_graph()
    assert "nodes" in graph
    assert "links" in graph
    assert len(graph["nodes"]) > 0
    assert len(graph["links"]) > 0

def test_cross_paper_comparison():
    req = CompareRequest(paper_ids=["paper_attn", "paper_rag"], title="Attention vs Multimodal RAG")
    comp = generate_comparison(req)
    assert comp.id is not None
    assert len(comp.paper_ids) == 2
    assert len(comp.matrix) >= 5

def test_research_gap_analysis():
    req = GapAnalysisRequest(paper_ids=["paper_attn", "paper_rag"])
    gap = analyze_research_gaps(req)
    assert gap.id is not None
    assert "Selected Corpus" in gap.scope_notice
    assert len(gap.frequently_reported_limitations) > 0
    assert len(gap.potential_research_questions) > 0
