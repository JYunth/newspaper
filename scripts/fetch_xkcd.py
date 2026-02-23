#!/usr/bin/env python3
"""Fetch the latest XKCD comic if it's new.

Checks the Atom feed, compares against last-seen state, and downloads
the comic PNG if fresh. Outputs metadata + local path to the image.

Output: JSON {new: bool, title, alt_text, img_url, img_path, comic_num}.
Typical output size: ~200 bytes + PNG file on disk.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

import requests

from _util import parse_feed


def fetch(feed_url="https://www.xkcd.com/atom.xml",
          output_dir=".",
          assets_dir=None,
          state_file=None,
          max_age_hours=48):
    """Check for new XKCD comic.

    Args:
        feed_url: XKCD Atom feed
        output_dir: Where to save the comic PNG
        assets_dir: If set, also copy the comic to this directory as
                    ``xkcd_latest.<ext>`` and return a template-relative
                    ``img_path`` (just the filename) so the Typst template
                    in the same directory can embed it with ``image()``.
        state_file: Optional file tracking last-seen comic number
        max_age_hours: Consider comics newer than this as "new"
    """
    feed = parse_feed(feed_url)

    if not feed.entries:
        return {"source": "xkcd", "new": False, "reason": "empty_feed"}

    entry = feed.entries[0]  # Most recent

    # Parse update time
    updated = entry.get("updated_parsed") or entry.get("published_parsed")
    if updated:
        from time import mktime
        entry_dt = datetime.fromtimestamp(mktime(updated), tz=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        is_fresh = entry_dt >= cutoff
    else:
        is_fresh = True  # Can't tell, assume fresh

    # Check state file for duplicate prevention
    last_seen = None
    if state_file and os.path.exists(state_file):
        try:
            with open(state_file) as f:
                last_seen = json.load(f).get("comic_num")
        except Exception:
            pass

    title = entry.get("title", "").strip()

    # Extract comic number from link
    link = entry.get("link", "")
    comic_num_match = re.search(r'/(\d+)/?', link)
    comic_num = int(comic_num_match.group(1)) if comic_num_match else None

    if last_seen and comic_num and comic_num <= last_seen:
        return {
            "source": "xkcd",
            "new": False,
            "reason": "already_seen",
            "comic_num": comic_num,
            "title": title
        }

    if not is_fresh:
        return {
            "source": "xkcd",
            "new": False,
            "reason": "stale",
            "comic_num": comic_num,
            "title": title
        }

    # Get comic image URL from the XKCD JSON API
    img_url = ""
    alt_text = ""
    if comic_num:
        try:
            api_resp = requests.get(f"https://xkcd.com/{comic_num}/info.0.json", timeout=10)
            api_resp.raise_for_status()
            data = api_resp.json()
            img_url = data.get("img", "")
            alt_text = data.get("alt", "")
            title = data.get("safe_title", title)
        except Exception:
            # Fallback: parse from feed entry summary
            summary = entry.get("summary", "")
            img_match = re.search(r'src="([^"]+)"', summary)
            if img_match:
                img_url = img_match.group(1)
            alt_match = re.search(r'alt="([^"]*)"', summary)
            if alt_match:
                alt_text = alt_match.group(1)

    # Download the image
    img_path = ""
    if img_url:
        try:
            ext = os.path.splitext(img_url.split("?")[0])[1] or ".png"
            filename = f"xkcd-{comic_num}{ext}" if comic_num else f"xkcd-latest{ext}"
            save_path = os.path.join(output_dir, filename)
            os.makedirs(output_dir, exist_ok=True)
            resp = requests.get(img_url, timeout=15)
            resp.raise_for_status()
            img_bytes = resp.content

            # Save to output_dir (primary copy)
            with open(save_path, "wb") as f:
                f.write(img_bytes)

            # Also copy to assets_dir so the Typst template can find it.
            # The template references images relative to its own directory.
            if assets_dir:
                os.makedirs(assets_dir, exist_ok=True)
                assets_filename = f"xkcd_latest{ext}"
                assets_path = os.path.join(assets_dir, assets_filename)
                with open(assets_path, "wb") as f:
                    f.write(img_bytes)
                # Return just the filename — Typst resolves relative to template dir
                img_path = assets_filename
            else:
                # No assets dir: return the absolute path so callers can locate it
                img_path = os.path.abspath(save_path)
        except Exception as e:
            img_path = ""
            print(f"[xkcd] image download failed: {e}", file=sys.stderr)

    # Update state
    if state_file and comic_num:
        os.makedirs(os.path.dirname(state_file) or ".", exist_ok=True)
        with open(state_file, "w") as f:
            json.dump({"comic_num": comic_num, "fetched_at": datetime.now(timezone.utc).isoformat()}, f)

    return {
        "source": "xkcd",
        "new": True,
        "comic_num": comic_num,
        "title": title,
        "alt_text": alt_text,
        "img_url": img_url,
        "img_path": img_path,
        "link": link
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch latest XKCD comic")
    parser.add_argument("--url", default="https://www.xkcd.com/atom.xml")
    parser.add_argument("--output-dir", default=".", help="Dir to save comic PNG")
    parser.add_argument("--assets-dir", default=None,
                        help="Dir where the Typst template lives; image is copied here as xkcd_latest.png")
    parser.add_argument("--state-file", help="Track last-seen comic number")
    parser.add_argument("--max-age", type=int, default=48, help="Max comic age in hours")
    parser.add_argument("--output", "-o", help="JSON output file (default: stdout)")
    args = parser.parse_args()

    try:
        result = fetch(
            feed_url=args.url,
            output_dir=args.output_dir,
            assets_dir=args.assets_dir,
            state_file=args.state_file,
            max_age_hours=args.max_age
        )
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "xkcd", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
