"""Simple topic tagging and language detection logic."""

from __future__ import annotations

import re
from collections import Counter


STOP_WORDS = {
    "about", "after", "also", "and", "are", "because", "been", "but", "can",
    "could", "data", "does", "for", "from", "has", "have", "into", "its",
    "more", "not", "our", "than", "that", "the", "their", "then", "there",
    "these", "this", "through", "use", "used", "using", "was", "were", "when",
    "where", "which", "with", "you", "your"
}

KEYWORD_TOPICS = {
    "ai": {"ai", "artificial", "intelligence", "machine", "learning", "model", "neural"},
    "web scraping": {"scraping", "scraper", "crawl", "crawler", "html", "beautifulsoup", "requests"},
    "python": {"python", "pip", "package", "script", "django", "flask"},
    "healthcare": {"health", "medical", "medicine", "clinical", "patient", "disease", "doctor"},
    "research": {"study", "trial", "journal", "abstract", "pubmed", "citation", "research"},
    "programming": {"code", "programming", "software", "developer", "function", "library"},
    "education": {"course", "learn", "tutorial", "lesson", "video", "training"},
}


def detect_language(text: str) -> str:
    """Lightweight language detector for this assignment dataset."""
    if not text:
        return "unknown"
    ascii_letters = sum(1 for char in text if char.isascii() and char.isalpha())
    letters = sum(1 for char in text if char.isalpha())
    if letters and ascii_letters / letters > 0.85:
        return "en"
    return "unknown"


def generate_topic_tags(text: str, limit: int = 6) -> list[str]:
    """Generate keyword-based topic tags without requiring an external model."""
    words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z+-]{2,}", text or "")]
    word_set = set(words)

    tags: list[str] = []
    for topic, keywords in KEYWORD_TOPICS.items():
        if word_set & keywords:
            tags.append(topic)

    counts = Counter(word for word in words if word not in STOP_WORDS and len(word) > 3)
    for word, _ in counts.most_common(10):
        if word not in tags:
            tags.append(word)
        if len(tags) >= limit:
            break

    return tags[:limit]
