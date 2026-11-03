import re
from typing import List, Dict, Any, Optional
from ..database.models import ExtractedElementRecord
from ..core.logging import logger

class EquationExtractor:
    def __init__(self):
        # Detect common equation numbering patterns like (1), (2.1), Eq. 3
        self.eq_number_pattern = re.compile(
            r"(\((?:\d+|\d+\.\d+|[a-zA-Z]\d*)\))\s*$"
        )
        # Mathematical symbol cues
        self.math_symbols = set([
            "∑", "∏", "∫", "∂", "√", "∈", "∉", "⊆", "⊂", "∀", "∃",
            "∇", "≤", "≥", "≠", "≈", "≡", "×", "÷", "±", "→", "⇒",
            "α", "β", "γ", "δ", "ϵ", "θ", "λ", "μ", "σ", "ω", "π",
            "argmax", "argmin", "min", "max", "softmax", "log", "exp",
            "\\mathcal", "\\mathbb", "\\sum", "\\prod", "\\frac"
        ])

    def extract_from_page(
        self,
        doc,
        page_num: int,
        paper_id: str,
        section_name: str = "Methodology"
    ) -> List[ExtractedElementRecord]:
        """
        Extracts mathematical equations and formulas with equation numbers and context.
        """
        page = doc[page_num - 1]
        elements: List[ExtractedElementRecord] = []

        try:
            text_page = page.get_text("dict")
            blocks = text_page.get("blocks", [])

            for b_idx, block in enumerate(blocks):
                if block.get("type") != 0:
                    continue

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
                math_cue_count = 0
                has_math_font = False

                for line in block.get("lines", []):
                    line_str = ""
                    for span in line.get("spans", []):
                        span_text = span.get("text", "")
                        line_str += span_text
                        font_name = span.get("font", "").lower()
                        if any(mf in font_name for mf in ["math", "symbol", "cmmi", "cmsy", "cmex", "msam"]):
                            has_math_font = True
                    block_text += line_str + "\n"

                block_text = block_text.strip()
                if not block_text:
                    continue

                # Count math symbols
                for sym in self.math_symbols:
                    if sym in block_text:
                        math_cue_count += 1

                # Check if this block ends with equation numbering (1), (2), etc.
                match_eq = self.eq_number_pattern.search(block_text)
                is_equation = False
                eq_num = None

                if match_eq and (math_cue_count >= 1 or has_math_font or "=" in block_text):
                    is_equation = True
                    eq_num = match_eq.group(1)
                elif has_math_font and ("=" in block_text or "∈" in block_text) and len(block_text.splitlines()) <= 3:
                    is_equation = True

                if is_equation:
                    clean_formula = block_text.replace("\n", " ").strip()
                    element = ExtractedElementRecord(
                        id=f"{paper_id}_p{page_num}_eq_{b_idx}",
                        paper_id=paper_id,
                        page_number=page_num,
                        section_name=section_name,
                        element_type="equation",
                        content=f"**Equation {eq_num or ''}**\n\n$$\n{clean_formula}\n$$",
                        raw_content=clean_formula,
                        source_coordinates=coords,
                        extraction_method="pymupdf_math_heuristics",
                        created_at=""
                    )
                    elements.append(element)

        except Exception as e:
            logger.warning("Error in EquationExtractor for paper %s page %d: %s", paper_id, page_num, e)

        return elements

equation_extractor = EquationExtractor()

