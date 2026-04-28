"""Trust score calculation for scraped sources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from dateutil import parser as date_parser


TRUSTED_DOMAINS = {
    "pubmed.ncbi.nlm.nih.gov": 0.98,
    "ncbi.nlm.nih.gov": 0.98,
    "nih.gov": 0.96,
    "who.int": 0.95,
    "realpython.com": 0.82,
    "scrapingbee.com": 0.78,
    "apify.com": 0.78,
    "freecodecamp.org": 0.76,
    "dataquest.io": 0.74,
    "youtube.com": 0.55,
    "www.youtube.com": 0.55,
}

AUTHOR_HINTS = {
    "pubmed": 0.95,
    "nih": 0.95,
    "real python": 0.82,
    "scrapingbee": 0.78,
    "apify": 0.78,
    "freecodecamp": 0.75,
    "3blue1brown": 0.72,
}


@dataclass
class ScoreBreakdown:
    author_credibility: float
    citation_count: float
    domain_authority: float
    recency: float
    medical_disclaimer_presence: float
    final_score: float


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def score_author(author: str | list[str] | None) -> float:
    if isinstance(author, list):
        if not author:
            return 0.45
        return sum(score_author(item) for item in author) / len(author)
    if not author:
        return 0.45
    lowered = author.lower()
    for hint, score in AUTHOR_HINTS.items():
        if hint in lowered:
            return score
    if "," in author or " and " in lowered:
        return 0.65
    return 0.55


def score_citations(citation_count: int | None) -> float:
    if citation_count is None:
        return 0.5
    if citation_count <= 0:
        return 0.35
    if citation_count >= 100:
        return 1.0
    return clamp(0.35 + (citation_count / 100) * 0.65)


def score_domain(url: str) -> float:
    host = urlparse(url).netloc.lower().replace("www.", "")
    if host in TRUSTED_DOMAINS:
        return TRUSTED_DOMAINS[host]
    for domain, score in TRUSTED_DOMAINS.items():
        if host.endswith(domain.replace("www.", "")):
            return score
    return 0.5


def score_recency(published_date: str | None) -> float:
    if not published_date:
        return 0.45
    try:
        parsed = date_parser.parse(str(published_date), fuzzy=True)
        if not parsed.tzinfo:
            parsed = parsed.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return 0.45

    age_days = max(0, (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days)
    if age_days <= 365:
        return 1.0
    if age_days <= 365 * 3:
        return 0.85
    if age_days <= 365 * 5:
        return 0.65
    if age_days <= 365 * 10:
        return 0.45
    return 0.25


def score_medical_disclaimer(text: str, source_type: str) -> float:
    lowered = (text or "").lower()
    medical_terms = {"medical", "health", "clinical", "patient", "disease", "treatment"}
    has_medical_content = any(term in lowered for term in medical_terms) or source_type == "pubmed"
    if not has_medical_content:
        return 0.75
    disclaimer_terms = ("not medical advice", "consult", "clinician", "healthcare professional", "physician")
    return 1.0 if any(term in lowered for term in disclaimer_terms) or source_type == "pubmed" else 0.35


def calculate_trust_score(
    *,
    source_url: str,
    source_type: str,
    author: str | list[str] | None,
    published_date: str | None,
    text: str,
    citation_count: int | None = None,
) -> dict[str, float]:
    """Return a weighted trust score from 0 to 1 with component scores."""
    breakdown = ScoreBreakdown(
        author_credibility=score_author(author),
        citation_count=score_citations(citation_count),
        domain_authority=score_domain(source_url),
        recency=score_recency(published_date),
        medical_disclaimer_presence=score_medical_disclaimer(text, source_type),
        final_score=0.0,
    )
    final = (
        breakdown.author_credibility * 0.25
        + breakdown.citation_count * 0.15
        + breakdown.domain_authority * 0.25
        + breakdown.recency * 0.20
        + breakdown.medical_disclaimer_presence * 0.15
    )
    breakdown.final_score = round(clamp(final), 3)
    return {
        "author_credibility": round(breakdown.author_credibility, 3),
        "citation_count": round(breakdown.citation_count, 3),
        "domain_authority": round(breakdown.domain_authority, 3),
        "recency": round(breakdown.recency, 3),
        "medical_disclaimer_presence": round(breakdown.medical_disclaimer_presence, 3),
        "final_score": breakdown.final_score,
    }
