from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional

from ...database.models import StructuredComparisonRecord
from ...database.repository import db_repo
from ...reasoning.paper_comparator import paper_comparator

router = APIRouter(prefix="/compare", tags=["comparison"])

class CompareRequest(BaseModel):
    paper_ids: List[str]
    title: Optional[str] = None

@router.post("", response_model=StructuredComparisonRecord)
def generate_comparison(req: CompareRequest):
    if len(req.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least two research papers to compare.")
    try:
        return paper_comparator.compare_papers(req.paper_ids, custom_title=req.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/list", response_model=List[StructuredComparisonRecord])
def list_comparisons():
    return db_repo.list_comparisons()

@router.get("/{comparison_id}/csv")
def export_comparison_csv(comparison_id: str):
    comparisons = db_repo.list_comparisons()
    match = next((c for c in comparisons if c.id == comparison_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    
    csv_data = paper_comparator.export_as_csv(match)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=comparison_{comparison_id}.csv"}
    )

