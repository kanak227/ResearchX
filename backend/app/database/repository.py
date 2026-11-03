import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..core.config import settings
from ..core.logging import logger
from .models import (
    PaperRecord,
    ExtractedElementRecord,
    StructuredComparisonRecord,
    ResearchGapRecord,
    BenchmarkResultRecord
)

class SQLiteRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Papers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    published_year INTEGER,
                    journal_venue TEXT,
                    page_count INTEGER DEFAULT 0,
                    doi TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    processing_status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    metadata_json TEXT
                )
            """)

            # Extracted Elements Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS elements (
                    id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    section_name TEXT NOT NULL,
                    element_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    raw_content TEXT,
                    source_coordinates TEXT,
                    extraction_method TEXT DEFAULT 'pymupdf',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
                )
            """)

            # Indexing for elements
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_paper ON elements(paper_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_type ON elements(element_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_page ON elements(paper_id, page_number)")

            # Structured Comparisons Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comparisons (
                    id TEXT PRIMARY KEY,
                    paper_ids TEXT NOT NULL,
                    title TEXT NOT NULL,
                    matrix TEXT NOT NULL,
                    synthesis TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Research Gaps Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_gaps (
                    id TEXT PRIMARY KEY,
                    paper_ids TEXT NOT NULL,
                    scope_notice TEXT NOT NULL,
                    trends TEXT NOT NULL,
                    common_methodologies TEXT NOT NULL,
                    frequently_reported_limitations TEXT NOT NULL,
                    unexplored_combinations TEXT NOT NULL,
                    potential_research_questions TEXT NOT NULL,
                    contradictory_findings TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Benchmark Runs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    id TEXT PRIMARY KEY,
                    config_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sample_count INTEGER NOT NULL,
                    precision_at_k REAL NOT NULL,
                    recall_at_k REAL NOT NULL,
                    mrr REAL NOT NULL,
                    answer_correctness REAL NOT NULL,
                    citation_accuracy REAL NOT NULL,
                    faithfulness REAL NOT NULL,
                    avg_response_latency REAL NOT NULL,
                    avg_retrieval_latency REAL NOT NULL,
                    detailed_metrics TEXT NOT NULL
                )
            """)

            conn.commit()
            logger.info("SQLite database initialized at: %s", self.db_path)

    # ---------------- Papers CRUD ---------------- #
    def create_paper(self, paper: PaperRecord) -> PaperRecord:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO papers (
                    id, filename, filepath, title, authors, abstract,
                    published_year, journal_venue, page_count, doi,
                    created_at, updated_at, processing_status, error_message, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.id,
                paper.filename,
                paper.filepath,
                paper.title,
                json.dumps(paper.authors),
                paper.abstract,
                paper.published_year,
                paper.journal_venue,
                paper.page_count,
                paper.doi,
                paper.created_at,
                paper.updated_at,
                paper.processing_status,
                paper.error_message,
                json.dumps(paper.metadata_json)
            ))
            conn.commit()
        return paper

    def get_paper(self, paper_id: str) -> Optional[PaperRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_paper(row)

    def list_papers(self) -> List[PaperRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_paper(r) for r in rows]

    def update_paper_status(
        self,
        paper_id: str,
        status: str,
        error_message: Optional[str] = None,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        abstract: Optional[str] = None,
        page_count: Optional[int] = None,
        metadata_json: Optional[Dict[str, Any]] = None
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = ["processing_status = ?", "updated_at = ?"]
            params = [status, datetime.utcnow().isoformat()]

            if error_message is not None:
                updates.append("error_message = ?")
                params.append(error_message)
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if authors is not None:
                updates.append("authors = ?")
                params.append(json.dumps(authors))
            if abstract is not None:
                updates.append("abstract = ?")
                params.append(abstract)
            if page_count is not None:
                updates.append("page_count = ?")
                params.append(page_count)
            if metadata_json is not None:
                updates.append("metadata_json = ?")
                params.append(json.dumps(metadata_json))

            params.append(paper_id)
            query = f"UPDATE papers SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()

    def delete_paper(self, paper_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM elements WHERE paper_id = ?", (paper_id,))
            cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
            conn.commit()

    def _row_to_paper(self, row: sqlite3.Row) -> PaperRecord:
        return PaperRecord(
            id=row["id"],
            filename=row["filename"],
            filepath=row["filepath"],
            title=row["title"],
            authors=json.loads(row["authors"]) if row["authors"] else [],
            abstract=row["abstract"] or "",
            published_year=row["published_year"],
            journal_venue=row["journal_venue"],
            page_count=row["page_count"] or 0,
            doi=row["doi"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            processing_status=row["processing_status"],
            error_message=row["error_message"],
            metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else {}
        )

    # ---------------- Extracted Elements CRUD ---------------- #
    def add_elements(self, elements: List[ExtractedElementRecord]):
        if not elements:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            records = [
                (
                    e.id,
                    e.paper_id,
                    e.page_number,
                    e.section_name,
                    e.element_type,
                    e.content,
                    e.raw_content,
                    json.dumps(e.source_coordinates) if e.source_coordinates else None,
                    e.extraction_method,
                    e.created_at
                )
                for e in elements
            ]
            cursor.executemany("""
                INSERT OR REPLACE INTO elements (
                    id, paper_id, page_number, section_name, element_type,
                    content, raw_content, source_coordinates, extraction_method, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()

    def get_elements_by_paper(self, paper_id: str, element_type: Optional[str] = None) -> List[ExtractedElementRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if element_type and isinstance(element_type, str):
                cursor.execute(
                    "SELECT * FROM elements WHERE paper_id = ? AND element_type = ? ORDER BY page_number ASC",
                    (paper_id, element_type)
                )
            else:
                cursor.execute(
                    "SELECT * FROM elements WHERE paper_id = ? ORDER BY page_number ASC",
                    (paper_id,)
                )
            rows = cursor.fetchall()
            return [self._row_to_element(r) for r in rows]

    def get_element_by_id(self, element_id: str) -> Optional[ExtractedElementRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM elements WHERE id = ?", (element_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_element(row)

    def _row_to_element(self, row: sqlite3.Row) -> ExtractedElementRecord:
        return ExtractedElementRecord(
            id=row["id"],
            paper_id=row["paper_id"],
            page_number=row["page_number"],
            section_name=row["section_name"],
            element_type=row["element_type"],
            content=row["content"],
            raw_content=row["raw_content"],
            source_coordinates=json.loads(row["source_coordinates"]) if row["source_coordinates"] else None,
            extraction_method=row["extraction_method"] or "pymupdf",
            created_at=row["created_at"]
        )

    # ---------------- Comparisons CRUD ---------------- #
    def save_comparison(self, comp: StructuredComparisonRecord):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO comparisons (
                    id, paper_ids, title, matrix, synthesis, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                comp.id,
                json.dumps(comp.paper_ids),
                comp.title,
                json.dumps([m.dict() for m in comp.matrix]),
                comp.synthesis,
                comp.created_at
            ))
            conn.commit()

    def list_comparisons(self) -> List[StructuredComparisonRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM comparisons ORDER BY created_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                matrix_data = json.loads(r["matrix"])
                results.append(StructuredComparisonRecord(
                    id=r["id"],
                    paper_ids=json.loads(r["paper_ids"]),
                    title=r["title"],
                    matrix=matrix_data,
                    synthesis=r["synthesis"],
                    created_at=r["created_at"]
                ))
            return results

    # ---------------- Research Gaps CRUD ---------------- #
    def save_research_gap(self, gap: ResearchGapRecord):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO research_gaps (
                    id, paper_ids, scope_notice, trends, common_methodologies,
                    frequently_reported_limitations, unexplored_combinations,
                    potential_research_questions, contradictory_findings, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gap.id,
                json.dumps(gap.paper_ids),
                gap.scope_notice,
                json.dumps(gap.trends),
                json.dumps(gap.common_methodologies),
                json.dumps(gap.frequently_reported_limitations),
                json.dumps(gap.unexplored_combinations),
                json.dumps(gap.potential_research_questions),
                json.dumps(gap.contradictory_findings),
                gap.created_at
            ))
            conn.commit()

    def list_research_gaps(self) -> List[ResearchGapRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM research_gaps ORDER BY created_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append(ResearchGapRecord(
                    id=r["id"],
                    paper_ids=json.loads(r["paper_ids"]),
                    scope_notice=r["scope_notice"],
                    trends=json.loads(r["trends"]),
                    common_methodologies=json.loads(r["common_methodologies"]),
                    frequently_reported_limitations=json.loads(r["frequently_reported_limitations"]),
                    unexplored_combinations=json.loads(r["unexplored_combinations"]),
                    potential_research_questions=json.loads(r["potential_research_questions"]),
                    contradictory_findings=json.loads(r["contradictory_findings"]),
                    created_at=r["created_at"]
                ))
            return results

    # ---------------- Benchmark Runs CRUD ---------------- #
    def save_benchmark_run(self, run: BenchmarkResultRecord):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO benchmark_runs (
                    id, config_name, timestamp, sample_count,
                    precision_at_k, recall_at_k, mrr, answer_correctness,
                    citation_accuracy, faithfulness, avg_response_latency,
                    avg_retrieval_latency, detailed_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.id,
                run.config_name,
                run.timestamp,
                run.sample_count,
                run.precision_at_k,
                run.recall_at_k,
                run.mrr,
                run.answer_correctness,
                run.citation_accuracy,
                run.faithfulness,
                run.avg_response_latency,
                run.avg_retrieval_latency,
                json.dumps(run.detailed_metrics)
            ))
            conn.commit()

    def list_benchmark_runs(self) -> List[BenchmarkResultRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM benchmark_runs ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append(BenchmarkResultRecord(
                    id=r["id"],
                    config_name=r["config_name"],
                    timestamp=r["timestamp"],
                    sample_count=r["sample_count"],
                    precision_at_k=r["precision_at_k"],
                    recall_at_k=r["recall_at_k"],
                    mrr=r["mrr"],
                    answer_correctness=r["answer_correctness"],
                    citation_accuracy=r["citation_accuracy"],
                    faithfulness=r["faithfulness"],
                    avg_response_latency=r["avg_response_latency"],
                    avg_retrieval_latency=r["avg_retrieval_latency"],
                    detailed_metrics=json.loads(r["detailed_metrics"])
                ))
            return results

db_repo = SQLiteRepository()
