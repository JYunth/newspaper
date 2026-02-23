#!/usr/bin/env python3
"""Fetch top tech headlines from Techmeme.

Output: JSON array of {headline, link, source, blurb} to stdout.
Typical output size: ~2KB (vs ~100KB raw HTML).
"""

import json
import sys
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def fetch(url="https://www.techmeme.com/", max_items=20):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    seen_headlines = set()

    # Techmeme uses .clus divs for story clusters
    for cluster in soup.select(".clus"):
        # Headline link has class "ourh"
        headline_el = cluster.select_one("a.ourh")
        if not headline_el:
            continue

        headline = headline_el.get_text(strip=True)
        if not headline or headline in seen_headlines:
            continue
        seen_headlines.add(headline)

        link = headline_el.get("href", "")

        # Source attribution from <cite> tag
        source_el = cluster.select_one("cite")
        source = source_el.get_text(strip=True).rstrip(":") if source_el else ""

        # Blurb from the .ii div text after the em dash
        blurb = ""
        ii_el = cluster.select_one(".ii")
        if ii_el:
            text = ii_el.get_text(strip=True)
            if "\u2014" in text:
                blurb = text.split("\u2014", 1)[1].strip()[:300]
            blurb = re.sub(r'\s+', ' ', blurb).strip()

        items.append({
            "headline": headline,
            "link": link,
            "source": source,
            "blurb": blurb
        })

        if len(items) >= max_items:
            break

    return {
        "source": "techmeme",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch Techmeme headlines")
    parser.add_argument("--url", default="https://www.techmeme.com/")
    parser.add_argument("--max", type=int, default=20)
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(url=args.url, max_items=args.max)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "techmeme", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
