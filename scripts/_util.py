"""Shared utilities for fetcher scripts."""

import feedparser
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}


def parse_feed(url, timeout=30):
    """Fetch RSS/Atom feed using requests (proxy-aware), parse with feedparser.

    feedparser.parse(url) uses urllib internally which doesn't respect
    system proxy settings in some environments. This function decouples
    HTTP fetching from XML parsing for reliability.
    """
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Failed to parse feed from {url}: {feed.bozo_exception}")
    return feed
