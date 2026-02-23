#!/usr/bin/env python3
"""Orchestrator: run all enabled fetchers and write results to an output directory.

Usage:
    python fetch_all.py --config ../config/sources.json --output-dir ./today/

This runs each enabled fetcher, writing individual JSON files to output-dir:
    today/techmeme.json
    today/producthunt.json
    today/hackernews.json
    today/arxiv.json
    today/github_trending.json
    today/youtube.json
    today/xkcd.json
    today/xkcd-NNNN.png  (if new comic found)
    today/manifest.json   (summary of all fetches)

Each fetcher runs as a subprocess so failures are isolated.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent


def run_fetcher(name, cmd, output_file):
    """Run a single fetcher subprocess. Returns (name, success, path_or_error)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            return (name, False, result.stderr.strip())

        with open(output_file, "w") as f:
            f.write(result.stdout)

        # Parse to get item count
        try:
            data = json.loads(result.stdout)
            count = data.get("count",
                          data.get("total_new_videos",
                          "new" if data.get("new") else "?"))
        except Exception:
            count = "?"

        return (name, True, f"{count} items → {output_file}")

    except subprocess.TimeoutExpired:
        return (name, False, "TIMEOUT (120s)")
    except Exception as e:
        return (name, False, str(e))


def fetch_all(config_path, output_dir):
    config_path = os.path.abspath(config_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with open(config_path) as f:
        config = json.load(f)

    sources = config.get("sources", {})
    py = sys.executable
    sd = str(SCRIPT_DIR)

    # Build fetcher commands for enabled sources
    fetchers = {}

    if sources.get("techmeme", {}).get("enabled"):
        url = sources["techmeme"].get("url", "https://www.techmeme.com/")
        fetchers["techmeme"] = (
            [py, f"{sd}/fetch_techmeme.py", "--url", url],
            f"{output_dir}/techmeme.json"
        )

    if sources.get("producthunt", {}).get("enabled"):
        url = sources["producthunt"].get("url", "https://www.producthunt.com/feed?category=undefined")
        count = str(sources["producthunt"].get("count", 5))
        fetchers["producthunt"] = (
            [py, f"{sd}/fetch_producthunt.py", "--url", url, "--count", count],
            f"{output_dir}/producthunt.json"
        )

    if sources.get("hackernews", {}).get("enabled"):
        url = sources["hackernews"].get("url", "https://news.ycombinator.com/rss")
        count = str(sources["hackernews"].get("count", 10))
        cmd = [py, f"{sd}/fetch_hackernews.py", "--url", url, "--count", count]
        if not sources["hackernews"].get("follow_links", True):
            cmd.append("--no-follow")
        fetchers["hackernews"] = (cmd, f"{output_dir}/hackernews.json")

    if sources.get("arxiv", {}).get("enabled"):
        arxiv_cfg = sources["arxiv"]
        cmd = [py, f"{sd}/fetch_arxiv.py"]
        # Support both "urls" (list) and legacy "url" (single string)
        urls = arxiv_cfg.get("urls", [])
        if not urls:
            legacy = arxiv_cfg.get("url")
            if legacy:
                urls = [legacy]
        for u in urls:
            cmd += ["--url", u]
        c = arxiv_cfg.get("count")
        if c:
            cmd += ["--count", str(c)]
        fetchers["arxiv"] = (cmd, f"{output_dir}/arxiv.json")

    if sources.get("github_trending", {}).get("enabled"):
        rss = sources["github_trending"].get("url", "https://githubawesome.com/rss/")
        fb = sources["github_trending"].get("fallback_url", "https://rsshub.app/github/trending/daily")
        per_day = str(sources["github_trending"].get("per_day", 10))
        state = f"{output_dir}/.github_trending_state.json"
        fetchers["github_trending"] = (
            [py, f"{sd}/fetch_github_trending.py", "--rss-url", rss, "--fallback-url", fb,
             "--state-file", state, "--per-day", per_day],
            f"{output_dir}/github_trending.json"
        )

    if sources.get("youtube", {}).get("enabled"):
        fetchers["youtube"] = (
            [py, f"{sd}/fetch_youtube.py", "channels", "--config", config_path],
            f"{output_dir}/youtube.json"
        )

    if sources.get("xkcd", {}).get("enabled"):
        url = sources["xkcd"].get("url", "https://www.xkcd.com/atom.xml")
        state = f"{output_dir}/.xkcd_state.json"
        assets = str(SCRIPT_DIR.parent / "assets")
        fetchers["xkcd"] = (
            [py, f"{sd}/fetch_xkcd.py", "--url", url,
             "--output-dir", output_dir, "--assets-dir", assets,
             "--state-file", state],
            f"{output_dir}/xkcd.json"
        )

    # Run all fetchers in parallel
    results = {}
    print(f"Fetching {len(fetchers)} sources...", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=len(fetchers)) as pool:
        futures = {}
        for name, (cmd, out_file) in fetchers.items():
            futures[pool.submit(run_fetcher, name, cmd, out_file)] = name

        for future in as_completed(futures):
            name, success, detail = future.result()
            status = "ok" if success else "FAILED"
            print(f"  [{status}] {name}: {detail}", file=sys.stderr)
            results[name] = {"success": success, "detail": detail}

    # Write manifest
    manifest = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "config": config_path,
        "output_dir": output_dir,
        "results": results
    }
    manifest_path = f"{output_dir}/manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest: {manifest_path}", file=sys.stderr)

    successes = sum(1 for r in results.values() if r["success"])
    failures = len(results) - successes
    print(f"Done: {successes} succeeded, {failures} failed", file=sys.stderr)

    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run all configured fetchers")
    parser.add_argument("--config", required=True, help="Path to sources.json")
    parser.add_argument("--output-dir", required=True, help="Output directory for fetched data")
    args = parser.parse_args()

    manifest = fetch_all(args.config, args.output_dir)
    print(json.dumps(manifest, indent=2))
