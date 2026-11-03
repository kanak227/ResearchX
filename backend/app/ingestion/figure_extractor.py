import os
import re
from typing import List, Dict, Any, Optional
from PIL import Image
import io
from ..core.config import settings
from ..core.logging import logger
from ..database.models import ExtractedElementRecord

class FigureExtractor:
    def __init__(self):
        self.caption_pattern = re.compile(
            r"^(fig(?:ure)?\.?\s+(\d+|[ivx]+)[:.\-\s]+[^\n]+)", re.IGNORECASE
        )

    def extract_from_page(
        self,
        doc,
        page_num: int,
        paper_id: str,
        section_name: str = "Architecture"
    ) -> List[ExtractedElementRecord]:
        """
        Extracts figures, diagrams, and associated captions from a PyMuPDF page.
        Saves cropped images to disk and generates metadata.
        """
        page = doc[page_num - 1]
        elements: List[ExtractedElementRecord] = []
        figures_dir = os.path.join(settings.EXTRACTED_DIR, paper_id, "figures")
        os.makedirs(figures_dir, exist_ok=True)

        try:
            # 1. Search page text for figure captions
            page_text = page.get_text("text")
            lines = [l.strip() for l in page_text.splitlines() if l.strip()]
            captions = []
            for line in lines:
                match = self.caption_pattern.match(line)
                if match:
                    captions.append(match.group(1).strip())

            # 2. Extract embedded images
            image_list = page.get_images(full=True)
            for img_idx, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Filter out tiny icon/bullet images (< 60px)
                    width = base_image["width"]
                    height = base_image["height"]
                    if width < 80 or height < 80:
                        continue

                    # Try to locate image bbox on page
                    rects = page.get_image_rects(xref)
                    bbox = rects[0] if rects else None
                    coords = {}
                    if bbox:
                        coords = {
                            "x0": round(bbox.x0, 2),
                            "y0": round(bbox.y0, 2),
                            "x1": round(bbox.x1, 2),
                            "y1": round(bbox.y1, 2),
                            "width": round(bbox.width, 2),
                            "height": round(bbox.height, 2),
                        }

                    fig_filename = f"fig_p{page_num}_{img_idx}.{image_ext}"
                    fig_rel_path = f"extracted/{paper_id}/figures/{fig_filename}"
                    fig_abs_path = os.path.join(figures_dir, fig_filename)

                    with open(fig_abs_path, "wb") as f:
                        f.write(image_bytes)

                    # Match with available caption or generate descriptive title
                    caption = captions[img_idx] if img_idx < len(captions) else f"Figure on page {page_num}"

                    # Detect visual type heuristically
                    cap_lower = caption.lower()
                    if any(k in cap_lower for k in ["architecture", "overview", "pipeline", "framework", "flow"]):
                        detected_type = "architecture_diagram"
                    elif any(k in cap_lower for k in ["curve", "plot", "roc", "accuracy", "loss", "graph", "histogram"]):
                        detected_type = "quantitative_graph"
                    else:
                        detected_type = "scientific_figure"

                    description = f"{caption}. High-resolution visual element representing {detected_type.replace('_', ' ')}."

                    element = ExtractedElementRecord(
                        id=f"{paper_id}_p{page_num}_fig_{img_idx}",
                        paper_id=paper_id,
                        page_number=page_num,
                        section_name=section_name,
                        element_type="figure",
                        content=f"**[{detected_type.upper()}]** {caption}\n\n*Image Path:* `{fig_rel_path}`\n\n{description}",
                        raw_content=str({
                            "caption": caption,
                            "image_path": fig_rel_path,
                            "type": detected_type,
                            "dimensions": {"width": width, "height": height}
                        }),
                        source_coordinates=coords,
                        extraction_method="pymupdf_image_xref",
                        created_at=""
                    )
                    elements.append(element)

                except Exception as img_err:
                    logger.debug("Failed extracting image xref %s: %s", xref, img_err)

        except Exception as e:
            logger.warning("Error in FigureExtractor for paper %s page %d: %s", paper_id, page_num, e)

        return elements

figure_extractor = FigureExtractor()

