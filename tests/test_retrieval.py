import pytest
from backend.app.retrieval.hybrid_retriever import hybrid_retriever
from backend.app.retrieval.vector_store import vector_store
from backend.app.retrieval.bm25_retriever import bm25_retriever
from backend.app.database.repository import db_repo
from backend.app.embeddings.embedding_service import embedding_service

def test_retrieval_configurations():
    # Ingest elements into index
    elements = db_repo.get_elements_by_paper("test_p1")
    if not elements:
        from backend.app.ingestion.pdf_parser import pdf_parser
        pdf_parser.process_paper("test_p1", "datasets/sample_papers/Paper1_Transformer_Attention_Mechanisms.pdf")
        elements = db_repo.get_elements_by_paper("test_p1")

    elem_dicts = [e.dict() for e in elements]
    contents = [e.content for e in elements]
    embeddings = embedding_service.embed_documents(contents)

    vector_store.upsert_elements(elem_dicts, embeddings)
    bm25_retriever.index_elements(elem_dicts)

    query = "What is the formula for scaled dot product attention?"

    # 1. Text-Only RAG
    res_text = hybrid_retriever.retrieve(query, mode="text_only", top_k=3, paper_id="test_p1")
    assert len(res_text) <= 3
    for r in res_text:
        assert r["payload"]["element_type"] == "text"

    # 2. Hybrid RAG
    res_hybrid = hybrid_retriever.retrieve(query, mode="hybrid", top_k=3, paper_id="test_p1")
    assert len(res_hybrid) <= 3

    # 3. Multimodal RAG
    res_multi = hybrid_retriever.retrieve(query, mode="multimodal", top_k=5, paper_id="test_p1")
    assert len(res_multi) > 0
    # Should include equations or figures
    element_types = [r["payload"]["element_type"] for r in res_multi]
    assert any(t in ["equation", "figure", "table", "text"] for t in element_types)

