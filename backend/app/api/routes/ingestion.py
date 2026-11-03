from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import uuid
from datetime import datetime
import shutil

from ...core.config import settings
from ...core.logging import logger
from ...database.models import PaperRecord
from ...database.repository import db_repo
from ...ingestion.pdf_parser import pdf_parser
from ...embeddings.embedding_service import embedding_service
from ...retrieval.vector_store import vector_store
from ...retrieval.bm25_retriever import bm25_retriever

router = APIRouter(prefix="/ingest", tags=["ingestion"])

def _ingest_and_index(paper_id: str, filepath: str):
    """Background or inline worker that processes PDF and updates vector/BM25 indices."""
    try:
        summary = pdf_parser.process_paper(paper_id, filepath)
        # Fetch elements to build vector and BM25 indices
        elements = db_repo.get_elements_by_paper(paper_id)
        if elements:
            elem_dicts = [e.dict() for e in elements]
            # Batch embedding
            contents = [e.content for e in elements]
            embeddings = embedding_service.embed_documents(contents)
            vector_store.upsert_elements(elem_dicts, embeddings)
            
            # Update BM25 index with all elements in database
            all_db_elements = []
            for p in db_repo.list_papers():
                all_db_elements.extend([e.dict() for e in db_repo.get_elements_by_paper(p.id)])
            bm25_retriever.index_elements(all_db_elements)

        logger.info("Successfully indexed paper %s in vector and BM25 store", paper_id)
    except Exception as e:
        logger.error("Error during background indexing of paper %s: %s", paper_id, e)

@router.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    paper_id = str(uuid.uuid4())[:8]
    clean_filename = os.path.basename(file.filename).replace(" ", "_")
    save_path = os.path.join(settings.UPLOADS_DIR, f"{paper_id}_{clean_filename}")

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    now_str = datetime.utcnow().isoformat()
    paper = PaperRecord(
        id=paper_id,
        filename=file.filename,
        filepath=save_path,
        title=os.path.splitext(file.filename)[0].replace("_", " "),
        authors=[],
        abstract="",
        page_count=0,
        created_at=now_str,
        updated_at=now_str,
        processing_status="processing"
    )
    db_repo.create_paper(paper)

    # Process paper
    try:
        summary = pdf_parser.process_paper(paper_id, save_path)
        # Index in vector store and BM25
        elements = db_repo.get_elements_by_paper(paper_id)
        if elements:
            elem_dicts = [e.dict() for e in elements]
            contents = [e.content for e in elements]
            embeddings = embedding_service.embed_documents(contents)
            vector_store.upsert_elements(elem_dicts, embeddings)

            all_db_elements = []
            for p in db_repo.list_papers():
                all_db_elements.extend([e.dict() for e in db_repo.get_elements_by_paper(p.id)])
            bm25_retriever.index_elements(all_db_elements)

        return {
            "message": "Paper ingested and indexed successfully",
            "paper_id": paper_id,
            "summary": summary
        }
    except Exception as e:
        logger.error("Ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/status/{paper_id}")
def check_status(paper_id: str):
    paper = db_repo.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {
        "id": paper.id,
        "title": paper.title,
        "status": paper.processing_status,
        "error": paper.error_message,
        "page_count": paper.page_count
    }

