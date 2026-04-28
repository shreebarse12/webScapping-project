"""Blog/article scraper."""

from __future__ import annotations

from scraper.common import canonical_url, clean, first_text, meta_content, soup_from_url
from scoring.trust_score import calculate_trust_score
from utils.chunking import chunk_text
from utils.tagging import detect_language, generate_topic_tags


NOISE_SELECTORS = [
    "script", "style", "noscript", "nav", "footer", "header", "aside",
    "form", ".ad", ".ads", ".advertisement", ".newsletter", ".sidebar"
]


def extract_article_text(soup) -> str:
    for selector in NOISE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    article = soup.select_one("article") or soup.select_one("main") or soup.body
    paragraphs = [clean(p.get_text(" ")) for p in article.select("p, li") if clean(p.get_text(" "))]
    return "\n\n".join(paragraphs)


def scrape_blog(url: str) -> dict:
    soup = soup_from_url(url)
    title = (
        meta_content(soup, "og:title", "twitter:title")
        or first_text(soup, ["h1"])
        or clean(soup.title.string if soup.title else "")
    )
    author = (
        meta_content(soup, "author", "article:author")
        or first_text(soup, [".author", ".byline", "[rel='author']"])
    )
    published_date = meta_content(
        soup,
        "article:published_time",
        "datePublished",
        "pubdate",
        "publishdate",
        "date",
    )
    description = meta_content(soup, "description", "og:description", "twitter:description")
    content = extract_article_text(soup)
    combined_text = "\n\n".join(part for part in [title, description, content] if part)
    chunks = chunk_text(content or description)
    score = calculate_trust_score(
        source_url=url,
        source_type="blog",
        author=author,
        published_date=published_date,
        text=combined_text,
    )

    return {
        "source_url": canonical_url(url, soup),
        "source_type": "blog",
        "title": title,
        "description": description,
        "author": author or "Unknown",
        "published_date": published_date or "Unknown",
        "language": detect_language(combined_text),
        "region": "Unknown",
        "topic_tags": generate_topic_tags(combined_text),
        "trust_score": score["final_score"],
        "trust_score_breakdown": score,
        "content_chunks": chunks,
    }
