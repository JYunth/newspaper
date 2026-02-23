#!/usr/bin/env python3
"""Fetch Hacker News front page stories with article body extraction.

For each story: parses the HN RSS, follows the link, extracts the article
body as clean markdown. Falls back gracefully if a link can't be read.

Output: JSON array of {title, link, hn_link, body_md, points, comments_url}.
Typical output size: ~15KB for 10 stories (vs ~500KB raw HTML).
"""

import json
import re
import sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from _util import parse_feed, HEADERS as _HEADERS


HEADERS = _HEADERS


def extract_article(url, timeout=15):
    """Extract main article text from a URL. Returns clean text or empty string."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()

        # Skip non-HTML
        ct = resp.headers.get("content-type", "")
        if "html" not in ct and "text" not in ct:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "iframe", "noscript", "form"]):
            tag.decompose()

        # Try <article> first, then <main>, then largest <div>
        article = soup.find("article")
        if not article:
            article = soup.find("main")
        if not article:
            # Fallback: find the div with the most <p> children
            divs = soup.find_all("div")
            if divs:
                article = max(divs, key=lambda d: len(d.find_all("p")))

        if not article:
            return ""

        # Extract paragraphs
        paragraphs = []
        for p in article.find_all(["p", "h1", "h2", "h3", "li"]):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Skip trivial fragments
                paragraphs.append(text)

        body = "\n\n".join(paragraphs)

        # Trim to ~2000 chars to keep context tight
        if len(body) > 2000:
            body = body[:2000].rsplit(" ", 1)[0] + "..."

        return body

    except Exception:
        return ""


def fetch(url="https://news.ycombinator.com/rss", count=10, follow_links=True):
    feed = parse_feed(url)

    entries = feed.entries[:count]

    items = []
    if follow_links:
        # Separate self-posts from external links
        external = []
        self_posts = []
        for entry in entries:
            link = entry.get("link", "")
            if "news.ycombinator.com" in link:
                self_posts.append(entry)
            else:
                external.append(entry)

        # Parallel article extraction for external links only
        extracted = {}
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(extract_article, e.get("link", "")): e
                       for e in external}
            for future in as_completed(futures):
                entry = futures[future]
                try:
                    extracted[entry.get("title", "")] = future.result()
                except Exception:
                    extracted[entry.get("title", "")] = ""

        for entry in entries:
            title = entry.get("title", "").strip()
            body = extracted.get(title, "")
            hn_id = entry.get("id", entry.get("link", ""))
            comments_url = entry.get("comments", f"https://news.ycombinator.com/item?id={hn_id}")

            items.append({
                "title": title,
                "link": entry.get("link", ""),
                "comments_url": comments_url,
                "body_md": body,
                "extractable": bool(body)
            })
    else:
        for entry in entries:
            items.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "comments_url": entry.get("comments", ""),
                "body_md": "",
                "extractable": False
            })

    return {
        "source": "hackernews",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "extractable_count": sum(1 for i in items if i["extractable"]),
        "items": items
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch Hacker News front page")
    parser.add_argument("--url", default="https://news.ycombinator.com/rss")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--no-follow", action="store_true", help="Skip article extraction")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(url=args.url, count=args.count, follow_links=not args.no_follow)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "hackernews", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
