from fastapi import APIRouter, Query
from typing import Optional, List

from ...graph.knowledge_graph import knowledge_graph

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("")
def get_knowledge_graph(paper_ids: Optional[str] = Query(default=None, description="Comma-separated paper IDs")):
    pids = paper_ids if isinstance(paper_ids, str) else None
    pid_list = [p.strip() for p in pids.split(",") if p.strip()] if pids else None
    return knowledge_graph.build_graph_for_papers(pid_list)
