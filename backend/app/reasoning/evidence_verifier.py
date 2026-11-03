import re
from typing import List, Dict, Any, Tuple
from ..database.models import VerifiedClaim, CitationItem
from ..core.logging import logger

class EvidenceVerifier:
    def __init__(self):
        # Stopwords to exclude from overlap calculations
        self.stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "by", "for",
            "with", "about", "against", "between", "into", "through", "during", "before",
            "after", "above", "below", "to", "from", "up", "down", "in", "out", "of",
            "and", "but", "or", "as", "if", "this", "that", "these", "those", "it", "its"
        }

    def tokenize_clean(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        return [w for w in words if w not in self.stopwords]

    def decompose_into_claims(self, text: str) -> List[str]:
        """
        Decomposes generated text into atomic verifiable claims.
        Splits by sentences and bullet points, filtering out conversational boilerplate.
        """
        # Split by newlines and sentence punctuation
        raw_units = []
        for line in text.splitlines():
            line = line.strip()
            # Clean markdown formatting
            cleaned_line = re.sub(r"^[-*#>\s]+", "", line).strip()
            if not cleaned_line or len(cleaned_line) < 15:
                continue
            # Split line into sentences
            sentences = re.split(r"(?<=[.!?])\s+", cleaned_line)
            raw_units.extend([s.strip() for s in sentences if len(s.strip()) >= 15])

        # Filter out meta/intro sentences
        filtered_claims = []
        for unit in raw_units:
            unit_lower = unit.lower()
            if any(unit_lower.startswith(prefix) for prefix in [
                "based on the retrieved", "here is the summary", "in conclusion",
                "according to the provided", "the papers discuss"
            ]):
                continue
            filtered_claims.append(unit)

        return filtered_claims if filtered_claims else ([text] if text else [])

    def verify_response(
        self,
        answer_text: str,
        retrieved_evidence: List[Dict[str, Any]]
    ) -> Tuple[List[VerifiedClaim], List[CitationItem], float]:
        """
        Validates the generated answer against the retrieved evidence.
        Returns:
            claims: List of VerifiedClaim with status and confidence
            citations: Unified list of CitationItem
            overall_faithfulness: Float score between 0.0 and 1.0
        """
        claims = self.decompose_into_claims(answer_text)
        verified_claims: List[VerifiedClaim] = []
        all_citations: List[CitationItem] = []

        if not claims or not retrieved_evidence:
            return [], [], 0.0

        total_score = 0.0

        for claim in claims:
            claim_tokens = set(self.tokenize_clean(claim))
            # Also extract numerical values in claim (e.g. 94.2%, 0.85, 1024)
            claim_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", claim))

            best_match_score = 0.0
            best_evidence = None
            supporting_citations: List[CitationItem] = []

            for ev in retrieved_evidence:
                payload = ev.get("payload", {})
                content = payload.get("content", "")
                content_tokens = set(self.tokenize_clean(content))
                content_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", content))

                # Word overlap score (Jaccard-like recall)
                overlap = len(claim_tokens.intersection(content_tokens))
                word_score = overlap / max(len(claim_tokens), 1)

                # Numbers precision check: if claim has numbers, ensure they appear in evidence
                num_score = 1.0
                if claim_numbers:
                    num_overlap = len(claim_numbers.intersection(content_numbers))
                    num_score = num_overlap / len(claim_numbers)

                composite_match = (word_score * 0.7) + (num_score * 0.3)

                if composite_match > 0.3:
                    cit = CitationItem(
                        paper_id=payload.get("paper_id", "unknown"),
                        paper_title=payload.get("paper_title", "Research Paper"),
                        page_number=payload.get("page_number", 1),
                        section_name=payload.get("section_name", "General"),
                        snippet=content[:250],
                        element_type=payload.get("element_type", "text"),
                        confidence_score=round(composite_match, 3)
                    )
                    supporting_citations.append(cit)
                    if cit not in all_citations:
                        all_citations.append(cit)

                if composite_match > best_match_score:
                    best_match_score = composite_match
                    best_evidence = payload

            # Determine claim status
            if best_match_score >= 0.55:
                status = "verified"
                confidence = min(round(best_match_score, 3), 1.0)
                notes = "Strong textual and metric grounding in retrieved source."
            elif best_match_score >= 0.30:
                status = "partially_supported"
                confidence = round(best_match_score, 3)
                notes = "Partially grounded; conceptual overlap present but may contain slight extrapolations."
            else:
                status = "unsupported"
                confidence = round(best_match_score, 3)
                notes = "Flagged: Low evidence overlap. Verify against primary document."

            total_score += best_match_score
            verified_claims.append(VerifiedClaim(
                claim=claim,
                status=status,
                supporting_citations=supporting_citations[:3],
                confidence_score=confidence,
                verification_notes=notes
            ))

        overall_faithfulness = round(total_score / max(len(claims), 1), 3)
        return verified_claims, all_citations, min(overall_faithfulness, 1.0)

evidence_verifier = EvidenceVerifier()

