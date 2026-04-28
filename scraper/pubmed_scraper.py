"""PubMed scraper using NCBI E-utilities XML."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests

from scoring.trust_score import calculate_trust_score
from utils.chunking import clean_text, chunk_text
from utils.tagging import detect_language, generate_topic_tags


def pmid_from_url(url_or_pmid: str) -> str:
    match = re.search(r"(\d{6,9})", url_or_pmid)
    if not match:
        raise ValueError(f"Could not find PubMed ID in {url_or_pmid}")
    return match.group(1)


def text_of(node, path: str) -> str:
    found = node.find(path)
    return clean_text("".join(found.itertext())) if found is not None else ""


def scrape_pubmed(url_or_pmid: str) -> dict:
    pmid = pmid_from_url(url_or_pmid)
    response = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "pubmed", "id": pmid, "retmode": "xml"},
        timeout=20,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    article = root.find(".//PubmedArticle")
    if article is None:
        raise ValueError(f"No PubMed article found for PMID {pmid}")

    title = text_of(article, ".//ArticleTitle")
    journal = text_of(article, ".//Journal/Title")
    year = text_of(article, ".//PubDate/Year") or text_of(article, ".//ArticleDate/Year")
    abstract_parts = [
        clean_text("".join(node.itertext()))
        for node in article.findall(".//Abstract/AbstractText")
        if clean_text("".join(node.itertext()))
    ]
    abstract = "\n\n".join(abstract_parts)
    authors = []
    for author in article.findall(".//AuthorList/Author"):
        last = text_of(author, "LastName")
        fore = text_of(author, "ForeName")
        collective = text_of(author, "CollectiveName")
        name = collective or clean_text(f"{fore} {last}")
        if name:
            authors.append(name)

    citation_count = len(article.findall(".//Reference"))
    source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    content = "\n\n".join(part for part in [title, journal, abstract] if part)
    score = calculate_trust_score(
        source_url=source_url,
        source_type="pubmed",
        author=authors,
        published_date=year,
        text=content,
        citation_count=citation_count,
    )

    return {
        "source_url": source_url,
        "source_type": "pubmed",
        "title": title,
        "description": abstract[:300],
        "author": authors,
        "published_date": year or "Unknown",
        "language": detect_language(content),
        "region": urlparse(source_url).netloc,
        "topic_tags": generate_topic_tags(content),
        "trust_score": score["final_score"],
        "trust_score_breakdown": score,
        "journal": journal,
        "citation_count": citation_count,
        "content_chunks": chunk_text(abstract or title),
    }
