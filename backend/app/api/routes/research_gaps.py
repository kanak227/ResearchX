from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ...database.models import ResearchGapRecord
from ...database.repository import db_repo
from ...reasoning.research_gap_analyzer import research_gap_analyzer

router = APIRouter(prefix="/gaps", tags=["research_gaps"])

class GapAnalysisRequest(BaseModel):
    paper_ids: List[str]

@router.post("/analyze", response_model=ResearchGapRecord)
def analyze_research_gaps(req: GapAnalysisRequest):
    if not req.paper_ids:
        raise HTTPException(status_code=400, detail="Select at least one paper for gap discovery.")
    try:
        return research_gap_analyzer.analyze_gaps(req.paper_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")

@router.get("/list", response_model=List[ResearchGapRecord])
def list_gap_reports():
    return db_repo.list_research_gaps()

