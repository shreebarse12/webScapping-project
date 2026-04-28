# Data Scraping and Trust Scoring Assignment

This project implements a multi-source scraper and trust scoring system for:

- 3 blog posts
- 2 YouTube videos
- 1 PubMed article

The generated dataset is written to `output/scraped_data.json` with one object per source. Split files are also written to `output/scraped_data/blogs.json`, `output/scraped_data/youtube.json`, and `output/scraped_data/pubmed.json`.

## Project Structure

```text
scraper/
  blog_scraper.py
  youtube_scraper.py
  pubmed_scraper.py
scoring/
  trust_score.py
utils/
  tagging.py
  chunking.py
config/
  sources.json
output/
  scraped_data.json
main.py
```

## Tools and Libraries

- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- Python `xml.etree.ElementTree` for PubMed XML
- `python-dateutil` for flexible date parsing
- Custom keyword logic for language detection and topic tagging

## Scraping Approach

Blogs are fetched as HTML pages. The scraper extracts title, description, author, publish date, and article paragraphs while removing common noise such as navigation, ads, headers, footers, sidebars, scripts, and forms.

YouTube records are collected from public page metadata and the public oEmbed endpoint. The scraper extracts channel name, title, publish date when available, description, and text chunks from the description. Transcript extraction is treated as optional because public transcripts are not always available without extra libraries or API access.

PubMed data is collected through the official NCBI E-utilities XML endpoint. The scraper extracts article title, authors, journal, abstract, publication year, and reference count.

## Trust Score Design

The trust score ranges from `0` to `1` and uses this weighted formula:

```text
trust_score =
  author_credibility * 0.25
  + citation_count * 0.15
  + domain_authority * 0.25
  + recency * 0.20
  + medical_disclaimer_presence * 0.15
```

Rules:

- Known institutions and reputable publishers receive higher author/domain scores.
- PubMed, NIH, and other official health domains receive high domain authority.
- Recent content receives a higher recency score.
- Medical content without a disclaimer is penalized unless it is a PubMed source.
- Missing metadata receives neutral or conservative fallback scores rather than crashing the pipeline.

## Edge Cases

- Missing author/date/transcript values are stored as `Unknown`.
- Multiple PubMed authors are averaged for author credibility.
- Long content is split into chunks of approximately 120 words.
- Non-English content is marked as `unknown` by the lightweight language detector.
- Failed sources are still represented in output with an error in `trust_score_breakdown`.

## Abuse Prevention

- Fake or unknown authors receive conservative credibility scores.
- Low or unknown domains are capped near neutral authority.
- SEO-heavy blogs do not receive high trust from keywords alone.
- Medical claims without a disclaimer are penalized.
- Older content receives recency penalties, which helps reduce the ranking of outdated information.

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python main.py
```

The final JSON dataset will be available at:

```text
output/scraped_data.json
```
