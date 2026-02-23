// Vallie's Daily — Broadsheet Newspaper Template
// A4, two-column broadsheet with per-page column flow

// ─── CONFIG (filled by agent) ───────────────────────────────────────────────

#let edition-date = "Sunday, February 23, 2026"
#let edition-number = "No. 1"
#let tagline = "Your personalized tech briefing"

#let techmeme-items = (
  (headline: "OpenAI Scrambles for Compute as Stargate Stalls Amid SoftBank Clash", source: "The Information", blurb: "The $500 billion Stargate data center project — once the crown jewel of OpenAI's infrastructure ambitions — has hit serious turbulence. Disagreements between SoftBank and OpenAI over funding timelines and equity splits have left construction of the first Texas facility effectively frozen, according to three people familiar with the matter. When President Trump announced Stargate in January 2025, it was supposed to signal a new era of American AI dominance. Instead, the project has become a cautionary tale about the gap between political theater and engineering reality. OpenAI is now scrambling to secure interim compute capacity from cloud providers including Microsoft Azure and Oracle, paying premium spot-pricing to maintain its training schedules. The delay threatens the company's roadmap for GPT-5 and its planned reasoning models, which require cluster sizes that simply don't exist on the open market. Internally, engineers have been told to optimize for smaller training runs while leadership negotiates. Sources say OpenAI building its own data centers is not its near-term priority — the company would rather lease capacity than become a real estate developer. SoftBank, which committed $100 billion in the first tranche, is said to be seeking board seats and veto rights that OpenAI's nonprofit governance structure was never designed to accommodate.", link: "https://www.theinformation.com/articles/inside-openais-scramble-get-computing-power-stargate-stalled"),
  (headline: "AI Adoption Faces More Resistance Than Expected, Altman and Huang Warn", source: "New York Times", blurb: "In recent interviews, OpenAI CEO Sam Altman acknowledged that artificial intelligence adoption faces more public resistance than he anticipated, while Nvidia's Jensen Huang warned the 'doomer narrative' may be winning hearts and minds. Tech leaders are beginning to worry about the public's underwhelming enthusiasm for their plans to remake the world with AI. Enterprise adoption has been strong, but consumer engagement has plateaued. Altman's candid remarks signal a growing awareness in the Valley that the AI revolution may unfold more slowly than investors have priced in, with several major AI startups quietly revising their revenue projections downward.", link: "https://www.nytimes.com/2026/02/21/technology/ai-boom-backlash.html"),
  (headline: "Samsung Plans to Add Perplexity to Galaxy AI for S26 Series", source: "Engadget", blurb: "Samsung's upcoming Galaxy S26 flagship devices will ship with Perplexity AI deeply integrated into its Galaxy AI suite, marking the company's most significant departure from its longstanding Google partnership. Users can launch the Perplexity agent by saying 'Hey Plex' or pressing a dedicated physical button. The deal gives Perplexity access to Samsung's on-device neural processing unit, enabling faster inference without cloud roundtrips. Google's Gemini will remain available but will no longer be the default AI assistant — a shift that could redirect millions of daily queries.", link: "https://www.engadget.com/ai/samsung-is-adding-perplexity-to-galaxy-ai-for-its-upcoming-s26-series-203729539.html"),
  (headline: "Google Restricts AI Ultra Subscribers Over Third-Party OAuth Client", source: "Implicator.ai", blurb: "Dozens of paid Gemini AI Ultra subscribers report having their accounts suspended after Google detected access through OpenClaw, a popular third-party OAuth client. Google's terms technically prohibit automated access through consumer subscriptions, but enforcement had been lax until now. Affected users say they received no warning — just a terse email stating accounts were 'under review.' Developer Peter Steinberger says he may remove OpenClaw support entirely. The crackdown has ignited debate about whether API access should be bundled with the $30/month Ultra tier.", link: "https://www.implicator.ai/google-restricts-ai-ultra-subscribers-over-openclaw-oauth-days-after-anthropic-ban/"),
  (headline: "Dell, Lenovo Working With Nvidia on Arm-Based Laptop SoC for H1 2026", source: "Wall Street Journal", blurb: "Dell, Lenovo, and other PC makers are working with Nvidia on laptops powered by the Arm-based Nvidia-MediaTek system-on-chip, sources say. The partnership aims to make PCs lighter and thinner while maintaining long battery life — and could launch as soon as the first half of 2026. The move represents Nvidia's biggest push into consumer computing since its early GPU days, challenging Qualcomm's Snapdragon X and Apple's M-series silicon.", link: "https://www.wsj.com/tech/nvidia-wants-to-be-the-brain-of-consumer-pcs-once-again-9e1e41b3"),
  (headline: "Russia-Linked Crypto Exchanges Continue to Enable Sanctions Evasion", source: "Elliptic", blurb: "A new report from blockchain analytics firm Elliptic identifies Bitpapa and Exmo as critical nodes in a network of cryptocurrency exchanges facilitating sanctions evasion. The exchanges process billions in monthly volume through peer-to-peer trading desks that make origin tracing nearly impossible, allowing sanctioned Russian entities to convert rubles to stablecoins and eventually to hard currency in jurisdictions with weaker oversight.", link: "https://www.elliptic.co/blog/russia-linked-cryptocurrency-services-and-sanctions-evasion"),
  (headline: "South Korea Chip Exports Surge 134% as AI Demand Powers Through Tariff Fears", source: "Bloomberg", blurb: "South Korean trade data shows chip exports rose 134% year-over-year while computer peripherals climbed 129% in the first 20 days of February. The gains extend a remarkable streak driven by insatiable AI demand, even as trade uncertainty over US tariff policy looms. Samsung and SK Hynix continue to benefit from the global scramble for high-bandwidth memory chips that power AI training clusters.", link: "https://www.bloomberg.com/news/articles/2026-02-23/s-korea-s-early-exports-show-resilience-despite-us-tariff-risks"),
)

#let hn-items = (
  (title: "Ladybird Browser Adopts Rust, With Help From AI", body: "The Ladybird browser project announced it is adopting Rust to replace C++ as its primary systems language — and used AI coding agents to accelerate the transition. Creator Andreas Kling explained that the team previously explored Swift but found C++ interop lacking and platform support limited outside the Apple ecosystem. When they first evaluated Rust in 2024, they rejected it because the web platform's deep OOP inheritance hierarchies were a poor fit for Rust's ownership model. But after 'another year of treading water,' pragmatism won out. The first target was LibJS, Ladybird's JavaScript engine. Kling used Claude Code and Codex for the translation — describing the process as 'human-directed, not autonomous code generation,' with hundreds of small prompts and multiple adversarial review passes. The result was 25,000 lines of Rust producing byte-for-byte identical output, completed in two weeks instead of the months it would have taken by hand.", link: "https://ladybird.org/posts/adopting-rust/"),
  (title: "Elsevier Shuts Down Finance Journal Citation Cartel", body: "The world's largest academic publisher has retracted 12 papers and removed 7 editor positions after an investigation exposed what researchers are calling an 'open secret' — a citation cartel operating within Elsevier's finance journals. On Christmas Eve, nine peer-reviewed economics papers were quietly retracted from the International Review of Financial Analysis, a journal with an 18% acceptance rate. The retracted papers spanned topics from cryptocurrency analysis to climate policy, and investigators found a coordinated ring of editors and authors cross-citing each other's work to inflate impact factors. The scandal raises broader questions about the integrity of peer review in an era of publish-or-perish pressure.", link: "https://www.chrisbrunet.com/p/elsevier-shuts-down-its-finance-journal"),
  (title: "0 A.D. Drops the Alpha Label With Release 28: Boiorix", body: "Wildfire Games, the international volunteer game development team, has released version 28 of 0 A.D., the free and open-source real-time strategy game of ancient warfare. Named after the Cimbri king Boiorix, this marks the first release without the 'Alpha' label — a milestone after years of development. The game is licensed under GPL v2 for code and CC-BY-SA 3.0 for art, and remains completely free with no freemium hooks or in-game ads. The team is actively seeking contributors in social media management, testing, translation, and development.", link: "https://play0ad.com/new-release-0-a-d-release-28-boiorix/"),
  (title: "Loops: A Federated, Open-Source TikTok Alternative", body: "A new project called Loops aims to be the fediverse's answer to TikTok — a federated, open-source short-video platform built on ActivityPub. It features a vertical swipe feed, a 'For You' discovery algorithm driven by engagement rather than ads, and creator-first tools including a minimal camera for capturing vertical loops. Because Loops speaks ActivityPub, videos can reach users on Mastodon, Pixelfed, and other compatible platforms. The project pitches itself as 'all the fun of short-form video, none of the corporate control,' with each instance community-owned and moderated.", link: "https://joinloops.org/"),
  (title: "Pope Tells Priests to Use Their Brains, Not AI, to Write Homilies", body: "Pope Leo XIV has issued a direct message to Catholic clergy: write your own homilies. The pontiff expressed concern that priests are turning to large language models to generate sermons, arguing that the faithful deserve words that come from genuine spiritual reflection rather than algorithmic pattern-matching. The comments come as AI text generation tools have become ubiquitous across professions, raising questions about authenticity in fields from education to religious ministry.", link: "https://www.ewtnnews.com/vatican/pope-leo-xiv-tells-priests-to-use-their-brains-not-ai-to-write-homilies"),
)

#let producthunt-items = (
  (name: "Siteline", tagline: "Growth analytics for the agentic web", link: "https://www.producthunt.com/products/siteline"),
  (name: "Wispr Flow for Android", tagline: "AI dictation that turns messy speech into polished text", link: "https://www.producthunt.com/products/wisprflow"),
  (name: "Cuto", tagline: "One prompt, commercial-grade video edits", link: "https://www.producthunt.com/products/cuto"),
  (name: "Callio", tagline: "Connect any API with AI Agent in under 5 mins", link: "https://www.producthunt.com/products/callio-3"),
  (name: "TypeBoost", tagline: "Your personal AI writing toolkit, inside any app", link: "https://www.producthunt.com/products/typeboost-2"),
)

#let arxiv-items = (
  (title: "WeWrite: Personalized Query Rewriting in Video Search", authors: "Cheng et al.", categories: "cs.IR, cs.CV, cs.LG", link: "https://arxiv.org/abs/2602.17667", abstract: "User historical behaviors provide rich context for search intent, but traditional methods suffer from signal dilution. WeWrite proposes a personalized demand-aware query rewriting framework addressing three challenges: when to rewrite (an automated posterior-based mining strategy extracts high-quality samples), how to rewrite (hybrid SFT plus GRPO training aligns LLM output with retrieval), and deployment (a parallel 'Fake Recall' architecture ensures low latency). Online A/B testing on a large-scale video platform shows WeWrite improves click-through volume by 1.07% and reduces query reformulation rate by 2.97%."),
  (title: "The Dark Side of Dark Mode: User Behaviour Rebound Effects", authors: "Datson", categories: "cs.HC, cs.PF", link: "https://arxiv.org/abs/2602.17670", abstract: "Dark mode is widely recommended as an energy-saving measure for OLED displays, but this pilot study reveals a rebound effect: users increase display brightness when viewing dark-themed pages, potentially negating energy savings. The findings suggest that the interplay between content color scheme and user behavior must be carefully considered in sustainability guidelines — dark mode's benefits are not as straightforward as commonly believed."),
  (title: "AI Hallucination from Students' Perspective: A Thematic Analysis", authors: "Shoufan & Esmaeil", categories: "cs.HC, cs.AI, cs.CL", link: "https://arxiv.org/abs/2602.17671", abstract: "As students increasingly rely on LLMs, hallucinations pose a growing threat to learning. Surveying 63 university students, this study found reported issues primarily relate to fabricated citations, overconfident but misleading responses, poor prompt adherence, and sycophancy. Students detect hallucinations through intuitive judgment or cross-checking with external sources. Notably, many described AI as a 'research engine that fabricates when it cannot locate answers' — a mental model that obscures how generative models actually work."),
)

#let github-items = (
  (repo: "abhigyanpatwari/GitNexus", blurb: "The Zero-Server Code Intelligence Engine. A client-side knowledge graph creator that runs entirely in your browser — drop in a GitHub repo or ZIP file and get an interactive knowledge graph of the codebase.", language: "TypeScript", stars: "1.7k", link: "https://github.com/abhigyanpatwari/GitNexus"),
  (repo: "stan-smith/FossFLOW", blurb: "Make beautiful isometric infrastructure diagrams. A visual tool for creating cloud architecture diagrams with an isometric perspective and export to SVG.", language: "TypeScript", stars: "18.4k", link: "https://github.com/stan-smith/FossFLOW"),
  (repo: "VectifyAI/PageIndex", blurb: "Document Index for Vectorless, Reasoning-based RAG. Instead of chunking and embedding documents, PageIndex maintains a structured page-level index that LLMs can reason over directly.", language: "Python", stars: "16.4k", link: "https://github.com/VectifyAI/PageIndex"),
  (repo: "cloudflare/agents", blurb: "Build and deploy AI Agents on Cloudflare. An official framework for building persistent, stateful agents with tool use, memory, and scheduling on Cloudflare Workers.", language: "TypeScript", stars: "3.9k", link: "https://github.com/cloudflare/agents"),
  (repo: "NevaMind-AI/memU", blurb: "Memory for 24/7 proactive agents. A structured memory layer for always-on agents like OpenClaw bots, with per-user memory isolation and automatic context summarization.", language: "Python", stars: "9.9k", link: "https://github.com/NevaMind-AI/memU"),
  (repo: "siteboon/claudecodeui", blurb: "Use Claude Code on mobile and web with CloudCLI. A free open-source web GUI for managing Claude Code sessions and projects remotely from any device.", language: "JavaScript", stars: "6.5k", link: "https://github.com/siteboon/claudecodeui"),
)

#let youtube-items = (
  (channel: "Mehul Mohan", title: "MCP Killer Is Here", link: "https://www.youtube.com/watch?v=D8Nrs8_oxSc", summary: "Mehul walks through Cloudflare's new 'as-code mode' for AI agents, which lets you give an agent an entire API of arbitrary size in under 1,000 tokens. The video explains how MCPs have become the standard way for agents to use external tools, but every tool added fills the context window — leaving less room for actual work. Cloudflare's approach compresses tool definitions into compact code representations, dramatically reducing token overhead while preserving full functionality. Mehul covers the fundamentals of tool calling, the tension between tool breadth and context limits, and why this matters for anyone building agent workflows."),
  (channel: "AICodeKing", title: "Claude Code New Updates: Better Desktop App, Simple Mode, Worktrees & More", link: "https://www.youtube.com/watch?v=BMG4c-QT8hI", summary: "A comprehensive rundown of Claude Code's recent feature blitz. Key highlights include native Git worktree isolation (the -w flag gives each session its own worktree, eliminating conflicts between parallel sessions), improved background agent control with Ctrl+F kill confirmation, the new config change hook for enterprise security auditing, and the upgraded desktop app with built-in app preview and GitHub integration. The video also covers Opus 4.6, automemory, and the new simple mode for less technical users."),
)

#let xkcd-item = (
  has-comic: true,
  title: "Eliminating the Impossible",
  alt-text: "If you've eliminated a few possibilities and you can't think of any others, your weird theory is proven right — isn't quite as rhetorically compelling.",
  img-path: "xkcd_latest.png",
)

// ─── PAGE SETUP ─────────────────────────────────────────────────────────────

#set page(
  paper: "a4",
  margin: (top: 1cm, bottom: 1.3cm, left: 1.3cm, right: 1.3cm),
  footer: context {
    set text(size: 6.5pt, fill: luma(130), font: "Libertinus Serif")
    line(length: 100%, stroke: 0.2pt + luma(180))
    v(2pt)
    grid(
      columns: (1fr, 1fr, 1fr),
      align(left)[Vallie's Daily],
      align(center)[#edition-date],
      align(right)[Page #counter(page).display() of #counter(page).final().first()],
    )
  },
)

#set text(font: "Libertinus Serif", size: 8.2pt, lang: "en")
#set par(justify: true, leading: 0.48em)

// Links: clickable but visually subtle (no underline, dark ink color)
#show link: it => {
  set text(fill: rgb("#111111"))
  it
}

// ─── STYLE HELPERS ──────────────────────────────────────────────────────────

#let rule-thin = line(length: 100%, stroke: 0.25pt + luma(120))
#let rule-thick = line(length: 100%, stroke: 1pt + luma(0))
#let rule-med = line(length: 100%, stroke: 0.4pt + luma(40))
#let rule-double = { line(length: 100%, stroke: 0.6pt + luma(0)); v(1.2pt); line(length: 100%, stroke: 0.25pt + luma(0)) }

#let section-head(title) = {
  v(1pt)
  rule-med
  v(1.5pt)
  text(size: 6.5pt, weight: "bold", tracking: 0.12em, upper(title))
  v(0.5pt)
  rule-thin
  v(2pt)
}

#let hl-large(body, url) = link(url)[#text(size: 15pt, weight: "bold", body)]
#let hl-med(body, url) = link(url)[#text(size: 11pt, weight: "bold", body)]
#let hl-small(body, url) = link(url)[#text(size: 9pt, weight: "bold", body)]
#let src-tag(body) = text(size: 6.5pt, fill: luma(100), style: "italic", body)
#let byline(body) = text(size: 6.5pt, fill: luma(80), style: "italic", body)
#let sep = { v(2pt); rule-thin; v(2pt) }

// ─── MASTHEAD ───────────────────────────────────────────────────────────────

#rule-thick
#v(2pt)
#grid(
  columns: (1fr, auto, 1fr),
  align(left + horizon)[#text(size: 6pt, tracking: 0.06em, fill: luma(60), upper(tagline))],
  align(center)[#image("masthead.png", width: 48%)],
  align(right + horizon)[#text(size: 6pt, tracking: 0.06em, fill: luma(60))[#edition-date #h(6pt) #edition-number]],
)
#v(1pt)
#rule-double
#v(4pt)

// ─── LEAD STORY (full width) ────────────────────────────────────────────────

#if techmeme-items.len() > 0 {
  let lead = techmeme-items.at(0)
  hl-large(lead.headline, lead.link)
  v(1.5pt)
  src-tag(lead.source)
  v(3pt)
  text(size: 8.5pt, lead.blurb)
  v(4pt)
  rule-med
  v(3pt)
}

// ─── TWO-COLUMN BODY ────────────────────────────────────────────────────────
// Typst columns() flows per-page: left col p1 → right col p1 → left col p2 → etc.

#columns(2, gutter: 14pt)[

// ── Tech Headlines ──
#if techmeme-items.len() > 1 {
  section-head("Tech Headlines")
  for (i, item) in techmeme-items.slice(1).enumerate() {
    hl-small(item.headline, item.link)
    v(1pt)
    src-tag(item.source)
    v(2pt)
    text(size: 7.8pt, item.blurb)
    if i < techmeme-items.len() - 2 { sep }
  }
  v(1pt)
}

// ── Hacker News ──
#if hn-items.len() > 0 {
  section-head("Hacker News")
  for (i, item) in hn-items.enumerate() {
    hl-small(item.title, item.link)
    v(1pt)
    text(size: 7.8pt, item.body)
    if i < hn-items.len() - 1 { sep }
  }
  v(1pt)
}

// ── Product Launches ──
#if producthunt-items.len() > 0 {
  section-head("Product Launches")
  for (i, item) in producthunt-items.enumerate() {
    link(item.link)[*#item.name*]
    h(3pt)
    text(size: 7.2pt, fill: luma(70))[— #item.tagline]
    if i < producthunt-items.len() - 1 { v(2pt) }
  }
  v(1pt)
}

// ── Trending Repos ──
#if github-items.len() > 0 {
  section-head("Trending Repos")
  for (i, item) in github-items.enumerate() {
    {
      link(item.link)[#text(size: 7pt, weight: "bold", font: "Menlo", item.repo)]
      h(4pt)
      text(size: 5.5pt, fill: luma(100))[#item.language #if item.stars != "" [★ #item.stars]]
    }
    v(1pt)
    text(size: 7.2pt, item.blurb)
    if i < github-items.len() - 1 { sep }
  }
  v(1pt)
}

// ── YouTube Roundup ──
#if youtube-items.len() > 0 {
  section-head("YouTube Roundup")
  for (i, item) in youtube-items.enumerate() {
    hl-small(item.title, item.link)
    v(0.5pt)
    byline(item.channel)
    v(1pt)
    text(size: 7.2pt, item.summary)
    if i < youtube-items.len() - 1 { sep }
  }
}

] // end columns

// ─── RESEARCH PAPERS (full-width, after columns) ────────────────────────────

#if arxiv-items.len() > 0 {
  section-head("Research Papers")
  for (i, item) in arxiv-items.enumerate() {
    hl-small(item.title, item.link)
    v(0.5pt)
    byline(item.authors + " — " + item.categories)
    v(1pt)
    text(size: 7.2pt, item.abstract)
    if i < arxiv-items.len() - 1 { sep }
  }
  v(1pt)
}

// ─── XKCD (full-width strip, after columns) ────────────────────────────────

#if xkcd-item.has-comic {
  v(2pt)
  rule-med
  v(1.5pt)
  text(size: 6.5pt, weight: "bold", tracking: 0.12em, upper("XKCD"))
  v(0.5pt)
  rule-thin
  v(3pt)
  align(center, text(size: 8.5pt, weight: "bold", xkcd-item.title))
  v(2pt)
  if xkcd-item.img-path != "" {
    align(center, image(xkcd-item.img-path, width: 60%))
    v(1pt)
  }
  align(center, text(size: 6.5pt, style: "italic", fill: luma(80), xkcd-item.alt-text))
}
