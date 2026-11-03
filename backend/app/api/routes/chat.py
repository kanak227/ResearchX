from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import time

from ...database.models import ChatResponse, VerifiedClaim, CitationItem
from ...database.repository import db_repo
from ...retrieval.hybrid_retriever import hybrid_retriever
from ...llm.ollama_client import ollama_client
from ...llm.prompt_templates import PromptTemplates
from ...reasoning.evidence_verifier import evidence_verifier
from ...core.logging import logger

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    paper_id: Optional[str] = None
    retrieval_mode: str = "multimodal"  # text_only, hybrid, multimodal
    top_k: int = 5
    enable_verification: bool = True

@router.post("", response_model=ChatResponse)
def ask_research_assistant(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    t0 = time.time()
    logger.info("Chat request received: '%s' (Mode: %s, Paper: %s)", req.query, req.retrieval_mode, req.paper_id)

    # 1. Retrieve evidence
    retrieved = hybrid_retriever.retrieve(
        query=req.query,
        mode=req.retrieval_mode,
        top_k=req.top_k,
        paper_id=req.paper_id,
        apply_reranker=True
    )

    # Attach paper metadata into retrieved payload if missing
    for r in retrieved:
        pid = r["payload"].get("paper_id")
        if pid and "paper_title" not in r["payload"]:
            paper = db_repo.get_paper(pid)
            if paper:
                r["payload"]["paper_title"] = paper.title

    # 2. Build context string with explicit provenance anchors
    context_blocks = []
    for r in retrieved:
        payload = r["payload"]
        p_title = payload.get("paper_title", "Research Paper")
        p_num = payload.get("page_number", 1)
        sec_name = payload.get("section_name", "General")
        elem_type = payload.get("element_type", "text").upper()
        content = payload.get("content", "")

        block = f"[SOURCE: {p_title} | Page {p_num} | Section: {sec_name} | Type: {elem_type}]\n{content}"
        context_blocks.append(block)

    context_str = "\n\n---\n\n".join(context_blocks)
    if not context_str:
        context_str = "No directly relevant documents found in the selected corpus."

    # 3. Generate answer via local LLM
    prompt = PromptTemplates.RAG_QA_USER_TEMPLATE.format(context=context_str, query=req.query)
    answer = ollama_client.generate(
        prompt=prompt,
        system_prompt=PromptTemplates.SYSTEM_RESEARCH_ASSISTANT,
        temperature=0.2
    )

    # 4. Evidence & Citation Verification
    verified_claims = []
    citations = []
    if req.enable_verification:
        verified_claims, citations, faithfulness = evidence_verifier.verify_response(answer, retrieved)
    else:
        # Construct direct citations from top retrieved evidence
        for r in retrieved:
            payload = r["payload"]
            citations.append(CitationItem(
                paper_id=payload.get("paper_id", "unknown"),
                paper_title=payload.get("paper_title", "Paper"),
                page_number=payload.get("page_number", 1),
                section_name=payload.get("section_name", "General"),
                snippet=payload.get("content", "")[:250],
                element_type=payload.get("element_type", "text"),
                confidence_score=r.get("score", 0.8)
            ))

    latency = round(time.time() - t0, 3)

    return ChatResponse(
        query=req.query,
        answer=answer,
        retrieval_mode=req.retrieval_mode,
        claims=verified_claims,
        citations=citations,
        latency_seconds=latency,
        model_used=ollama_client.model
    )

