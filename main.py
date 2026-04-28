"""Run the multi-source scraping assignment pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from scraper.blog_scraper import scrape_blog
from scraper.pubmed_scraper import scrape_pubmed
from scraper.youtube_scraper import scrape_youtube


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config" / "sources.json"
OUTPUT_DIR = ROOT / "output"
OUTPUT_PATH = OUTPUT_DIR / "scraped_data.json"
SPLIT_OUTPUT_DIR = OUTPUT_DIR / "scraped_data"


def load_sources() -> dict[str, list[str]]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def scrape_many(urls: list[str], scraper: Callable[[str], dict], source_type: str) -> list[dict]:
    records = []
    for url in urls:
        print(f"Scraping {source_type}: {url}")
        try:
            records.append(scraper(url))
        except Exception as exc:
            records.append(
                {
                    "source_url": url,
                    "source_type": source_type,
                    "title": "",
                    "description": "",
                    "author": "Unknown",
                    "published_date": "Unknown",
                    "language": "unknown",
                    "region": "Unknown",
                    "topic_tags": [],
                    "trust_score": 0,
                    "trust_score_breakdown": {"error": str(exc), "final_score": 0},
                    "content_chunks": [],
                }
            )
            print(f"  Failed: {exc}")
    return records


def main() -> None:
    sources = load_sources()
    blogs = scrape_many(sources.get("blogs", []), scrape_blog, "blog")
    youtube = scrape_many(sources.get("youtube", []), scrape_youtube, "youtube")
    pubmed = scrape_many(sources.get("pubmed", []), scrape_pubmed, "pubmed")
    data = [*blogs, *youtube, *pubmed]

    OUTPUT_DIR.mkdir(exist_ok=True)
    SPLIT_OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    (SPLIT_OUTPUT_DIR / "blogs.json").write_text(json.dumps(blogs, indent=2, ensure_ascii=False), encoding="utf-8")
    (SPLIT_OUTPUT_DIR / "youtube.json").write_text(json.dumps(youtube, indent=2, ensure_ascii=False), encoding="utf-8")
    (SPLIT_OUTPUT_DIR / "pubmed.json").write_text(json.dumps(pubmed, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(data)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
