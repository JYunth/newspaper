#!/usr/bin/env python3
"""Fetch trending GitHub repositories from githubawesome.com blog.

Parses the githubawesome.com RSS feed for curated repo write-ups with
editorial blurbs explaining why each repo is notable.

Uses a state file to stagger repos across the week — each day returns a
fresh batch that hasn't been served before. When a new blog post drops,
the pool resets.

Falls back to scraping github.com/trending if the blog is unreachable.

Output: JSON array of {repo, description, blurb, link, language, stars}.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from _util import parse_feed, HEADERS


def fetch_from_blog(rss_url):
    """Parse repos and editorial blurbs from githubawesome.com blog posts.

    Returns (blog_id, items) where blog_id is the URL of the source post.
    """
    items = []
    seen = set()
    blog_id = None

    try:
        feed = parse_feed(rss_url)
        for entry in feed.entries:
            title = entry.get("title", "")

            content = ""
            if entry.get("content"):
                content = entry["content"][0].get("value", "")
            if not content:
                content = entry.get("summary", "")
            if not content:
                continue

            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            if "Trending" in title:
                # Use first trending post's link as the blog_id
                if blog_id is None:
                    blog_id = entry.get("link", title)

                # Multi-repo roundup post — split by "No.N" markers
                sections = re.split(r'(?=No\.\d+)', text)
                for section in sections[1:]:
                    lines = section.strip().split("\n")
                    blurb_lines = []
                    repo_url = ""
                    for line in lines[1:]:  # Skip "No.N"
                        if "github.com/" in line:
                            repo_url = line.strip()
                        else:
                            blurb_lines.append(line.strip())

                    match = re.search(r'github\.com/([^/\s]+/[^/\s]+)', repo_url)
                    if match:
                        repo = match.group(1).rstrip("/")
                        if repo.lower() in seen:
                            continue
                        seen.add(repo.lower())

                        blurb = " ".join(blurb_lines).strip()
                        items.append({
                            "repo": repo,
                            "description": "",
                            "blurb": blurb,
                            "link": f"https://github.com/{repo}",
                            "language": "",
                            "stars": ""
                        })
            else:
                # Single-repo blog post
                links = soup.find_all("a", href=re.compile(r'github\.com/'))
                for a in links:
                    href = a.get("href", "")
                    match = re.search(r'github\.com/([^/\s]+/[^/\s]+)', href)
                    if match:
                        repo = match.group(1).rstrip("/")
                        if repo.lower() in seen:
                            break
                        seen.add(repo.lower())

                        blurb = text.strip()
                        if len(blurb) > 500:
                            blurb = blurb[:500].rsplit(" ", 1)[0] + "..."

                        items.append({
                            "repo": repo,
                            "description": "",
                            "blurb": blurb,
                            "link": f"https://github.com/{repo}",
                            "language": "",
                            "stars": ""
                        })
                        break

            if len(items) >= 50:
                break

    except Exception:
        pass

    return blog_id, items


def fetch_from_scrape():
    """Fallback: scrape github.com/trending directly."""
    try:
        resp = requests.get("https://github.com/trending", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        for row in soup.select("article.Box-row"):
            name_el = row.select_one("h2 a")
            if not name_el:
                continue
            repo = name_el.get_text(strip=True).replace("\n", "").replace(" ", "")
            link = "https://github.com" + name_el.get("href", "")

            desc_el = row.select_one("p")
            desc = desc_el.get_text(strip=True) if desc_el else ""

            lang_el = row.select_one("[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else ""

            stars_el = row.select_one(".f6 a")
            stars = stars_el.get_text(strip=True) if stars_el else ""

            items.append({
                "repo": repo,
                "description": desc[:200],
                "blurb": "",
                "link": link,
                "language": lang,
                "stars": stars
            })

        return items
    except Exception:
        return []


def _load_state(state_file):
    """Load stagger state from disk."""
    if state_file and os.path.exists(state_file):
        try:
            with open(state_file) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_state(state_file, state):
    """Persist stagger state to disk."""
    if not state_file:
        return
    os.makedirs(os.path.dirname(state_file) or ".", exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def fetch(rss_url="https://githubawesome.com/rss/",
          fallback_url="https://rsshub.app/github/trending/daily",
          state_file=None,
          per_day=10):
    """Fetch today's batch of trending repos.

    Args:
        rss_url: githubawesome.com RSS feed
        fallback_url: backup RSS (unused currently)
        state_file: JSON file tracking which repos have been served.
                    If None, returns the full blog dump (no staggering).
        per_day: How many repos to serve per day from the pool.
    """
    blog_id, all_items = fetch_from_blog(rss_url)

    if not all_items:
        # Blog unreachable or empty — fall back to scrape
        items = fetch_from_scrape()
        return {
            "source": "github_trending",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(items),
            "pool_remaining": 0,
            "items": items
        }

    # No state file → return everything (for debugging / first run inspection)
    if not state_file:
        return {
            "source": "github_trending",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(all_items),
            "pool_remaining": 0,
            "items": all_items
        }

    # --- Stagger logic ---
    state = _load_state(state_file)

    # If blog post changed, reset the pool
    if state.get("blog_id") != blog_id:
        state = {
            "blog_id": blog_id,
            "served": [],
        }

    served = set(r.lower() for r in state.get("served", []))

    # Filter to unserved repos
    remaining = [item for item in all_items if item["repo"].lower() not in served]

    # Pick today's batch
    todays_batch = remaining[:per_day]

    # Update served list
    newly_served = [item["repo"].lower() for item in todays_batch]
    state["served"] = list(served | set(newly_served))
    state["last_served_at"] = datetime.now(timezone.utc).isoformat()
    _save_state(state_file, state)

    return {
        "source": "github_trending",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(todays_batch),
        "pool_total": len(all_items),
        "pool_remaining": len(remaining) - len(todays_batch),
        "items": todays_batch
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch GitHub trending repos")
    parser.add_argument("--rss-url", default="https://githubawesome.com/rss/")
    parser.add_argument("--fallback-url", default="https://rsshub.app/github/trending/daily")
    parser.add_argument("--state-file", help="JSON file to track served repos (enables staggering)")
    parser.add_argument("--per-day", type=int, default=10, help="Repos per day (default: 10)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(rss_url=args.rss_url, fallback_url=args.fallback_url,
                       state_file=args.state_file, per_day=args.per_day)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "github_trending", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
