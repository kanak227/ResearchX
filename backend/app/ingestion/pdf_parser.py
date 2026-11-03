import os
import re
import fitz  # PyMuPDF
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..core.config import settings
from ..core.logging import logger
from ..database.models import PaperRecord, ExtractedElementRecord, PaperMetadata
from ..database.repository import db_repo
from .text_extractor import text_extractor
from .table_extractor import table_extractor
from .figure_extractor import figure_extractor
from .equation_extractor import equation_extractor

class PDFParser:
    def __init__(self):
        pass

    def validate_pdf(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            doc = fitz.open(filepath)
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
        except Exception:
            return False

    def extract_metadata_from_doc(self, doc, filename: str) -> PaperMetadata:
        """
        Extracts title, authors, abstract, publication year, DOI, venue from PyMuPDF document.
        """
        meta = doc.metadata or {}
        raw_title = meta.get("title", "").strip()
        raw_author = meta.get("author", "").strip()

        # Fallback to visual heuristics on page 1 if metadata is missing or generic
        page1 = doc[0]
        text_dict = page1.get_text("dict")
        blocks = text_dict.get("blocks", [])

        title = raw_title
        authors = [a.strip() for a in raw_author.split(";") if a.strip()] if raw_author else []
        abstract = ""
        year = None
        doi = None

        # Check font sizes on page 1 to locate title
        max_font_size = 0.0
        candidate_title = ""
        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    line_text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                    for span in line.get("spans", []):
                        size = span.get("size", 0.0)
                        if size > max_font_size and len(line_text) > 5:
                            max_font_size = size
                            candidate_title = line_text

        if not title or len(title) < 4 or title.lower().endswith(".pdf"):
            title = candidate_title if candidate_title else os.path.splitext(filename)[0].replace("_", " ")

        # Look for Abstract block
        page1_text = page1.get_text("text")
        abstract_match = re.search(r"abstract[\s:—–\-]+(.*?)(?=\n\s*(?:1\.?|i\.|introduction|keywords)|\Z)", page1_text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Clean up linebreaks
            abstract = re.sub(r"\s+", " ", abstract)

        # Look for year and DOI
        doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", page1_text)
        if doi_match:
            doi = doi_match.group(1)

        year_match = re.search(r"\b(19\d{2}|20[0-2]\d)\b", page1_text)
        if year_match:
            year = int(year_match.group(1))

        # Infer authors if empty
        if not authors:
            # Typically lines between title and abstract
            lines = [l.strip() for l in page1_text.splitlines() if l.strip()]
            for l in lines[:10]:
                if l != title and "abstract" not in l.lower() and "@" in l or "," in l:
                    potential = [p.strip() for p in l.split(",") if len(p.strip()) > 2]
                    if potential and len(potential) <= 10:
                        authors = potential
                        break

        if not authors:
            authors = ["Unknown Authors"]

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            published_year=year,
            journal_venue=meta.get("subject") or "Scientific Publication",
            page_count=len(doc),
            doi=doi
        )

    def process_paper(self, paper_id: str, filepath: str) -> Dict[str, Any]:
        """
        Executes the full multimodal ingestion pipeline on the PDF file.
        Extracts structured text, tables, figures, equations with exact page provenance.
        """
        logger.info("Starting ingestion pipeline for paper: %s (%s)", paper_id, filepath)
        now_str = datetime.utcnow().isoformat()

        if not self.validate_pdf(filepath):
            err_msg = f"Invalid or unreadable PDF: {filepath}"
            logger.error(err_msg)
            db_repo.update_paper_status(paper_id, status="failed", error_message=err_msg)
            raise ValueError(err_msg)

        doc = fitz.open(filepath)

        existing_paper = db_repo.get_paper(paper_id)
        if not existing_paper:
            new_paper = PaperRecord(
                id=paper_id,
                filename=os.path.basename(filepath),
                filepath=filepath,
                title=os.path.splitext(os.path.basename(filepath))[0].replace("_", " "),
                authors=[],
                abstract="",
                page_count=len(doc),
                created_at=now_str,
                updated_at=now_str,
                processing_status="processing"
            )
            db_repo.create_paper(new_paper)
        else:
            db_repo.update_paper_status(paper_id, status="processing")

        try:
            # 1. Extract metadata
            metadata = self.extract_metadata_from_doc(doc, os.path.basename(filepath))

            # 2. Iterate pages and run element extractors
            all_elements: List[ExtractedElementRecord] = []
            current_section = "Introduction"
            total_tables = 0
            total_figures = 0
            total_equations = 0

            for page_idx in range(len(doc)):
                page_num = page_idx + 1

                # A. Text elements & section tracking
                text_elems, current_section = text_extractor.extract_from_page(
                    doc=doc,
                    page_num=page_num,
                    paper_id=paper_id,
                    current_section=current_section
                )
                for elem in text_elems:
                    elem.created_at = now_str
                all_elements.extend(text_elems)

                # B. Table elements
                tbl_elems = table_extractor.extract_from_page(
                    doc=doc,
                    page_num=page_num,
                    paper_id=paper_id,
                    section_name=current_section
                )
                for elem in tbl_elems:
                    elem.created_at = now_str
                all_elements.extend(tbl_elems)
                total_tables += len(tbl_elems)

                # C. Figure elements
                fig_elems = figure_extractor.extract_from_page(
                    doc=doc,
                    page_num=page_num,
                    paper_id=paper_id,
                    section_name=current_section
                )
                for elem in fig_elems:
                    elem.created_at = now_str
                all_elements.extend(fig_elems)
                total_figures += len(fig_elems)

                # D. Equation elements
                eq_elems = equation_extractor.extract_from_page(
                    doc=doc,
                    page_num=page_num,
                    paper_id=paper_id,
                    section_name=current_section
                )
                for elem in eq_elems:
                    elem.created_at = now_str
                all_elements.extend(eq_elems)
                total_equations += len(eq_elems)

            metadata.total_tables = total_tables
            metadata.total_figures = total_figures
            metadata.total_equations = total_equations
            metadata.total_sections = len(set(e.section_name for e in all_elements))

            # 3. Persist elements in SQLite
            db_repo.add_elements(all_elements)

            # 4. Save cached extracted structure to disk
            extracted_json_path = os.path.join(settings.EXTRACTED_DIR, paper_id, "structure.json")
            os.makedirs(os.path.dirname(extracted_json_path), exist_ok=True)
            with open(extracted_json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "paper_id": paper_id,
                    "metadata": metadata.dict(),
                    "element_count": len(all_elements),
                    "elements": [e.dict() for e in all_elements]
                }, f, indent=2)

            # 5. Update paper record
            db_repo.update_paper_status(
                paper_id=paper_id,
                status="completed",
                title=metadata.title,
                authors=metadata.authors,
                abstract=metadata.abstract,
                page_count=len(doc),
                metadata_json=metadata.dict()
            )

            logger.info(
                "Ingestion completed for paper %s: %d total elements (%d tables, %d figures, %d equations)",
                paper_id, len(all_elements), total_tables, total_figures, total_equations
            )

            return {
                "paper_id": paper_id,
                "title": metadata.title,
                "authors": metadata.authors,
                "abstract": metadata.abstract,
                "page_count": len(doc),
                "total_elements": len(all_elements),
                "total_tables": total_tables,
                "total_figures": total_figures,
                "total_equations": total_equations,
                "status": "completed"
            }

        except Exception as e:
            logger.error("Failed processing paper %s: %s", paper_id, e, exc_info=True)
            db_repo.update_paper_status(paper_id, status="failed", error_message=str(e))
            raise e
        finally:
            doc.close()

pdf_parser = PDFParser()
