from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PaperMetadata(BaseModel):
    title: Optional[str] = "Untitled Paper"
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = ""
    published_year: Optional[int] = None
    journal_venue: Optional[str] = None
    page_count: int = 0
    doi: Optional[str] = None
    total_sections: int = 0
    total_tables: int = 0
    total_figures: int = 0
    total_equations: int = 0
    extra: Dict[str, Any] = Field(default_factory=dict)

class PaperRecord(BaseModel):
    id: str
    filename: str
    filepath: str
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str = ""
    published_year: Optional[int] = None
    journal_venue: Optional[str] = None
    page_count: int = 0
    doi: Optional[str] = None
    created_at: str
    updated_at: str
    processing_status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)

class ExtractedElementRecord(BaseModel):
    id: str
    paper_id: str
    page_number: int
    section_name: str
    element_type: str  # text, table, figure, equation
    content: str
    raw_content: Optional[str] = None
    source_coordinates: Optional[Dict[str, Any]] = None  # {x0, y0, x1, y1, width, height}
    extraction_method: str = "pymupdf"
    created_at: str

class TableRecord(BaseModel):
    id: str
    paper_id: str
    page_number: int
    title: Optional[str] = None
    columns: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)
    surrounding_text: Optional[str] = None
    markdown_representation: Optional[str] = None

class FigureRecord(BaseModel):
    id: str
    paper_id: str
    page_number: int
    figure_number: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    image_path: str
    surrounding_text: Optional[str] = None
    detected_type: Optional[str] = None  # architecture, graph, chart, photo, diagram

class EquationRecord(BaseModel):
    id: str
    paper_id: str
    page_number: int
    equation_number: Optional[str] = None
    latex_content: str
    surrounding_text: Optional[str] = None

class ComparisonMatrixEntry(BaseModel):
    criterion: str  # Research Objective, Methodology, Architecture, Datasets, Metrics, Results, Limitations, Future Work
    values: Dict[str, str]  # paper_id -> summary string
    evidence: Dict[str, List[Dict[str, Any]]]  # paper_id -> list of citations {page, section, snippet}

class StructuredComparisonRecord(BaseModel):
    id: str
    paper_ids: List[str]
    title: str
    matrix: List[ComparisonMatrixEntry]
    synthesis: str
    created_at: str

class ResearchGapRecord(BaseModel):
    id: str
    paper_ids: List[str]
    scope_notice: str = "Potential Research Gaps Identified Within the Selected Corpus."
    trends: List[str]
    common_methodologies: List[str]
    frequently_reported_limitations: List[Dict[str, Any]]
    unexplored_combinations: List[Dict[str, Any]]
    potential_research_questions: List[Dict[str, Any]]
    contradictory_findings: List[Dict[str, Any]]
    created_at: str

class CitationItem(BaseModel):
    paper_id: str
    paper_title: str
    page_number: int
    section_name: str
    snippet: str
    element_type: str = "text"
    confidence_score: float = 1.0

class VerifiedClaim(BaseModel):
    claim: str
    status: str  # verified, partially_supported, unsupported
    supporting_citations: List[CitationItem]
    confidence_score: float
    verification_notes: Optional[str] = None

class ChatResponse(BaseModel):
    query: str
    answer: str
    retrieval_mode: str
    claims: List[VerifiedClaim]
    citations: List[CitationItem]
    latency_seconds: float
    model_used: str

class BenchmarkResultRecord(BaseModel):
    id: str
    config_name: str
    timestamp: str
    sample_count: int
    precision_at_k: float
    recall_at_k: float
    mrr: float
    answer_correctness: float
    citation_accuracy: float
    faithfulness: float
    avg_response_latency: float
    avg_retrieval_latency: float
    detailed_metrics: Dict[str, Any]

