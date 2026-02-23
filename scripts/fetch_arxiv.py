#!/usr/bin/env python3
"""Fetch latest AI/ML/NLP papers from arXiv RSS feeds.

Supports fetching from multiple arXiv subcategory feeds (e.g. cs.AI, cs.CL,
cs.LG) and merging results with deduplication.

Outputs ALL recent papers with title + full abstract so the LLM agent
can pick the most relevant ones based on user interests.

Output: JSON array of {title, abstract, link, authors, categories}.
"""

import json
import re
import sys
from datetime import datetime, timezone

from _util import parse_feed

# Default feeds: AI, Computation & Language (NLP), Machine Learning
DEFAULT_URLS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/cs.CL",
    "https://rss.arxiv.org/rss/cs.LG",
]


def clean_text(text):
    """Strip HTML tags, arXiv boilerplate, and normalize whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    # Strip arXiv boilerplate prefix: "arXiv:XXXX Announce Type: ... Abstract: "
    text = re.sub(r'^arXiv:\S+\s+Announce Type:\s*\w+\s*Abstract:\s*', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch(urls=None, count=None):
    if urls is None:
        urls = DEFAULT_URLS

    # Normalize: accept a single URL string or a list
    if isinstance(urls, str):
        urls = [urls]

    seen_links = set()
    items = []

    for url in urls:
        try:
            feed = parse_feed(url)
        except Exception as e:
            print(f"Warning: failed to fetch {url}: {e}", file=sys.stderr)
            continue

        for entry in feed.entries:
            link = entry.get("link", "")

            # Deduplicate papers that appear in multiple subcategory feeds
            if link in seen_links:
                continue
            seen_links.add(link)

            title = clean_text(entry.get("title", ""))

            # arXiv RSS puts abstract in description/summary — keep full text
            abstract = clean_text(
                entry.get("summary", entry.get("description", ""))
            )

            # Extract authors
            authors = ""
            if "author" in entry:
                authors = entry["author"]
            elif "authors" in entry:
                authors = ", ".join(a.get("name", "") for a in entry["authors"])

            # Extract arXiv categories from tags
            categories = []
            for tag in entry.get("tags", []):
                term = tag.get("term", "")
                if term:
                    categories.append(term)

            items.append({
                "title": title,
                "abstract": abstract,
                "link": link,
                "authors": authors,
                "categories": categories,
            })

    # Apply count limit after merging all feeds
    if count:
        items = items[:count]

    return {
        "source": "arxiv",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "feed_urls": urls,
        "count": len(items),
        "items": items,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch arXiv AI/ML/NLP papers from subcategory feeds"
    )
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="arXiv RSS feed URL (can be repeated for multiple feeds). "
             "Defaults to cs.AI, cs.CL, cs.LG.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Max papers after merging (default: all, agent filters by interest)",
    )
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(urls=args.urls, count=args.count)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "arxiv", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
