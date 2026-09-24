"""Build static HTML pages for the UNESCO weekly reports.

Input:  weekly_reports/{ai,human_rights,environment}/YYYY-MM-DD_unesco_<topic>_weekly[_en].md
        templates/weekly/layout.html
Output: weekly/ and en/weekly/ (fully regenerated), plus the marked
        GENERATED regions inside index.html and en/index.html.
"""

import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from xml.etree import ElementTree as etree

import markdown
from markdown.treeprocessors import Treeprocessor

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "weekly_reports"
LAYOUT = Template((ROOT / "templates/weekly/layout.html").read_text(encoding="utf-8"))
SITE_URL = "https://ohkaminoseiza.github.io/UNESCO/"

TOPICS = {
    # source folder: (url slug, ja label, en label)
    "ai": ("ai", "AI", "AI"),
    "human_rights": ("human-rights", "人権", "Human Rights"),
    "environment": ("environment", "環境", "Environment"),
}

LANGS = {
    "ja": {
        "out": "weekly",
        "home": "",
        "site_title": "教育・科学・文化",
        "og_locale": "ja_JP",
        "copyright": "&copy; 2026 個人メディア - 教育・科学・文化 All Rights Reserved.",
        "weekly": "ウィークリーレポート",
        "archive_lead": "ユネスコ公式情報をもとに、AI・人権・環境の動向を毎週まとめたレポートの一覧です。",
        "latest": "最新のウィークリーレポート",
        "all": "すべて",
        "all_reports": "すべてのウィークリーレポート &raquo;",
        "read_more": "続きを読む &raquo;",
        "prev": "&laquo; 前の週",
        "next": "次の週 &raquo;",
        "same_week": "同じ週の他テーマ",
        "topic_list": "のウィークリーレポート一覧",
        "reports": "レポート数",
        "weeks": "発行週",
        "home_label": "ホーム",
        "switch": '<span class="lang-current">日本語</span> | <a href="{href}">English</a>',
    },
    "en": {
        "out": "en/weekly",
        "home": "en/",
        "site_title": "Education, Science, and Culture",
        "og_locale": "en_US",
        "copyright": "&copy; 2026 Personal Media - Education, Science, and Culture All Rights Reserved.",
        "weekly": "Weekly Reports",
        "archive_lead": "Weekly summaries of UNESCO's official updates on AI, human rights and the environment.",
        "latest": "Latest Weekly Reports",
        "all": "All",
        "all_reports": "All weekly reports &raquo;",
        "read_more": "Read More &raquo;",
        "prev": "&laquo; Previous week",
        "next": "Next week &raquo;",
        "same_week": "Other topics this week",
        "topic_list": " Weekly Reports",
        "reports": "Reports",
        "weeks": "Weeks",
        "home_label": "Home",
        "switch": '<a href="{href}">日本語</a> | <span class="lang-current">English</span>',
    },
}

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_unesco_([a-z_]+)_weekly(_en)?\.md$")
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
SIDEBAR_WEEKS = 8


def warn(path, message):
    # GitHub Actions annotation; also readable in a local terminal.
    print(f"::warning file={path.relative_to(ROOT)}::{message}")


@dataclass
class Report:
    topic: str
    lang: str
    date: str
    title: str
    body_md: str
    source: Path
    excerpt: str = ""
    html_body: str = ""
    older: "Report | None" = None
    newer: "Report | None" = None
    siblings: list = field(default_factory=list)

    @property
    def slug(self):
        return TOPICS[self.topic][0]

    @property
    def path(self):
        return f"{LANGS[self.lang]['out']}/{self.slug}/{self.date}.html"


# ---------------------------------------------------------------- Markdown

URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#@!$&'*+,;=%]+")


def split_urls(text):
    """Return (leading text, [<a> elements whose tails hold the text in between])."""
    lead, links, pos = text, [], 0
    for m in URL_RE.finditer(text):
        url = m.group(0).rstrip(".,;:!?'")
        a = etree.Element("a", href=url)
        a.text = url
        if links:
            links[-1].tail = text[pos:m.start()]
        else:
            lead = text[:m.start()]
        links.append(a)
        pos = m.start() + len(url)
    if links:
        links[-1].tail = text[pos:]
    return lead, links


class Linkify(Treeprocessor):
    """Turn bare URLs (common in the Sources lists) into links, outside existing links and code."""

    SKIP = {"a", "code", "pre"}

    def run(self, root):
        self.walk(root)

    def walk(self, el):
        if el.text:
            el.text, links = split_urls(el.text)
            for i, a in enumerate(links):
                el.insert(i, a)
        for child in list(el):
            if child.tag not in self.SKIP:
                self.walk(child)
            if child.tail:
                child.tail, links = split_urls(child.tail)
                idx = list(el).index(child)
                for j, a in enumerate(links, start=1):
                    el.insert(idx + j, a)


class LinkPolicy(Treeprocessor):
    """Allow only safe link targets and open external links in a new tab."""

    SAFE = re.compile(r"^(https?:|mailto:|#|/|\.|[^:/?#]+([/?#]|$))", re.I)

    def run(self, root):
        for a in root.iter("a"):
            href = (a.get("href") or "").strip()
            if not self.SAFE.match(href):
                a.attrib.pop("href", None)
            elif href.lower().startswith(("http://", "https://")):
                a.set("target", "_blank")
                a.set("rel", "noopener noreferrer")
        for img in list(root.iter("img")):
            if not (img.get("src") or "").lower().startswith("https://"):
                img.attrib.pop("src", None)


def make_markdown():
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "nl2br"])
    # Reports are written from external web content: never pass raw HTML through.
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    md.treeprocessors.register(Linkify(md), "linkify", 15)
    md.treeprocessors.register(LinkPolicy(md), "link_policy", 5)
    return md


def plain_text(md_text):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md_text)
    text = re.sub(r"[*_`#>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_excerpt(body_md, lang):
    """First paragraph of the 概要 / Overview section (or of the body)."""
    m = re.search(r"^##\s*(概要|Overview)\s*$\n+(.+?)(\n\s*\n|\Z)", body_md, re.M | re.S)
    if m:
        para = m.group(2)
    else:
        paras = [p for p in re.split(r"\n\s*\n", body_md) if p.strip() and not p.startswith("#")]
        para = paras[0] if paras else ""
    text = plain_text(para)
    limit = 120 if lang == "ja" else 240
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if lang == "en" and " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip("、。,. ") + "…"


# ----------------------------------------------------------------- Loading

def load_reports():
    reports = []
    for topic in TOPICS:
        folder = REPORTS_DIR / topic
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            m = FILENAME_RE.match(path.name)
            if not m or m.group(2) != topic:
                warn(path, "ファイル名が命名規則に合わないため公開対象外です")
                continue
            date, lang = m.group(1), "en" if m.group(3) else "ja"
            text = path.read_text(encoding="utf-8").lstrip("﻿")
            first, _, rest = text.partition("\n")
            if first.startswith("# "):
                title, body = first[2:].strip(), rest
            else:
                warn(path, "1行目に「# タイトル」がありません")
                label = TOPICS[topic][1 if lang == "ja" else 2]
                title, body = f"{label} {date}", text
            reports.append(Report(topic, lang, date, title, body, path))
    return reports


def link_reports(reports):
    by_key = {}
    for r in reports:
        by_key.setdefault((r.topic, r.lang), []).append(r)
    for series in by_key.values():
        series.sort(key=lambda r: r.date)
        for older, newer in zip(series, series[1:]):
            older.newer, newer.older = newer, older
    for r in reports:
        r.siblings = sorted(
            (o for o in reports if o.lang == r.lang and o.date == r.date and o.topic != r.topic),
            key=lambda o: list(TOPICS).index(o.topic))


# --------------------------------------------------------------- Rendering

def rel(from_path, to_path):
    return "../" * from_path.count("/") + to_path


def fmt_date(date, lang):
    y, m, d = (int(x) for x in date.split("-"))
    return f"{y}年{m}月{d}日" if lang == "ja" else f"{MONTHS_EN[m - 1]} {d}, {y}"


def fmt_month(month, lang):
    y, m = (int(x) for x in month.split("-"))
    return f"{y}年{m}月" if lang == "ja" else f"{MONTHS_EN[m - 1]} {y}"


def topic_label(topic, lang):
    return TOPICS[topic][1 if lang == "ja" else 2]


def badge(topic, lang):
    return f'<span class="weekly-badge weekly-badge--{TOPICS[topic][0]}">{topic_label(topic, lang)}</span>'


def render_page(path, lang, title, description, main, available, og_type="website"):
    L = LANGS[lang]
    other_lang = "en" if lang == "ja" else "ja"
    other_out = LANGS[other_lang]["out"]
    other_path = other_out + path[len(L["out"]):]
    alternates = ""
    if other_path in available:
        alternates = (f'    <link rel="alternate" hreflang="{lang}" href="{SITE_URL}{path}">\n'
                      f'    <link rel="alternate" hreflang="{other_lang}" href="{SITE_URL}{other_path}">')
    else:
        other_path = f"{other_out}/index.html"
    return LAYOUT.substitute(
        lang=lang,
        title=html.escape(f"{title} - {L['site_title']}"),
        og_title=html.escape(title),
        description=html.escape(description),
        canonical=f"{SITE_URL}{path}",
        alternates=alternates,
        og_type=og_type,
        og_locale=L["og_locale"],
        site_title=L["site_title"],
        root=rel(path, ""),
        home=rel(path, L["home"]),
        lang_switch=L["switch"].format(href=rel(path, other_path)),
        main=main,
        copyright=L["copyright"],
    )


def breadcrumb(path, lang, items):
    L = LANGS[lang]
    parts = [f'<a href="{rel(path, L["home"] + "index.html")}">{L["home_label"]}</a>']
    for label, target in items:
        parts.append(f'<a href="{rel(path, target)}">{label}</a>' if target else f"<span>{label}</span>")
    return '<nav class="breadcrumb" aria-label="breadcrumb">' + " &rsaquo; ".join(parts) + "</nav>"


def render_report(r, available):
    L = LANGS[r.lang]
    out = L["out"]
    crumbs = breadcrumb(r.path, r.lang, [
        (L["weekly"], f"{out}/index.html"),
        (topic_label(r.topic, r.lang), f"{out}/{r.slug}/index.html"),
        (fmt_date(r.date, r.lang), None),
    ])
    pager = '<nav class="weekly-pager">'
    pager += (f'<a class="weekly-pager-prev" href="{rel(r.path, r.older.path)}">{L["prev"]}</a>'
              if r.older else "<span></span>")
    pager += (f'<a class="weekly-pager-next" href="{rel(r.path, r.newer.path)}">{L["next"]}</a>'
              if r.newer else "<span></span>")
    pager += "</nav>"
    siblings = ""
    if r.siblings:
        links = "".join(
            f'<li><a href="{rel(r.path, s.path)}">{badge(s.topic, r.lang)} {html.escape(s.title)}</a></li>'
            for s in r.siblings)
        siblings = f'<aside class="weekly-related"><h2>{L["same_week"]}</h2><ul>{links}</ul></aside>'
    main = f"""        {crumbs}
        <article class="weekly-article">
            <header class="weekly-article-header">
                <p class="weekly-meta">{badge(r.topic, r.lang)} <time datetime="{r.date}">{fmt_date(r.date, r.lang)}</time></p>
                <h1>{html.escape(r.title)}</h1>
            </header>
            <div class="weekly-body">
{r.html_body}
            </div>
        </article>
        {pager}
        {siblings}"""
    return render_page(r.path, r.lang, r.title, r.excerpt, main, available, og_type="article")


def report_card(from_path, r, heading="h3"):
    L = LANGS[r.lang]
    href = rel(from_path, r.path)
    return f"""<article class="news-article weekly-card">
                    <p class="article-meta">{badge(r.topic, r.lang)} {fmt_date(r.date, r.lang)}</p>
                    <{heading}><a href="{href}">{html.escape(r.title)}</a></{heading}>
                    <p class="article-summary">{html.escape(r.excerpt)}</p>
                    <a href="{href}" class="read-more">{L["read_more"]}</a>
                </article>"""


def topic_filter(path, lang, active):
    out = LANGS[lang]["out"]
    items = [(LANGS[lang]["all"], f"{out}/index.html", active is None)]
    items += [(topic_label(t, lang), f"{out}/{TOPICS[t][0]}/index.html", active == t) for t in TOPICS]
    links = "".join(
        f'<a class="weekly-chip{" is-active" if on else ""}" href="{rel(path, target)}">{label}</a>'
        for label, target, on in items)
    return f'<nav class="weekly-filter">{links}</nav>'


def render_archive(lang, reports, available):
    L = LANGS[lang]
    path = f"{L['out']}/index.html"
    dates = sorted({r.date for r in reports}, reverse=True)
    months = {}
    for d in dates:
        months.setdefault(d[:7], []).append(d)
    groups = []
    for month, month_dates in months.items():
        rows = []
        for d in month_dates:
            chips = "".join(
                f'<a class="weekly-chip weekly-chip--{r.slug}" href="{rel(path, r.path)}">{topic_label(r.topic, lang)}</a>'
                for r in sorted((r for r in reports if r.date == d), key=lambda r: list(TOPICS).index(r.topic)))
            rows.append(f'<div class="weekly-archive-row"><time datetime="{d}">{fmt_date(d, lang)}</time>'
                        f'<div class="weekly-chips">{chips}</div></div>')
        groups.append(f'<section class="weekly-archive-month"><h2>{fmt_month(month, lang)}</h2>{"".join(rows)}</section>')
    main = f"""        {breadcrumb(path, lang, [(L["weekly"], None)])}
        <header class="weekly-list-header">
            <h1>{L["weekly"]}</h1>
            <p>{L["archive_lead"]}</p>
            <p class="weekly-stats">{L["reports"]}: {len(reports)} / {L["weeks"]}: {len(dates)}</p>
        </header>
        {topic_filter(path, lang, None)}
        {"".join(groups)}"""
    return path, render_page(path, lang, L["weekly"], L["archive_lead"], main, available)


def render_topic_index(lang, topic, reports, available):
    L = LANGS[lang]
    path = f"{L['out']}/{TOPICS[topic][0]}/index.html"
    title = topic_label(topic, lang) + L["topic_list"]
    items = sorted((r for r in reports if r.topic == topic), key=lambda r: r.date, reverse=True)
    cards = "\n                ".join(report_card(path, r, heading="h2") for r in items)
    main = f"""        {breadcrumb(path, lang, [(L["weekly"], f"{L['out']}/index.html"), (topic_label(topic, lang), None)])}
        <header class="weekly-list-header">
            <h1>{title}</h1>
        </header>
        {topic_filter(path, lang, topic)}
        <div class="weekly-card-list">
                {cards}
        </div>"""
    return path, render_page(path, lang, title, L["archive_lead"], main, available)


# ---------------------------------------------------- Home page (markers)

def home_latest(lang, reports):
    L = LANGS[lang]
    page = L["home"] + "index.html"
    latest = []
    for topic in TOPICS:
        series = sorted((r for r in reports if r.topic == topic), key=lambda r: r.date)
        if series:
            latest.append(series[-1])
    cards = "\n                ".join(report_card(page, r) for r in latest)
    return f"""<section class="weekly-latest">
                <h2 class="section-title">{L["latest"]}</h2>
                {cards}
                <p class="weekly-more"><a href="{rel(page, L['out'] + '/index.html')}">{L["all_reports"]}</a></p>
            </section>"""


def home_sidebar(lang, reports):
    L = LANGS[lang]
    page = L["home"] + "index.html"
    dates = sorted({r.date for r in reports}, reverse=True)[:SIDEBAR_WEEKS]
    rows = []
    for d in dates:
        chips = "".join(
            f'<a class="weekly-chip weekly-chip--{r.slug}" href="{rel(page, r.path)}">{topic_label(r.topic, lang)}</a>'
            for r in sorted((r for r in reports if r.date == d), key=lambda r: list(TOPICS).index(r.topic)))
        rows.append(f'<li><time datetime="{d}">{fmt_date(d, lang)}</time><div class="weekly-chips">{chips}</div></li>')
    return f"""<div class="widget weekly-widget">
                <h3 class="widget-title">{L["weekly"]}</h3>
                <ul class="weekly-widget-list">
                    {(chr(10) + " " * 20).join(rows)}
                </ul>
                <p class="weekly-more"><a href="{rel(page, L['out'] + '/index.html')}">{L["all_reports"]}</a></p>
            </div>"""


def replace_region(text, name, content, path):
    pattern = re.compile(
        rf"(<!-- BEGIN GENERATED {name} [^\n]*-->)(.*?)(\n[ \t]*<!-- END GENERATED {name} -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"{path}: <!-- BEGIN GENERATED {name} ... --> / <!-- END GENERATED {name} --> が見つかりません")
    return pattern.sub(lambda m: m.group(1) + "\n            " + content + m.group(3), text, count=1)


# -------------------------------------------------------------------- Main

def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main():
    reports = load_reports()
    link_reports(reports)
    md = make_markdown()
    for r in reports:
        r.excerpt = extract_excerpt(r.body_md, r.lang)
        r.html_body = md.reset().convert(r.body_md)

    for lang in LANGS:
        shutil.rmtree(ROOT / LANGS[lang]["out"], ignore_errors=True)

    available = {r.path for r in reports}
    for lang in LANGS:
        out = LANGS[lang]["out"]
        available.add(f"{out}/index.html")
        available.update(f"{out}/{s}/index.html" for s, _, _ in TOPICS.values())

    pages = {}
    for r in reports:
        pages[r.path] = render_report(r, available)
    for lang in LANGS:
        lang_reports = [r for r in reports if r.lang == lang]
        path, page = render_archive(lang, lang_reports, available)
        pages[path] = page
        for topic in TOPICS:
            path, page = render_topic_index(lang, topic, lang_reports, available)
            pages[path] = page
    for path, page in pages.items():
        write(path, page)

    for lang in LANGS:
        home_path = LANGS[lang]["home"] + "index.html"
        lang_reports = [r for r in reports if r.lang == lang]
        text = (ROOT / home_path).read_text(encoding="utf-8")
        text = replace_region(text, "weekly-latest", home_latest(lang, lang_reports), home_path)
        text = replace_region(text, "weekly-sidebar", home_sidebar(lang, lang_reports), home_path)
        write(home_path, text)

    print(f"Built {len(reports)} reports, {len(pages)} pages.")


if __name__ == "__main__":
    main()
