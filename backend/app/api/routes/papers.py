from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from ...database.models import PaperRecord, ExtractedElementRecord
from ...database.repository import db_repo
from ...core.logging import logger

router = APIRouter(prefix="/papers", tags=["papers"])

@router.get("", response_model=List[PaperRecord])
def list_papers():
    return db_repo.list_papers()

@router.get("/{paper_id}", response_model=PaperRecord)
def get_paper(paper_id: str):
    paper = db_repo.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@router.get("/{paper_id}/elements", response_model=List[ExtractedElementRecord])
def get_paper_elements(
    paper_id: str,
    element_type: Optional[str] = Query(default=None, description="text, table, figure, equation")
):
    paper = db_repo.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    elem_type = element_type if isinstance(element_type, str) else None
    return db_repo.get_elements_by_paper(paper_id, element_type=elem_type)

@router.get("/{paper_id}/pdf")
def get_paper_pdf(paper_id: str):
    paper = db_repo.get_paper(paper_id)
    if not paper or not os.path.exists(paper.filepath):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(paper.filepath, media_type="application/pdf", filename=paper.filename)

@router.delete("/{paper_id}")
def delete_paper(paper_id: str):
    paper = db_repo.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    db_repo.delete_paper(paper_id)
    return {"message": "Paper and extracted elements successfully deleted", "id": paper_id}
