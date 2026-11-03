from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .core.config import settings
from .core.logging import logger
from .api.routes import (
    papers,
    ingestion,
    chat,
    comparison,
    research_gaps,
    evaluation,
    graph
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal, Evidence-Grounded Research Intelligence System",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite dev runs on localhost:5173 by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(papers.router, prefix="/api")
app.include_router(ingestion.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(research_gaps.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(graph.router, prefix="/api")

# Mount extracted files (figures, images, crops)
os.makedirs(settings.EXTRACTED_DIR, exist_ok=True)
app.mount("/extracted", StaticFiles(directory=settings.EXTRACTED_DIR), name="extracted")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": "sqlite_connected",
        "vector_store": "local_qdrant_ready",
        "ollama_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }

# Mount Frontend production build assets
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if (frontend_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

@app.get("/")
def serve_index():
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ResearchX Backend on %s:%d", settings.HOST, settings.PORT)
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
