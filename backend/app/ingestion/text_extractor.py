import re
from typing import List, Dict, Any, Optional, Tuple
from ..database.models import ExtractedElementRecord
from ..core.logging import logger

class TextExtractor:
    def __init__(self):
        # Common section heading patterns in scientific papers
        self.heading_pattern = re.compile(
            r"^(\d+(\.\d+)*\s+)?([A-Z][A-Za-z0-9\s,\-–:]{2,60})$"
        )
        self.known_sections = {
            "abstract", "introduction", "background", "related work", "literature review",
            "methodology", "methods", "proposed method", "system architecture", "approach",
            "experiments", "experimental setup", "results", "discussion", "evaluation",
            "ablation study", "limitations", "future work", "conclusion", "conclusions",
            "acknowledgments", "references"
        }

    def extract_from_page(
        self,
        doc,
        page_num: int,
        paper_id: str,
        current_section: str = "Introduction"
    ) -> Tuple[List[ExtractedElementRecord], str]:
        """
        Extracts structured text paragraphs and section headers from a PyMuPDF page.
        Returns:
            elements: List of ExtractedElementRecord
            updated_section: The current section heading at the end of the page
        """
        page = doc[page_num - 1]
        elements: List[ExtractedElementRecord] = []
        
        # Extract detailed text blocks with font information
        text_page = page.get_text("dict")
        blocks = text_page.get("blocks", [])

        # Calculate median font size on the page to identify headings
        font_sizes = []
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_sizes.append(span.get("size", 10.0))
        
        body_font_size = sum(font_sizes) / max(len(font_sizes), 1) if font_sizes else 10.0

        for b_idx, block in enumerate(blocks):
            if block.get("type") != 0:
                continue  # Skip image blocks (handled by FigureExtractor)

            bbox = block.get("bbox", [0, 0, 0, 0])
            coords = {
                "x0": round(bbox[0], 2),
                "y0": round(bbox[1], 2),
                "x1": round(bbox[2], 2),
                "y1": round(bbox[3], 2),
                "width": round(bbox[2] - bbox[0], 2),
                "height": round(bbox[3] - bbox[1], 2),
            }

            block_text = ""
            max_span_size = 0.0
            is_bold = False

            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    size = span.get("size", 0.0)
                    if size > max_span_size:
                        max_span_size = size
                    flags = span.get("flags", 0)
                    if flags & 2 or "Bold" in span.get("font", ""):
                        is_bold = True
                block_text += line_text.strip() + " "

            block_text = block_text.strip()
            if not block_text or len(block_text) < 3:
                continue

            # Check if this block is a section header
            cleaned_lower = block_text.lower().strip()
            # Remove leading numbers like "1.", "1.1", "2."
            normalized_heading = re.sub(r"^\d+(\.\d+)*\s*", "", cleaned_lower).strip()

            is_heading = False
            if normalized_heading in self.known_sections:
                is_heading = True
            elif (max_span_size > body_font_size * 1.15 or is_bold) and len(block_text) < 80:
                if self.heading_pattern.match(block_text):
                    is_heading = True

            if is_heading:
                current_section = block_text.strip()
                element = ExtractedElementRecord(
                    id=f"{paper_id}_p{page_num}_sec_{b_idx}",
                    paper_id=paper_id,
                    page_number=page_num,
                    section_name=current_section,
                    element_type="text",
                    content=f"## {block_text}",
                    raw_content=block_text,
                    source_coordinates=coords,
                    extraction_method="pymupdf_header",
                    created_at=""
                )
                elements.append(element)
            else:
                # Regular paragraph
                element = ExtractedElementRecord(
                    id=f"{paper_id}_p{page_num}_txt_{b_idx}",
                    paper_id=paper_id,
                    page_number=page_num,
                    section_name=current_section,
                    element_type="text",
                    content=block_text,
                    raw_content=block_text,
                    source_coordinates=coords,
                    extraction_method="pymupdf_layout",
                    created_at=""
                )
                elements.append(element)

        return elements, current_section

text_extractor = TextExtractor()

