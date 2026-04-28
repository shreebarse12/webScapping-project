# Short Report

## Scraping Strategy

The project uses source-specific scrapers because blogs, YouTube videos, and PubMed articles expose metadata differently. Blog pages are parsed from HTML with BeautifulSoup, using meta tags and article/main content blocks where possible. YouTube data is collected from public page metadata and oEmbed, which avoids requiring an API key. PubMed uses NCBI E-utilities XML, which is more stable than scraping the visible PubMed web page.

## Topic Tagging Method

Topic tagging uses a lightweight keyword approach. The system checks extracted text against curated topic dictionaries such as `web scraping`, `python`, `AI`, `healthcare`, `research`, `programming`, and `education`. It then fills remaining tag slots with frequent non-stopword terms from the content. This keeps the project simple, explainable, and runnable without a paid NLP API.

## Trust Score Algorithm

The trust score is a weighted score from `0` to `1`:

```text
Trust Score = f(author_credibility, citation_count, domain_authority, recency, medical_disclaimer_presence)
```

The implemented weights are:

- Author credibility: 25%
- Citation count: 15%
- Domain authority: 25%
- Recency: 20%
- Medical disclaimer presence: 15%

PubMed and official health domains receive strong domain scores. Blogs and YouTube sources are scored more conservatively unless their author or domain is recognized. Missing values receive neutral fallback values instead of breaking the pipeline.

## Edge Case Handling

Missing author, publish date, and transcript fields are marked as `Unknown`. Multiple PubMed authors are handled as a list and averaged by the scoring module. Long articles and abstracts are chunked into smaller sections for downstream processing. If a source cannot be scraped because of network or site restrictions, the pipeline still writes an output object with an error message in the trust score breakdown.

## Limitations

The project avoids paid APIs and browser automation, so YouTube transcript availability is limited. Domain authority is rule-based rather than retrieved from an SEO provider. Language detection is lightweight and optimized for this English-language dataset. A production version should add retry queues, caching, structured logging, proxy controls, transcript APIs, and stronger author verification.
