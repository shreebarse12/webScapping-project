"""YouTube metadata scraper using public page data and oEmbed."""

from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, urlparse

import requests

from scraper.common import HEADERS, clean, fetch, meta_content
from scoring.trust_score import calculate_trust_score
from utils.chunking import chunk_text
from utils.tagging import detect_language, generate_topic_tags


def video_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.strip("/")
    return parse_qs(parsed.query).get("v", [""])[0]


def get_oembed(url: str) -> dict:
    endpoint = "https://www.youtube.com/oembed"
    response = requests.get(endpoint, params={"url": url, "format": "json"}, headers=HEADERS, timeout=20)
    if response.ok:
        return response.json()
    return {}


def extract_player_json(html: str) -> dict:
    match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});", html)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def scrape_youtube(url: str) -> dict:
    html = fetch(url).text
    player = extract_player_json(html)
    oembed = get_oembed(url)
    video = player.get("videoDetails", {})
    microformat = player.get("microformat", {}).get("playerMicroformatRenderer", {})

    title = video.get("title") or oembed.get("title", "")
    author = video.get("author") or oembed.get("author_name", "")
    published_date = microformat.get("publishDate") or microformat.get("uploadDate") or "Unknown"
    description = video.get("shortDescription") or microformat.get("description", {}).get("simpleText", "")
    transcript = ""
    content = "\n\n".join(part for part in [title, description, transcript] if part)
    chunks = chunk_text(transcript or description or title)
    score = calculate_trust_score(
        source_url=url,
        source_type="youtube",
        author=author,
        published_date=published_date,
        text=content,
    )

    return {
        "source_url": url,
        "source_type": "youtube",
        "title": clean(title),
        "description": clean(description),
        "author": clean(author) or "Unknown",
        "published_date": published_date,
        "language": detect_language(content),
        "region": microformat.get("availableCountries", ["Unknown"])[0],
        "topic_tags": generate_topic_tags(content),
        "trust_score": score["final_score"],
        "trust_score_breakdown": score,
        "content_chunks": chunks,
    }
