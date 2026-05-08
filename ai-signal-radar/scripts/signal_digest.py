#!/usr/bin/env python3
import argparse
import html
import re
import ssl
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


@dataclass
class Item:
    title: str
    url: str
    source: str
    summary: str


def fetch(url: str, insecure: bool = False) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(req, timeout=20, context=context) as resp:
        data = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        return data.decode(charset, errors="replace")


def clean_text(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def domain(url: str) -> str:
    host = urlparse(url).netloc
    return host.replace("www.", "") or "local"


def parse_feed(xml_text: str, source_url: str):
    root = ET.fromstring(xml_text)
    items = []
    for node in root.findall(".//item"):
        title = (node.findtext("title") or "Untitled").strip()
        link = (node.findtext("link") or source_url).strip()
        summary = clean_text(node.findtext("description") or node.findtext("summary") or "")
        items.append(Item(title, link, domain(source_url), summary[:500]))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for node in root.findall(".//atom:entry", ns):
        title = (node.findtext("atom:title", default="Untitled", namespaces=ns) or "Untitled").strip()
        link = source_url
        link_node = node.find("atom:link", ns)
        if link_node is not None and link_node.attrib.get("href"):
            link = link_node.attrib["href"]
        summary = clean_text(
            node.findtext("atom:summary", default="", namespaces=ns)
            or node.findtext("atom:content", default="", namespaces=ns)
        )
        items.append(Item(title, link, domain(source_url), summary[:500]))
    return items


def parse_page(text: str, url: str):
    title_match = re.search(r"<title[^>]*>([\s\S]*?)</title>", text, flags=re.I)
    title = clean_text(title_match.group(1)) if title_match else url
    body = clean_text(text)
    return [Item(title=title[:160], url=url, source=domain(url), summary=body[:500])]


def load_text_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    title = path.stem.replace("-", " ").replace("_", " ")
    return [Item(title=title, url=str(path), source="local", summary=clean_text(text)[:800])]


def category_for(item: Item):
    hay = f"{item.title} {item.summary}".lower()
    if any(k in hay for k in ["model", "llm", "gpt", "claude", "gemini", "qwen", "deepseek"]):
        return "模型与基础设施"
    if any(k in hay for k in ["github", "open source", "开源", "repo", "library", "sdk"]):
        return "开源与开发者工具"
    if any(k in hay for k in ["paper", "arxiv", "论文", "research", "benchmark"]):
        return "论文与技术研究"
    if any(k in hay for k in ["funding", "startup", "revenue", "acquire", "融资", "收购", "商业"]):
        return "商业与行业信号"
    return "产品与应用"


def score_reason(item: Item):
    hay = f"{item.title} {item.summary}".lower()
    reasons = []
    if any(k in hay for k in ["release", "launch", "发布", "推出", "announces"]):
        reasons.append("有明确发布动作")
    if any(k in hay for k in ["open source", "github", "开源"]):
        reasons.append("开发者可直接验证")
    if any(k in hay for k in ["benchmark", "eval", "性能", "评测"]):
        reasons.append("影响技术选型")
    if any(k in hay for k in ["funding", "revenue", "融资", "收购"]):
        reasons.append("包含商业信号")
    if not reasons:
        reasons.append("值得进一步确认影响范围")
    return "，".join(reasons)


def dedupe(items):
    seen = set()
    out = []
    for item in items:
        key = (item.title.lower().strip(), item.url.strip())
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def render_markdown(items):
    items = dedupe(items)
    lines = ["# AI Signal Radar", ""]
    if not items:
        return "# AI Signal Radar\n\n暂无可整理的公开信号。"

    top = items[:5]
    lines.append("## 最值得先看")
    for i, item in enumerate(top, 1):
        lines.append(f"{i}. **{item.title}**")
        lines.append(f"   - 来源: {item.source}")
        lines.append(f"   - 为什么重要: {score_reason(item)}")
        if item.url:
            lines.append(f"   - 链接: {item.url}")
    lines.append("")

    groups = {}
    for item in items:
        groups.setdefault(category_for(item), []).append(item)

    for category, group in groups.items():
        lines.append(f"## {category}")
        for item in group:
            summary = item.summary or "暂无摘要。"
            lines.append(f"- **{item.title}**")
            lines.append(f"  - {summary[:240]}")
            if item.url:
                lines.append(f"  - {item.url}")
        lines.append("")

    lines.append("## 建议下一步")
    lines.append("- 优先打开前 5 条原文确认事实。")
    lines.append("- 把可测试的工具或模型加入试用清单。")
    lines.append("- 把有商业变化的信号单独追踪一周。")
    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="Create an AI signal digest from user-provided public sources.")
    parser.add_argument("--url", action="append", default=[], help="Public RSS/Atom feed or article URL. Can be repeated.")
    parser.add_argument("--file", help="File with one URL per line.")
    parser.add_argument("--text", action="append", default=[], help="Local text/markdown file. Can be repeated.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--insecure", action="store_true", help="Skip TLS certificate verification if local CA setup is broken.")
    args = parser.parse_args()

    urls = list(args.url)
    if args.file:
        urls.extend(
            line.strip()
            for line in Path(args.file).read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )

    items = []
    for url in urls:
        try:
            text = fetch(url, insecure=args.insecure)
            if "<rss" in text[:500].lower() or "<feed" in text[:500].lower():
                items.extend(parse_feed(text, url))
            else:
                items.extend(parse_page(text, url))
        except Exception as exc:
            print(f"warning: failed to fetch {url}: {exc}", file=sys.stderr)

    for path in args.text:
        items.extend(load_text_file(Path(path)))

    print(render_markdown(items[: args.limit]))


if __name__ == "__main__":
    main()
