"""Render content.json into single-language, offline HTML (report and blog) and Markdown.

Everything the page needs (fonts, ECharts, images, logo) is inlined, so one file works without a
network. Text comes only from content.json; the renderer adds labels and layout, never content.
"""
import base64
import html
import json
import mimetypes
import os
import re

from . import theme

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES = os.path.join(SKILL, "templates")
VENDOR = os.path.join(SKILL, "vendor")
RTL = {"fa", "ar", "he", "ur", "ps", "ckb"}
CREDIT = "Made with Reporch by Mobo · Behdad Morsalpoor"
FA_DIGITS = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")

LABELS = {
    "en": {"contents": "Contents", "slides": "Slides", "exit": "Exit slides", "next": "Next", "prev": "Previous",
           "menu": "Contents", "evidence": "Evidence", "data": "Show the data", "image": "Image needed",
           "appendix": "Appendix", "evidenceIndex": "Evidence", "glossary": "Glossary",
           "openQuestions": "Open questions", "source": "Source", "participant": "Participant",
           "by": "By", "priority": "Priority", "effort": "Effort", "owner": "Owner", "action": "Action",
           "method": "Method", "pending": "Still needed",
           "kinds": {"design": "Design", "screenshot": "Screenshot", "analytics": "Analytics view",
                     "illustration": "Illustration", "wireframe": "Wireframe", "photo": "Photo",
                     "diagram": "Diagram", "video": "Video", "logo": "Logo", "other": "Image"}},
    "fa": {"contents": "فهرست مطالب", "slides": "اسلاید", "exit": "خروج از اسلاید", "next": "بعدی", "prev": "قبلی",
           "menu": "فهرست", "evidence": "شواهد", "data": "نمایش داده", "image": "تصویر لازم است",
           "appendix": "پیوست", "evidenceIndex": "شواهد", "glossary": "واژه‌نامه",
           "openQuestions": "سؤال‌های باز", "source": "منبع", "participant": "شرکت‌کننده",
           "by": "نویسنده", "priority": "اولویت", "effort": "زحمت", "owner": "مسئول", "action": "اقدام",
           "method": "روش", "pending": "هنوز لازم است",
           "kinds": {"design": "طراحی", "screenshot": "اسکرین‌شات", "analytics": "نمای ابزار تحلیل",
                     "illustration": "تصویرسازی", "wireframe": "وایرفریم", "photo": "عکس",
                     "diagram": "نمودار", "video": "ویدیو", "logo": "لوگو", "other": "تصویر"}},
}


class Renderer:
    def __init__(self, doc, lang, project_dir):
        self.doc, self.lang, self.dir = doc, lang, project_dir
        self.L = LABELS.get(lang, LABELS["en"])
        self.charts = []
        self.ev = {e["id"]: e for e in doc.get("evidence") or []}
        self.analyses = {a["id"]: a for a in doc.get("analyses") or []}
        self.article = False     # the blog shows no evidence ids: its readers have no evidence index
        self.depth = 2
        self.chart_ids = {}
        self.sources = _source_names(project_dir)

    # ---------------------------------------------------------------- text helpers
    def t(self, value):
        if isinstance(value, dict):
            return value.get(self.lang) or ""
        return "" if value is None else str(value)

    def num(self, v, kind=None):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return html.escape(self.t(v))
        if kind == "percent":
            p = v * 100
            s = f"{p:.1f}".rstrip("0").rstrip(".") + ("٪" if self.lang == "fa" else "%")
        else:
            s = str(round(v)) if abs(v) >= 100 else (f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
        return s.translate(FA_DIGITS) if self.lang == "fa" else s

    def inline(self, text):
        s = html.escape(text)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
        return s

    def paras(self, value):
        parts = [p.strip() for p in re.split(r"\n\s*\n", self.t(value)) if p.strip()]
        return "".join(f"<p>{self.inline(p).replace(chr(10), '<br>')}</p>" for p in parts)

    def evidence_note(self, ids):
        if not ids or self.article:
            return ""
        refs = ", ".join(f'<a href="#ev-{html.escape(i)}">{html.escape(i)}</a>' for i in ids)
        return f'<p class="evidence">{self.L["evidence"]}: {refs}</p>'

    def data_uri(self, rel):
        path = os.path.join(self.dir, rel)
        if not os.path.isfile(path):
            return None
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

    # ---------------------------------------------------------------- blocks
    def table(self, table, cls=""):
        fmt = table.get("format") or {}
        cols = table["columns"]
        head = "".join(f"<th>{html.escape(self.t(table.get('labels', {}).get(c, c)))}</th>" for c in cols)
        body = "".join("<tr>" + "".join(f'<td class="num">{self.num(v, fmt.get(c))}</td>' if isinstance(v, (int, float))
                                       else f"<td>{self.num(v)}</td>" for c, v in zip(cols, r)) + "</tr>"
                       for r in table["rows"])
        return f'<div class="table-wrap {cls}"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

    def chart(self, chart, table, title=None, deck=False):
        known = self.chart_ids.get(id(table))
        if deck and known:                       # the deck reuses the report's chart data
            return f'<div class="chart" data-deck-chart="{known}-data" role="img" aria-label="{html.escape(self.t(title) or self.L["data"])}"></div>'
        cid = f"chart-{len(self.charts) + 1}"
        self.chart_ids[id(table)] = cid
        local = {"columns": table["columns"], "format": table.get("format") or {},
                 "rows": [[self.t(v) if isinstance(v, dict) else v for v in r] for r in table["rows"]],
                 "labels": {c: self.t(table.get("labels", {}).get(c, c)) for c in table["columns"]}}
        self.charts.append((cid, {"chart": chart, "table": local}))
        aria = html.escape(self.t(title) or self.L["data"])
        if deck:
            return f'<div class="chart" data-deck-chart="{cid}-data" role="img" aria-label="{aria}"></div>'
        return (f'<div class="chart-box"><div class="chart" data-chart="{cid}-data" role="img" aria-label="{aria}"></div></div>'
                f'<details class="data"><summary>{self.L["data"]}</summary>{self.table(table)}</details>')

    def block(self, b, show_ev=True):
        t = b["type"]
        ev = self.evidence_note(b.get("evidence")) if show_ev and t not in ("quote", "analysis") else ""
        if t == "heading":
            return f"<h3>{self.inline(self.t(b['text']))}</h3>"
        if t == "paragraph":
            return self.paras(b["text"]) + ev
        if t == "callout":
            return f'<div class="callout {html.escape(b["tone"])}">{self.paras(b["text"])}</div>{ev}'
        if t == "quote":
            src = html.escape(b["participant"]) + ("" if self.article else "".join(
                f' · <a href="#ev-{html.escape(i)}">{html.escape(i)}</a>' for i in b.get("evidence", [])))
            return f'<blockquote class="quote"><p>«{self.inline(self.t(b["text"]))}»</p><footer>{src}</footer></blockquote>' \
                if self.lang == "fa" else \
                f'<blockquote class="quote"><p>“{self.inline(self.t(b["text"]))}”</p><footer>{src}</footer></blockquote>'
        if t == "stats":
            cards = "".join(
                f'<div class="stat {html.escape(i.get("tone", ""))}"><div class="label">{self.inline(self.t(i.get("label")))}</div>'
                f'<div class="value">{self.inline(self.t(i.get("value")))}</div>'
                + (f'<div class="note">{self.inline(self.t(i.get("note")))}</div>' if i.get("note") else "") + "</div>"
                for i in b["items"])
            return f'<div class="stats">{cards}</div>{ev}'
        if t == "table":
            return self.table(b) + ev
        if t == "chart":
            return self.chart(b["chart"], b["table"], b.get("caption")) + ev
        if t in ("image", "video"):
            return self.figure(b) + ev
        if t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            return f"<{tag}>" + "".join(f"<li>{self.inline(self.t(i))}</li>" for i in b["items"]) + f"</{tag}>{ev}"
        if t == "analysis":
            return self.analysis(self.analyses[b["analysis"]], self.depth + 1)
        if t == "actionPlan":
            rows = "".join(f'<tr><td>{self.inline(self.t(i.get("text")))}</td><td class="priority">{html.escape(self.t(i.get("priority")))}</td>'
                           f'<td>{html.escape(self.t(i.get("effort")))}</td><td>{html.escape(self.t(i.get("owner")))}</td></tr>' for i in b["items"])
            L = self.L
            return (f'<div class="table-wrap action-plan"><table><thead><tr><th>{L["action"]}</th><th>{L["priority"]}</th>'
                    f'<th>{L["effort"]}</th><th>{L["owner"]}</th></tr></thead><tbody>{rows}</tbody></table></div>{ev}')
        if t == "persona":
            return f'<div class="persona"><h3>{self.inline(self.t(b["name"]))}</h3>{self.paras(b["text"])}</div>{ev}'
        if t == "flow":
            return '<ol class="flow">' + "".join(f'<li class="{html.escape(s.get("status", ""))}">{self.inline(self.t(s.get("text")))}</li>'
                                                 for s in b["steps"]) + f"</ol>{ev}"
        if t == "timeline":
            return '<ul class="timeline">' + "".join(f'<li><strong>{self.num(i.get("date"))}</strong> {self.inline(self.t(i.get("text")))}</li>'
                                                     for i in b["items"]) + f"</ul>{ev}"
        if t == "pending":
            return f'<div class="pending"><strong>{self.L["pending"]}:</strong> {self.inline(self.t(b["text"]))}</div>'
        return ""

    def blocks(self, bs):
        """Blocks in order; a run of blocks citing the same evidence shows the evidence line once, after the run."""
        out = []
        for i, b in enumerate(bs):
            nxt = bs[i + 1] if i + 1 < len(bs) else None
            same = nxt is not None and nxt["type"] not in ("quote", "analysis") and nxt.get("evidence") == b.get("evidence")
            out.append(self.block(b, show_ev=not same))
        return "".join(out)

    def figure(self, b):
        cap = f"<figcaption>{self.inline(self.t(b.get('caption')))}</figcaption>" if b.get("caption") else ""
        src = self.data_uri(b["src"]) if b.get("src") else None
        if src and b["type"] == "video":
            poster = self.data_uri(b["poster"]) if b.get("poster") else None
            p = f' poster="{poster}"' if poster else ""
            return f'<figure><video controls preload="metadata" src="{src}"{p}></video>{cap}</figure>'
        if src:
            return f'<figure><img src="{src}" alt="{html.escape(self.t(b.get("alt") or b.get("caption")))}" loading="lazy">{cap}</figure>'
        ph = b.get("placeholder") or {"kind": "other", "description": b.get("src", "")}
        kind = self.L["kinds"].get(ph.get("kind"), self.L["kinds"]["other"])
        return (f'<figure><div class="placeholder"><span class="kind">{self.L["image"]} · {kind}</span>'
                f'<p>{self.inline(self.t(ph.get("description")))}</p></div>{cap}</figure>')

    def analysis(self, a, depth=3):
        h = f"h{min(depth, 6)}"
        out = [f'<div class="analysis" id="an-{html.escape(a["id"])}"><{h}>{self.inline(self.t(a["title"]))}</{h}>',
               f'<div class="finding">{self.paras(a["finding"])}</div>']
        if a.get("chart") and a.get("table"):
            out.append(self.chart(a["chart"], a["table"], a["title"]))
        elif a.get("table"):
            out.append(self.table(a["table"]))
        if a.get("method"):
            out.append(f'<p class="evidence">{self.L["method"]}: {html.escape(self.t(a["method"]))}</p>')
        out.append(self.evidence_note(a.get("evidence")) + "</div>")
        return "".join(out)

    # ---------------------------------------------------------------- report
    def sections(self, secs, depth=2):
        out, toc = [], []
        for s in secs:
            title = self.t(s.get("title"))
            sid = html.escape(s["id"])
            toc.append((depth, sid, title))
            inner, sub_toc = self.sections(s.get("children") or [], depth + 1)
            self.depth = depth
            body = self.blocks(s.get("blocks") or [])
            wide = " wide" if any(b["type"] in ("analysis", "chart", "table", "stats") for b in s.get("blocks") or []) else ""
            out.append(f'<section class="sec{wide}" id="{sid}"><h{depth}>{self.inline(title)}</h{depth}>{body}{inner}</section>')
            toc += sub_toc
        return "".join(out), toc

    def appendix(self):
        d, L, parts = self.doc, self.L, []
        if d.get("evidence"):
            rows = "".join(f'<tr id="ev-{html.escape(e["id"])}"><td>{html.escape(e["id"])}</td><td>{html.escape(e.get("participant", ""))}</td>'
                           f'<td>{html.escape(self.sources(e["source"]))}{(" · " + html.escape(self.t(e["locator"]))) if e.get("locator") else ""}</td></tr>'
                           for e in d["evidence"])
            parts.append(f'<h3>{L["evidenceIndex"]}</h3><div class="table-wrap"><table><thead><tr><th>ID</th>'
                         f'<th>{L["participant"]}</th><th>{L["source"]}</th></tr></thead><tbody>{rows}</tbody></table></div>')
        if d.get("glossary"):
            parts.append(f'<h3>{L["glossary"]}</h3><dl>' + "".join(
                f'<dt><strong>{html.escape(g["term"])}</strong></dt><dd>{self.inline(self.t(g.get("text")))}</dd>' for g in d["glossary"]) + "</dl>")
        if d.get("openQuestions"):
            parts.append(f'<h3>{L["openQuestions"]}</h3><ul>' + "".join(
                f"<li>{self.inline(self.t(q.get('text')))}</li>" for q in d["openQuestions"]) + "</ul>")
        return "".join(parts)

    def report(self):
        d, L = self.doc, self.L
        meta = d["meta"]
        secs = list(d.get("sections") or [])
        extra = self.appendix()
        if extra:
            if secs and secs[-1].get("role") == "appendix":
                body, toc = self.sections(secs)
                body = body[: body.rfind("</section>")] + extra + "</section>"
            else:
                body, toc = self.sections(secs)
                body += f'<section class="sec" id="appendix-auto"><h2>{L["appendix"]}</h2>{extra}</section>'
                toc.append((2, "appendix-auto", L["appendix"]))
        else:
            body, toc = self.sections(secs)
        title = self.t(meta["title"])
        nav = "".join(f'<a href="#{sid}" class="{"sub" if lvl > 2 else ""}">{html.escape(t)}</a>' for lvl, sid, t in toc if lvl <= 3)
        print_toc = "<ol>" + "".join(f"<li>{html.escape(t)}</li>" for lvl, sid, t in toc if lvl == 2) + "</ol>"
        logo = self.logo()
        authors = " · ".join(html.escape(self.t(a.get("name"))) for a in meta.get("authors") or [])
        dates = meta.get("dates") or {}
        fa = self.lang == "fa"
        when = (" تا " if fa else " – ").join(
            f'<bdi dir="ltr">{html.escape(str(x)).translate(FA_DIGITS) if fa else html.escape(str(x))}</bdi>'
            for x in (dates.get("start"), dates.get("end")) if x)
        cover = (f'<header class="cover">{"<div class=eyebrow>" + html.escape(self.t(meta.get("eyebrow"))) + "</div>" if meta.get("eyebrow") else ""}'
                 f'<h1>{self.inline(title)}</h1>'
                 + (f'<p class="headline">{self.inline(self.t(meta.get("headline")))}</p>' if meta.get("headline") else "")
                 + f'<div class="meta">{"<span>" + authors + "</span>" if authors else ""}{"<span class=num>" + when + "</span>" if when else ""}</div></header>')
        main = (f'<div class="progress"></div><div class="glow-wrap" aria-hidden="true"><div class="glow"></div></div>'
                f'<div class="topbar"><span class="title">{html.escape(title)}</span>'
                f'<button class="btn" data-open-toc>{L["menu"]}</button></div>'
                f'<div class="layout"><div class="scrim"></div><aside class="toc"><div class="brand">{logo}</div>'
                f'<nav aria-label="{L["contents"]}">{nav}</nav>'
                f'<div class="tools"><button class="btn" data-slides>{L["slides"]}</button></div></aside>'
                f'<main><nav class="print-toc"><h2>{L["contents"]}</h2>{print_toc}</nav>{cover}{body}</main></div>'
                f'{self.deck()}'
                f'<div class="lightbox"><img alt=""></div><footer class="credit">{CREDIT}</footer>')
        return self.page(title, main, ["base.css", "report.css"])

    # ---------------------------------------------------------------- slides
    def deck(self):
        """A 16:9 deck built from the content: cover, then the sections as slides. Heavy blocks (analysis,
        figure, stats, table, action plan, flow) get a slide each; text is grouped up to a slide's worth; quotes
        come three to a slide. The evidence index and glossary stay in the report."""
        d, slides = self.doc, []
        meta = d["meta"]

        def slide(kind, inner, title=None):
            head = f'<h2 class="s-title">{self.inline(title)}</h2>' if title else ""
            slides.append(f'<section class="slide {kind}">{head}<div class="s-body">{inner}</div></section>')

        authors = " · ".join(html.escape(self.t(a.get("name"))) for a in meta.get("authors") or [])
        slide("s-cover", f'<div class="s-logo">{self.logo()}</div><h1>{self.inline(self.t(meta["title"]))}</h1>'
              + (f'<p class="s-lead">{self.inline(self.t(meta.get("headline")))}</p>' if meta.get("headline") else "")
              + (f'<p class="s-meta">{authors}</p>' if authors else ""))

        def text_slides(title, chunks):
            page, size = [], 0
            for html_part, n in chunks:
                if page and size + n > 520:
                    slide("s-text", "".join(page), title)
                    page, size = [], 0
                page.append(html_part)
                size += n
            if page:
                slide("s-text", "".join(page), title)

        def walk(secs):
            for sec in secs:
                if sec.get("role") == "appendix" and not sec.get("blocks"):
                    continue
                title, chunks, quotes = self.t(sec.get("title")), [], []

                def flush():
                    nonlocal chunks, quotes
                    if chunks:
                        text_slides(title, chunks)
                    for i in range(0, len(quotes), 3):
                        slide("s-quotes", "".join(quotes[i:i + 3]), title)
                    chunks, quotes = [], []

                for b in sec.get("blocks") or []:
                    t = b["type"]
                    if t in ("paragraph", "callout", "list", "heading", "pending", "persona", "timeline"):
                        n = len(self.t(b.get("text"))) + sum(len(self.t(i)) for i in b.get("items") or [] if not isinstance(i, dict))
                        chunks.append((self.block(b, show_ev=False), max(n, 60)))
                    elif t == "quote":
                        quotes.append(self.block(b))
                    else:
                        flush()
                        if t == "analysis":
                            a = self.analyses[b["analysis"]]
                            vis = (self.chart(a["chart"], a["table"], a["title"], deck=True) if a.get("chart") and a.get("table")
                                   else self.table(a["table"]) if a.get("table") else "")
                            slide("s-analysis" + ("" if vis else " s-solo"),
                                  f'<div class="s-finding">{self.paras(a["finding"])}</div><div class="s-visual">{vis}</div>',
                                  self.t(a["title"]))
                        elif t in ("image", "video"):
                            slide("s-figure", self.figure(b), title)
                        elif t == "chart":
                            slide("s-figure", self.chart(b["chart"], b["table"], b.get("caption"), deck=True), title)
                        elif t in ("table", "actionPlan"):
                            rows = b["rows"] if t == "table" else b["items"]
                            for i in range(0, max(len(rows), 1), 6):
                                part = dict(b, **({"rows": rows[i:i + 6]} if t == "table" else {"items": rows[i:i + 6]}))
                                slide("s-table", self.block(part, show_ev=False), title)
                        else:
                            slide("s-" + t, self.block(b, show_ev=False), title)
                flush()
                walk(sec.get("children") or [])

        walk(d.get("sections") or [])
        if d.get("openQuestions"):
            text_slides(self.L["openQuestions"], [("<ul>" + "".join(f"<li>{self.inline(self.t(q.get('text')))}</li>"
                                                                     for q in d["openQuestions"]) + "</ul>", 300)])
        slide("s-end", f'<h1>{self.inline(self.t(meta["title"]))}</h1><p class="s-meta">{CREDIT}</p>')
        L = self.L
        return (f'<div class="deck" aria-hidden="true"><div class="stage">{"".join(slides)}</div>'
                f'<div class="deck-bar"><div class="deck-progress"><span></span></div>'
                f'<button class="btn" data-prev aria-label="{L["prev"]}">{L["prev"]}</button><span class="count"></span>'
                f'<button class="btn" data-next aria-label="{L["next"]}">{L["next"]}</button>'
                f'<button class="btn" data-exit-slides>{L["exit"]}</button></div></div>')

    # ---------------------------------------------------------------- blog
    def blog(self):
        d, b = self.doc, self.doc["blog"]
        self.article = True
        meta = d["meta"]
        title = self.t(b["title"])
        authors = " · ".join(html.escape(self.t(a.get("name"))) for a in meta.get("authors") or [])
        parts = []
        for s in b.get("sections") or []:
            if s.get("title"):
                parts.append(f'<h2 id="{html.escape(s["id"])}">{self.inline(self.t(s["title"]))}</h2>')
            parts.append(self.blocks(s.get("blocks") or []))
        head = (f'<header>{self.logo("logo")}<h1>{self.inline(title)}</h1>'
                + (f'<p class="dek">{self.inline(self.t(b.get("dek")))}</p>' if b.get("dek") else "")
                + (f'<p class="byline">{authors}</p>' if authors else "") + "</header>")
        main = (f'<div class="glow-wrap" aria-hidden="true"><div class="glow"></div></div><article class="article">{head}{"".join(parts)}</article>'
                f'<div class="lightbox"><img alt=""></div><footer class="credit">{CREDIT}</footer>')
        return self.page(title, main, ["base.css", "blog.css"])

    # ---------------------------------------------------------------- page shell
    def logo(self, cls=""):
        rel = (self.doc["meta"].get("brand") or {}).get("logo")
        uri = self.data_uri(rel) if rel else None
        return f'<img class="{cls}" src="{uri}" alt="logo">' if uri else ""

    def page(self, title, body, styles):
        brand = self.doc["meta"].get("brand") or {}
        tokens = theme.css(brand.get("primary"))
        font_face, display = brand_font(self.dir)
        with open(os.path.join(VENDOR, "vazirmatn", "Vazirmatn-Variable.woff2"), "rb") as f:
            vazir = "data:font/woff2;base64," + base64.b64encode(f.read()).decode()
        css = "".join(_read(os.path.join(TEMPLATES, s)) for s in styles)
        css = css.replace("{{VAZIRMATN}}", vazir).replace("{{BRAND_FONT_FACE}}", font_face).replace("{{FONT_STACK}}", BODY_STACK).replace("{{DISPLAY_STACK}}", display)
        data = "".join(f'<script type="application/json" id="{cid}-data">{_json(spec)}</script>' for cid, spec in self.charts)
        scripts = ""
        if self.charts:
            scripts += f"<script>{_read(os.path.join(VENDOR, 'echarts', 'echarts.min.js'))}</script>"
        scripts += f"<script>{_read(os.path.join(TEMPLATES, 'report.js'))}</script>"
        d = "rtl" if self.lang in RTL else "ltr"
        return (f'<!doctype html><html lang="{self.lang}" dir="{d}"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<meta name="generator" content="Reporch"><title>{html.escape(title)}</title>'
                f'<style>{tokens}{css}</style></head><body>{body}{data}{scripts}</body></html>')


BODY_STACK = '"Vazirmatn", system-ui, -apple-system, "Segoe UI", sans-serif'


def brand_font(project_dir):
    """A brand font (e.g. Lahzeh) is used only when the user put its files in <project>/assets/fonts/, and only
    for titles, subtitles and big numbers: returns (@font-face rules, the display stack). Body text stays Vazirmatn."""
    stack = BODY_STACK
    folder = os.path.join(project_dir, "assets", "fonts")
    if not os.path.isdir(folder):
        return "", stack
    faces, family = [], "ReporchBrand"
    for name in sorted(os.listdir(folder)):
        ext = os.path.splitext(name)[1].lower()
        if ext not in (".woff2", ".woff", ".ttf", ".otf"):
            continue
        weight = _weight(name)
        with open(os.path.join(folder, name), "rb") as f:
            uri = f"data:font/{ext[1:]};base64," + base64.b64encode(f.read()).decode()
        faces.append(f'@font-face {{ font-family: "{family}"; src: url("{uri}"); font-weight: {weight}; font-display: swap; }}')
    if not faces:
        return "", stack
    return "\n".join(faces), f'"{family}", ' + stack


def _source_names(project_dir):
    """Map Reporch's working copies (inputs/clean/x.tables.json) back to the file the user gave (x.xlsx)."""
    originals = {}
    idx = os.path.join(project_dir or "", "inputs", "index.json")
    if os.path.exists(idx):
        with open(idx, encoding="utf-8") as f:
            originals = {os.path.splitext(e["file"])[0]: e["file"] for e in json.load(f)}

    def name(src):
        base = os.path.basename(src)
        for suffix in (".tables.json", ".txt"):
            if src.startswith("inputs/") and base.endswith(suffix) and base[: -len(suffix)] in originals:
                return originals[base[: -len(suffix)]]
        return base if src.startswith("inputs/") else src
    return name


def _weight(name):
    n = name.lower()
    for word, w in (("thin", 100), ("extralight", 200), ("ultralight", 200), ("light", 300), ("medium", 500),
                    ("semibold", 600), ("demibold", 600), ("extrabold", 800), ("ultrabold", 800), ("black", 900),
                    ("heavy", 900), ("bold", 700)):
        if word in n.replace("-", "").replace("_", ""):
            return w
    return 400


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


# -------------------------------------------------------------------- markdown

def markdown(doc, lang, kind="report"):
    r = Renderer(doc, lang, "")
    t = r.t
    out = []

    def blocks(bs):
        for b in bs:
            ty = b["type"]
            if ty in ("paragraph", "heading", "callout", "pending"):
                prefix = {"heading": "### ", "callout": "> ", "pending": "> **" + r.L["pending"] + ":** "}.get(ty, "")
                out.append(prefix + t(b["text"]))
            elif ty == "quote":
                out.append(f"> {t(b['text'])}\n> — {b['participant']}")
            elif ty == "list":
                out.extend(("1. " if b.get("ordered") else "- ") + t(i) for i in b["items"])
            elif ty == "stats":
                out.extend(f"- **{t(i.get('value'))}** {t(i.get('label'))}" for i in b["items"])
            elif ty in ("table", "chart"):
                out.append(md_table(b if ty == "table" else b["table"], r))
            elif ty == "analysis":
                a = r.analyses[b["analysis"]]
                out.append(f"### {t(a['title'])}\n\n{t(a['finding'])}")
                if a.get("table"):
                    out.append(md_table(a["table"], r))
            elif ty in ("image", "video"):
                ph = b.get("placeholder")
                out.append(f"![{t(b.get('caption'))}]({b['src']})" if b.get("src")
                           else f"> **{r.L['image']} ({ph.get('kind')}):** {t(ph.get('description'))}")
            elif ty == "persona":
                out.append(f"**{t(b['name'])}**: {t(b['text'])}")
            elif ty == "flow":
                out.append(" → ".join(t(s.get("text")) for s in b["steps"]))
            elif ty == "timeline":
                out.extend(f"- **{i.get('date')}** {t(i.get('text'))}" for i in b["items"])
            elif ty == "actionPlan":
                out.extend(f"- {t(i.get('text'))} ({t(i.get('priority'))})" for i in b["items"])
            out.append("")

    def secs(ss, depth):
        for s in ss:
            out.append("#" * depth + " " + t(s.get("title")) + "\n")
            blocks(s.get("blocks") or [])
            secs(s.get("children") or [], depth + 1)

    if kind == "blog":
        b = doc["blog"]
        out += [f"# {t(b['title'])}", "", f"*{t(b.get('dek'))}*" if b.get("dek") else "", ""]
        for s in b.get("sections") or []:
            if s.get("title"):
                out.append(f"## {t(s['title'])}\n")
            blocks(s.get("blocks") or [])
    else:
        out += [f"# {t(doc['meta']['title'])}", ""]
        secs(doc.get("sections") or [], 2)
    out.append(f"\n---\n<sub>{CREDIT}</sub>\n")
    return "\n".join(out)


def md_table(table, r):
    fmt = table.get("format") or {}
    cols = table["columns"]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    lines += ["| " + " | ".join(html.unescape(r.num(v, fmt.get(c))) for c, v in zip(cols, row)) + " |" for row in table["rows"]]
    return "\n".join(lines)


def build(doc, project_dir, markdown_too=False):
    """Write out/report.<lang>.html and out/blog.<lang>.html (and .md) for every language. Returns paths."""
    out_dir = os.path.join(project_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for lang in doc["meta"]["languages"]:
        pages = {"report": Renderer(doc, lang, project_dir).report()}
        if doc.get("blog"):
            pages["blog"] = Renderer(doc, lang, project_dir).blog()
        for name, page in pages.items():
            path = os.path.join(out_dir, f"{name}.{lang}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(page)
            written.append(path)
            if markdown_too:
                md = os.path.join(out_dir, f"{name}.{lang}.md")
                with open(md, "w", encoding="utf-8") as f:
                    f.write(markdown(doc, lang, name))
                written.append(md)
    return written
