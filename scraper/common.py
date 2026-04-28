"""Shared scraper helpers."""

from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def fetch(url: str, timeout: int = 20) -> requests.Response:
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    if not response.encoding or response.encoding.lower() in {"iso-8859-1", "windows-1252"}:
        response.encoding = response.apparent_encoding
    return response


def soup_from_url(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch(url).text, "html.parser")


def meta_content(soup: BeautifulSoup, *names: str) -> str:
    for name in names:
        selectors = [
            {"name": name},
            {"property": name},
            {"itemprop": name},
        ]
        for attrs in selectors:
            tag = soup.find("meta", attrs=attrs)
            if tag and tag.get("content"):
                return clean(tag["content"])
    return ""


def clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def first_text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            value = clean(node.get_text(" "))
            if value:
                return value
    return ""


def canonical_url(url: str, soup: BeautifulSoup) -> str:
    link = soup.find("link", rel=lambda value: value and "canonical" in value)
    return clean(link.get("href")) if link and link.get("href") else url
