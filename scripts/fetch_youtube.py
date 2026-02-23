#!/usr/bin/env python3
"""Fetch new YouTube videos from configured channels and optionally transcripts.

Two modes:
  --channels-file / --channels: Check channels for new videos (<max_age_hours)
  --transcript URL:             Get transcript for a single video

Channel check output: JSON {channels: [{name, videos: [{title, link, published}]}]}
Transcript output:    JSON {video_url, title, transcript_text}

Typical output: ~2KB manifest, ~5-15KB per transcript.
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from time import mktime
from concurrent.futures import ThreadPoolExecutor, as_completed

from _util import parse_feed


YT_FEED_BASE = "https://www.youtube.com/feeds/videos.xml?channel_id="


def _check_one_channel(ch, cutoff):
    """Check a single channel for new videos. Called in parallel."""
    name = ch["name"]
    cid = ch["id"]
    feed_url = YT_FEED_BASE + cid

    try:
        feed = parse_feed(feed_url)
        new_videos = []

        for entry in feed.entries:
            pub = entry.get("published_parsed") or entry.get("updated_parsed")
            if not pub:
                continue

            pub_dt = datetime.fromtimestamp(mktime(pub), tz=timezone.utc)

            if pub_dt >= cutoff:
                video_id = entry.get("yt_videoid", "")
                link = entry.get("link", "")
                if not link and video_id:
                    link = f"https://www.youtube.com/watch?v={video_id}"

                new_videos.append({
                    "title": entry.get("title", "").strip(),
                    "link": link,
                    "video_id": video_id,
                    "published": pub_dt.isoformat(),
                })

        if new_videos:
            return {"channel": name, "channel_id": cid,
                    "new_video_count": len(new_videos), "videos": new_videos}
        return None

    except Exception as e:
        return {"channel": name, "channel_id": cid,
                "error": str(e), "videos": []}


def check_channels(channels, max_age_hours=24):
    """Check all channels for videos newer than max_age_hours (parallel)."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max_age_hours)
    results = []

    with ThreadPoolExecutor(max_workers=min(len(channels), 8)) as pool:
        futures = {pool.submit(_check_one_channel, ch, cutoff): ch for ch in channels}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

    # Sort by channel name for stable output
    results.sort(key=lambda r: r["channel"])

    total = sum(len(r.get("videos", [])) for r in results)
    return {
        "source": "youtube",
        "fetched_at": now.isoformat(),
        "total_new_videos": total,
        "channels_with_new": len([r for r in results if r.get("videos")]),
        "channels": results
    }


def fetch_transcript(video_url):
    """Fetch full transcript for a single video."""
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
    if not match:
        raise ValueError(f"Could not extract video ID from: {video_url}")

    video_id = match.group(1)

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        text = " ".join(snippet.text for snippet in transcript.snippets)
        text = re.sub(r'\s+', ' ', text).strip()
    except ImportError:
        # Fallback: try yt-dlp subtitle extraction
        import subprocess
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "subs")
            subprocess.run(
                ["yt-dlp", "--write-auto-sub", "--sub-lang", "en",
                 "--skip-download", "--sub-format", "vtt",
                 "-o", out_path, video_url],
                capture_output=True, text=True, timeout=30
            )

            vtt_file = None
            for f in os.listdir(tmpdir):
                if f.endswith(".vtt"):
                    vtt_file = os.path.join(tmpdir, f)
                    break

            if not vtt_file:
                raise RuntimeError("No transcript available (tried youtube-transcript-api and yt-dlp)")

            with open(vtt_file) as f:
                raw = f.read()

            lines = []
            for line in raw.split("\n"):
                line = line.strip()
                if not line or line.startswith("WEBVTT") or "-->" in line:
                    continue
                if re.match(r'^\d+$', line):
                    continue
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    lines.append(line)

            deduped = []
            for line in lines:
                if not deduped or line != deduped[-1]:
                    deduped.append(line)

            text = " ".join(deduped)
            text = re.sub(r'\s+', ' ', text).strip()

    return {
        "source": "youtube_transcript",
        "video_url": video_url,
        "video_id": video_id,
        "transcript_length": len(text),
        "transcript": text
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch YouTube channel updates and transcripts")
    sub = parser.add_subparsers(dest="command", required=True)

    # Subcommand: channels
    ch_parser = sub.add_parser("channels", help="Check channels for new videos")
    ch_parser.add_argument("--config", required=True, help="Path to sources.json")
    ch_parser.add_argument("--max-age", type=int, default=24, help="Max video age in hours")
    ch_parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    # Subcommand: transcript
    tr_parser = sub.add_parser("transcript", help="Get transcript for a video")
    tr_parser.add_argument("url", help="YouTube video URL")
    tr_parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    args = parser.parse_args()

    try:
        if args.command == "channels":
            with open(args.config) as f:
                config = json.load(f)
            channels = config.get("sources", {}).get("youtube", {}).get("channels", [])
            max_age = args.max_age or config.get("sources", {}).get("youtube", {}).get("max_age_hours", 24)
            result = check_channels(channels, max_age_hours=max_age)
        elif args.command == "transcript":
            result = fetch_transcript(args.url)

        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)

    except Exception as e:
        print(json.dumps({"source": "youtube", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
