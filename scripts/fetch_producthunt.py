#!/usr/bin/env python3
"""Fetch top Product Hunt launches from RSS feed.

Output: JSON array of {name, tagline, link, date} to stdout.
Typical output size: ~500 bytes for 5 items.
"""

import json
import re
import sys
from datetime import datetime, timezone

from _util import parse_feed


def clean_html(text):
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch(url="https://www.producthunt.com/feed?category=undefined", count=5):
    feed = parse_feed(url)

    items = []
    for entry in feed.entries[:count]:
        raw_tagline = entry.get("summary", entry.get("description", ""))
        tagline = clean_html(raw_tagline)
        # PH feed includes "Discussion | Link" noise after the tagline
        if "Discussion" in tagline and "|" in tagline:
            tagline = tagline.split("Discussion")[0].strip()

        items.append({
            "name": entry.get("title", "").strip(),
            "tagline": tagline,
            "link": entry.get("link", ""),
            "date": entry.get("published", "")
        })

    return {
        "source": "producthunt",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch Product Hunt top launches")
    parser.add_argument("--url", default="https://www.producthunt.com/feed?category=undefined")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(url=args.url, count=args.count)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "producthunt", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
