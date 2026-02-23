# Customizing This Skill

This document is for **you, the agent** helping a user customize their newspaper.
Read this before making any changes to the skill.

## How This Skill Works (Architecture Overview)

```
config/sources.json    →  scripts/fetch_*.py  →  JSON files  →  SKILL.md (agent)  →  template.typ  →  PDF
  (what to fetch)        (mechanical work)      (clean data)    (editorial work)     (layout)
```

The entire pipeline is split into two layers:

1. **Fetcher scripts** (`scripts/`) — deterministic Python CLIs that fetch, parse, and filter raw feeds/HTML into clean JSON. No LLM reasoning happens here.
2. **SKILL.md** — instructions for the LLM agent that consumes the JSON, makes editorial decisions, fills the Typst template, and compiles the PDF.

This separation is intentional. Fetchers handle mechanical work. The agent handles editorial judgment.

## What the User Can Customize

### 1. Adding a New RSS/Atom Source

The simplest case. User says: "I want to add TechCrunch" or "Add my company blog."

**Your steps:**

1. Ask the user for the RSS/Atom feed URL.
2. Fetch the feed yourself and inspect its structure (field names, date formats, what's in `title`, `summary`, `description`, etc.).
3. Determine if an existing fetcher can handle it. Most RSS feeds are structurally identical — `fetch_producthunt.py` is essentially a generic RSS fetcher. If the new feed uses standard RSS/Atom fields, you can reuse it by just adding a new entry to `sources.json` with a `"fetcher": "generic_rss"` flag.
4. If the feed has a non-standard structure (e.g., custom namespaces, nested content, media enclosures), write a new `fetch_<name>.py` following the existing pattern (see "Writing a New Fetcher" below).
5. Add the source to `config/sources.json` under `sources`.
6. Update `scripts/fetch_all.py` to include the new source in the orchestration logic.
7. Update `SKILL.md` to include a section describing how to lay out the new source in the newspaper.
8. Update the template (`assets/template.typ`) to add a data variable and rendering section for the new source.

### 2. Adding a New HTML/Scrape Source

User says: "I want Techmeme-style scraping of lobste.rs" or "Add Indie Hackers."

**Your steps:**

1. Navigate to the URL. Inspect the HTML structure — what elements contain the headlines, links, descriptions.
2. Write a new fetcher script using `requests` + `BeautifulSoup`. Follow the `fetch_techmeme.py` pattern.
3. Test it. Make sure it produces clean JSON.
4. Wire it into `sources.json` and `fetch_all.py`.
5. Update SKILL.md and the template.

### 3. Adding a New YouTube Channel

Trivially easy — just add a new entry to the `youtube.channels` array in `sources.json`:

```json
{"name": "Channel Name", "id": "UCxxxxxxxx"}
```

No script changes needed. `fetch_youtube.py` reads the channel list from config.

**How to find the channel ID:** Go to the channel page, view source, and search for `channelId` or `externalId`. Alternatively, use `https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxx` — if it returns a valid Atom feed, the ID is correct.

### 4. Removing a Source

Set `"enabled": false` in `sources.json`. The fetcher still exists but won't run.
Or remove the entire source block from `sources.json` and delete the corresponding fetcher script.

**Don't forget:** If you remove a source entirely, also remove its data variable and rendering section from `assets/template.typ`, and its editorial instructions from `SKILL.md`.

### 5. Changing the Newspaper Appearance

The Typst template in `assets/template.typ` controls layout. Users can customize:
- Masthead image (`assets/masthead.png`)
- Fonts, colors, column layout in the template
- Section order and naming

See "Modifying the Template Layout" below for details.

### 6. Changing the Newspaper Name

Edit `config/sources.json` → `newspaper.name` and `newspaper.tagline`. Then update the masthead image in `assets/masthead.png` to match the new name.

## Writing a New Fetcher

Every fetcher follows this contract:

**Input:** Command-line args (URL, count, etc.) or reads from `sources.json`
**Output:** JSON to stdout with this shape:

```json
{
  "source": "source_name",
  "fetched_at": "ISO-8601 timestamp",
  "count": 5,
  "items": [
    {
      "title": "...",
      "link": "https://...",
      "...": "source-specific fields"
    }
  ]
}
```

**Rules:**

- **Self-contained.** Each fetcher is a standalone Python script. No shared library imports beyond stdlib + `requests`, `feedparser`, `beautifulsoup4`.
- **Always include a `link` field.** The template uses Typst's `link()` function on every item. If an item is missing its `link` field, the template will crash during compilation. This is non-negotiable.
- **Fail to stderr.** On error, write `{"source": "name", "error": "message"}` to stderr and exit 1.
- **Respect the context budget.** The whole point of these fetchers is to keep LLM context tight. A fetcher's JSON output should be 10-100x smaller than its raw input. If you're outputting more than ~20KB for a single source, you're probably including too much.
- **Trim long text.** Article bodies should be capped at ~2000 chars. Abstracts can be full-length.
- **Freshness filtering.** If the source has dates, filter out stale items. Use `--max-age` style args.
- **Parallel-safe.** Fetchers may run concurrently via `fetch_all.py`. No shared mutable state (state files use separate paths per fetcher).

**Template for a new fetcher:**

```python
#!/usr/bin/env python3
"""Fetch [description].

Output: JSON array of {field1, field2, ...} to stdout.
"""

import json
import sys
from datetime import datetime, timezone

def fetch(url, count=10):
    # ... fetch and parse ...
    return {
        "source": "my_source",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items  # each item MUST have a "link" field
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    try:
        result = fetch(args.url, args.count)
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
        else:
            print(out)
    except Exception as e:
        print(json.dumps({"source": "my_source", "error": str(e)}), file=sys.stderr)
        sys.exit(1)
```

## Updating fetch_all.py

After creating a new fetcher, add an entry to the orchestration logic in `fetch_all.py`:

```python
if sources.get("my_source", {}).get("enabled"):
    url = sources["my_source"].get("url", "https://...")
    fetchers["my_source"] = (
        [py, f"{sd}/fetch_my_source.py", "--url", url],
        f"{output_dir}/my_source.json"
    )
```

**Note on arXiv:** The arXiv source uses `"urls"` (plural, an array of strings) in `sources.json`, not `"url"` (singular). This is because it fetches from multiple subcategory feeds (cs.AI, cs.CL, cs.LG) and deduplicates results. If you're adding a source that needs multiple feed URLs, follow this pattern — pass each URL as a separate `--url` argument.

## Updating SKILL.md

Add a section in the editorial instructions describing how the new source should appear in the newspaper. Include:
- Section heading name
- Whether it goes in the **two-column body** or as a **full-width section**
- Typical word count per item
- Whether items get individual story treatments or are listed briefly
- What fields to hyperlink

## Modifying the Template Layout

The template (`assets/template.typ`) has a specific structure. Understanding it is critical before making changes.

### Layout Zones

The template has three types of zones:

1. **Full-width zones** (before and after `columns()`):
   - Masthead
   - Lead Story
   - Research Papers (after columns close)
   - XKCD (after research papers)

2. **Two-column zone** (`columns(2)` block):
   - Tech Headlines
   - Hacker News
   - Product Launches
   - Trending Repos
   - YouTube Roundup

3. **Section headers** — each section starts with `section-head("Title")` which draws a ruled line and a bold uppercase label.

### Adding a Section to the Two-Column Body

Insert your section inside the `columns(2, gutter: 14pt)[ ... ]` block. Use the existing sections as a pattern:

```typst
// ── My New Section ──
#if my-items.len() > 0 {
  section-head("My Section")
  for (i, item) in my-items.enumerate() {
    hl-small(item.title, item.link)
    v(1pt)
    text(size: 7.8pt, item.body)
    if i < my-items.len() - 1 { sep }
  }
  v(1pt)
}
```

**Section order matters.** Columns flow top-to-bottom, left-to-right. Put the most important sections first.

### Adding a Full-Width Section

Insert your section **after** `] // end columns` and **before** the XKCD section. Use the Research Papers section as a pattern:

```typst
// ─── MY FULL-WIDTH SECTION ──────────────────────────────────────────────────

#if my-items.len() > 0 {
  section-head("My Section")
  for (i, item) in my-items.enumerate() {
    hl-small(item.title, item.link)
    v(1pt)
    text(size: 7.2pt, item.body)
    if i < my-items.len() - 1 { sep }
  }
  v(1pt)
}
```

### Adding a Data Variable

At the top of the template, add a new `#let` binding with sample data:

```typst
#let my-items = (
  (title: "Sample Item", body: "Description here.", link: "https://example.com"),
)
```

**Every item must have a `link` field.** The template's rendering code uses `link(item.link)` everywhere. Missing links cause a Typst compilation error.

### Removing a Section

1. Delete the data variable (`#let my-items = ...`)
2. Delete the rendering block (the `#if my-items.len() > 0 { ... }` block)
3. Update SKILL.md to remove the editorial instructions for that section

### Changing Section Order

Move the rendering block to a different position. Within the `columns()` block, sections render in the order they appear in the source. The column layout engine fills left-to-right, top-to-bottom.

### Changing Fonts

The template sets the global font at the top:
```typst
#set text(font: "Libertinus Serif", size: 8.2pt, lang: "en")
```

GitHub repo names use Menlo:
```typst
text(font: "Menlo", item.repo)
```

**Font availability:** Libertinus Serif must be installed (`brew install --cask font-libertinus` on macOS). Menlo is pre-installed on macOS. If targeting Linux, substitute with available serif and monospace fonts.

### Changing Colors

The template uses grayscale throughout:
- Body text: default black
- Source tags: `luma(100)` (medium gray)
- Bylines: `luma(80)` (darker gray)
- Rules: `luma(120)` thin, `luma(40)` medium, `luma(0)` thick
- Links: `rgb("#111111")` (near-black, visually subtle)

To change link color to something visible (e.g., blue):
```typst
#show link: it => {
  set text(fill: rgb("#1a5276"))
  it
}
```

### Page Budget Impact

Adding content pushes the page count up. The newspaper targets 3 pages on A4. When adding sections:
- A new two-column section with 5 items at ~80 words each adds roughly half a column
- A new full-width section with 5 items at ~80 words each adds roughly half a page
- Full arXiv abstracts (untruncated) take significant space — typically 1/3 to 1/2 of a full-width page for 5 papers

If the newspaper exceeds 3 pages after adding content, trim existing sections (see SKILL.md "Page Budget" for priorities).

## State Management for New Sources

If your new source needs to track what has been served (to avoid repeating content across days), follow the GitHub trending pattern:

1. Accept a `--state-file` argument in the fetcher
2. Load/save a JSON dict with tracking info
3. In `fetch_all.py`, create the state file path: `state = f"{output_dir}/.my_source_state.json"`
4. Pass it to the fetcher: `["--state-file", state]`

State files are dotfiles (hidden) in the output directory. They persist across runs.

If your source doesn't need statefulness (most RSS feeds don't — they naturally show fresh content), skip this.

## Asset Management

### Masthead
- Lives at `assets/masthead.png`
- Referenced in the template as `image("masthead.png", width: 48%)`
- To change: replace the PNG file. Keep the width reasonable (40-60% of page width)

### XKCD Comic
- `fetch_xkcd.py` downloads the comic PNG to `assets/xkcd_latest.png` (via `--assets-dir`)
- It also saves an archive copy as `xkcd-{num}.png` in the output directory
- The template references `"xkcd_latest.png"` — a stable filename that gets overwritten each run
- If the XKCD fetcher reports `"new": false` (comic already seen), the PNG from the previous run is still valid

### Adding New Image Assets
- Place all images in `assets/`
- Reference them by filename only (no path prefix) in the template, since the .typ file is compiled from the same directory
- If images are generated by a fetcher (like XKCD), have the fetcher write to `assets/` using an `--assets-dir` argument

## Testing

After any change, run the full pipeline:
```bash
cd newspaper
source .venv/bin/activate
python scripts/fetch_all.py --config config/sources.json --output-dir /tmp/test-fetch
```

Check each JSON file in the output directory. Verify:
- Item counts match expectations
- Every item has a `link` field
- Text fields aren't empty or truncated unexpectedly
- Output file sizes are reasonable (< 20KB per source)

Then do a test compile:
```bash
cp assets/template.typ assets/test-newspaper.typ
# (fill in test data)
typst compile assets/test-newspaper.typ /tmp/test-output.pdf
rm assets/test-newspaper.typ
```

**Common compilation pitfalls:**
- Missing `link` field on any item → Typst error about accessing non-existent dictionary key
- .typ file outside `assets/` → "file not found" for masthead.png or xkcd_latest.png
- PNG output without `{p}` placeholder → "cannot export multiple images" error
- Missing font → silent fallback to default font (no error, just different appearance)

## Config Reference: sources.json

Key fields in `sources.json` that affect fetcher behavior:

| Source | Key Fields | Notes |
|--------|-----------|-------|
| `techmeme` | `url`, `count` | Single URL, scrapes HTML |
| `hackernews` | `url`, `count`, `extractable_only` | RSS feed, optionally extracts article bodies |
| `producthunt` | `url`, `count` | RSS feed |
| `arxiv` | `urls` (array!), `count` | **Plural `urls`** — multiple subcategory feeds. Each URL is passed as a separate `--url` arg. Fetcher deduplicates. |
| `github_trending` | `url`, `per_day` | `per_day` controls staggering (default 10 repos/day) |
| `youtube` | `channels` (array), `max_age_hours` | Each channel: `{"name": "...", "id": "UC..."}` |
| `xkcd` | `url`, `max_age_hours` | Atom feed URL. `max_age_hours` controls freshness (default 48) |
