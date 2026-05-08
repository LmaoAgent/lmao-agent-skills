---
name: ai-signal-radar
description: Public-source AI signal radar by LMaoAgent. Use when the user wants to turn public RSS feeds, URLs, copied articles, release notes, newsletters, or raw AI news notes into a prioritized Chinese intelligence brief. This skill does not call private products or third-party branded APIs; users provide their own public sources.
---

# AI Signal Radar

Turn user-provided public sources into a concise AI intelligence brief.

This is a public-edition skill. It is intentionally source-agnostic: the user supplies RSS feeds, URLs, notes, or article text. The skill handles collection, deduplication, signal extraction, prioritization, and Chinese briefing.

## Boundary

Do not bundle private feeds, proprietary source lists, backend endpoints, cookies, credentials, ranking weights, import pipelines, or third-party branded assets.

Do not present this as a clone of another public AI news product. It is a generic workflow for user-provided sources.

## Inputs

Accept any of:

- RSS or Atom feed URLs
- Article URLs
- GitHub release/blog URLs
- pasted notes or article text
- a file containing one URL per line

## Workflow

1. Collect source material with `scripts/signal_digest.py` when URLs or feeds are provided.
2. Deduplicate by title and URL.
3. Extract the core change in one sentence.
4. Score each item qualitatively, not with hidden proprietary weights:
   - source credibility
   - novelty
   - practical impact
   - testability
   - content value
5. Group into:
   - 模型与基础设施
   - 产品与应用
   - 开源与开发者工具
   - 论文与技术研究
   - 商业与行业信号
6. Output a Chinese brief with:
   - 今日最值得看的 5 条
   - 分类摘要
   - 为什么重要
   - 建议下一步
   - source links

## Commands

Fetch RSS or URL sources:

```bash
python scripts/signal_digest.py --url https://example.com/feed.xml --url https://example.com/blog
```

Fetch URLs from a file:

```bash
python scripts/signal_digest.py --file sources.txt --limit 30
```

Read pasted or local notes:

```bash
python scripts/signal_digest.py --text notes.md
```

If local Python TLS certificates are broken, retry once with `--insecure`. Use it only for public sources.

## Briefing Style

Keep the result practical:

- Lead with the important signal, not with source mechanics.
- Mark uncertainty plainly.
- Include original links.
- Avoid hype.
- Prefer "what changed" and "what to do next" over generic summaries.
