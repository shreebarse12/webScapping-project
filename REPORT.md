# Short Report: Multi-Source Scraping and Trust Scoring

## Scraping Strategy

This project uses a source-specific scraping strategy because blogs, YouTube videos, and PubMed articles expose their content in different formats. Blog posts are scraped from HTML pages using `requests` and `BeautifulSoup`. The scraper reads common metadata fields such as title, description, author, and publish date from meta tags, then extracts article text mainly from `article`, `main`, paragraph, and list elements. Common non-content sections such as navigation bars, headers, footers, ads, sidebars, scripts, and forms are removed before chunking the article text.

YouTube videos are handled separately because their content is not structured like a normal blog page. The YouTube scraper collects public page metadata and oEmbed data, including video title, channel name, publish date when available, and video description. Transcript extraction is treated as optional because transcripts may be unavailable or restricted without an additional library or API.

PubMed is scraped through the official NCBI E-utilities XML endpoint instead of scraping the visual web page. This is more reliable for academic metadata. The PubMed scraper extracts article title, authors, journal name, abstract, publication year, and reference count where available. All scraped records are stored in a common JSON schema so that different source types can be processed consistently.

## Topic Tagging Method

Topic tagging is implemented with a lightweight keyword-based method. The extracted title, description, abstract, and content are combined into one text field. The tagging module checks this text against predefined topic keyword groups such as `web scraping`, `python`, `AI`, `healthcare`, `research`, `programming`, and `education`.

After matching known topic groups, the system also counts frequent meaningful words from the content and adds the most relevant terms as extra tags. Common stop words such as “the,” “and,” “with,” and “from” are ignored. This approach is simple, explainable, and does not require paid NLP APIs or large machine learning models. It is suitable for an assignment-level project where the goal is to automatically generate useful topic labels from scraped content.

## Trust Score Algorithm

The trust score estimates the reliability of each source on a scale from `0` to `1`. The implemented formula is:

```text
Trust Score =
  author_credibility * 0.25
  + citation_count * 0.15
  + domain_authority * 0.25
  + recency * 0.20
  + medical_disclaimer_presence * 0.15
```

Author credibility is based on whether the author, organization, or channel is known and reliable. For example, PubMed/NIH-style sources and established educational publishers receive stronger scores, while unknown authors receive conservative fallback values. Citation count is mainly useful for PubMed articles, where references can indicate academic grounding. Domain authority is rule-based and gives higher scores to trusted domains such as PubMed, NIH, and established educational websites. Recency rewards newer content and penalizes outdated information. Medical disclaimer presence is important for health-related content, because medical claims without proper disclaimers can be risky or misleading.

The final score is rounded to three decimal places and stored along with a detailed score breakdown. This makes the scoring system transparent and easy to explain.

## Edge Case Handling

The system handles missing metadata by storing unknown values instead of stopping the scraping pipeline. If an author, publish date, transcript, or region is not available, the field is marked as `Unknown`. The trust score module also uses neutral or conservative fallback scores for missing values, so incomplete metadata does not crash the program.

Multiple authors are supported, especially for PubMed articles. When several authors are present, their credibility scores are averaged. Long articles and abstracts are split into smaller chunks of about 120 words, which makes the content easier to process later for search, summarization, or analysis.

The project also includes basic abuse prevention logic. Unknown authors are not given high credibility automatically. Low-authority or unknown domains are scored conservatively. Medical content without a disclaimer is penalized unless it comes from a trusted academic source such as PubMed. Older content receives a recency penalty to reduce the risk of relying on outdated information.

If a website blocks scraping, returns an error, or changes its structure, the pipeline records the failed source with an error message instead of breaking the whole run. This makes the scraper more robust and ensures that one failed source does not prevent the remaining sources from being processed.
