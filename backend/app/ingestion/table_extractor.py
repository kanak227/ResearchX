import re
from typing import List, Dict, Any, Optional
from ..database.models import ExtractedElementRecord, TableRecord
from ..core.logging import logger

class TableExtractor:
    def __init__(self):
        self.caption_pattern = re.compile(
            r"^(table\s+(\d+|[ivx]+)[:.\-\s]+[^\n]+)", re.IGNORECASE
        )

    def extract_from_page(
        self,
        doc,
        page_num: int,
        paper_id: str,
        section_name: str = "Experiments"
    ) -> List[ExtractedElementRecord]:
        """
        Extracts structured tables from a PyMuPDF page.
        Employs page.find_tables() with bounding box and cell structure extraction.
        """
        page = doc[page_num - 1]
        elements: List[ExtractedElementRecord] = []

        try:
            # 1. PyMuPDF built-in high performance table finder for vector line grids
            tabs = page.find_tables()
            if tabs and len(tabs.tables) > 0:
                page_text = page.get_text("text")
                lines = [l.strip() for l in page_text.splitlines() if l.strip()]

                for t_idx, tab in enumerate(tabs.tables):
                    bbox = tab.bbox  # (x0, y0, x1, y1)
                    coords = {
                        "x0": round(bbox[0], 2),
                        "y0": round(bbox[1], 2),
                        "x1": round(bbox[2], 2),
                        "y1": round(bbox[3], 2),
                        "width": round(bbox[2] - bbox[0], 2),
                        "height": round(bbox[3] - bbox[1], 2),
                    }

                    extracted_data = tab.extract()
                    if not extracted_data or len(extracted_data) < 2:
                        continue

                    raw_headers = extracted_data[0]
                    headers = [str(h).strip() if h is not None else f"Col_{i}" for i, h in enumerate(raw_headers)]
                    
                    rows = []
                    for row in extracted_data[1:]:
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        if any(cleaned_row):
                            rows.append(cleaned_row)

                    if not rows:
                        continue

                    caption = f"Table {t_idx + 1}"
                    for line in lines:
                        match = self.caption_pattern.match(line)
                        if match:
                            caption = match.group(1).strip()
                            break

                    header_line = "| " + " | ".join(headers) + " |"
                    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
                    data_lines = ["| " + " | ".join(row) + " |" for row in rows]
                    markdown_table = f"### {caption}\n\n" + "\n".join([header_line, sep_line] + data_lines)

                    elements.append(ExtractedElementRecord(
                        id=f"{paper_id}_p{page_num}_tbl_{t_idx}",
                        paper_id=paper_id,
                        page_number=page_num,
                        section_name=section_name,
                        element_type="table",
                        content=markdown_table,
                        raw_content=str({
                            "caption": caption,
                            "columns": headers,
                            "rows": rows,
                            "row_count": len(rows),
                            "column_count": len(headers)
                        }),
                        source_coordinates=coords,
                        extraction_method="pymupdf_find_tables",
                        created_at=""
                    ))

            # 2. Text Pipe-Table & Delimited Table Fallback Detection
            page_text = page.get_text("text")
            lines = [l.strip() for l in page_text.splitlines() if l.strip()]
            pipe_table_lines = [l for l in lines if l.startswith("|") and l.endswith("|") and "|" in l[1:-1]]
            
            if len(pipe_table_lines) >= 3 and len(elements) == 0:
                caption = f"Table on page {page_num}"
                for l in lines:
                    match = self.caption_pattern.match(l)
                    if match:
                        caption = match.group(1).strip()
                        break
                
                # Parse headers and rows
                header_row = [c.strip() for c in pipe_table_lines[0].strip("|").split("|")]
                data_rows = []
                for row_line in pipe_table_lines[1:]:
                    if "---" in row_line:
                        continue
                    cells = [c.strip() for c in row_line.strip("|").split("|")]
                    if any(cells):
                        data_rows.append(cells)

                markdown_table = f"### {caption}\n\n" + "\n".join(pipe_table_lines)
                elements.append(ExtractedElementRecord(
                    id=f"{paper_id}_p{page_num}_tbl_text",
                    paper_id=paper_id,
                    page_number=page_num,
                    section_name=section_name,
                    element_type="table",
                    content=markdown_table,
                    raw_content=str({
                        "caption": caption,
                        "columns": header_row,
                        "rows": data_rows,
                        "row_count": len(data_rows),
                        "column_count": len(header_row)
                    }),
                    source_coordinates={"x0": 50.0, "y0": 150.0, "x1": 545.0, "y1": 300.0, "width": 495.0, "height": 150.0},
                    extraction_method="text_pipe_parser",
                    created_at=""
                ))

        except Exception as e:
            logger.warning("Error extracting tables from paper %s page %d: %s", paper_id, page_num, e)

        return elements

table_extractor = TableExtractor()
