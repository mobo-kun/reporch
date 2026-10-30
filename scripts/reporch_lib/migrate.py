"""Migrate an existing report (HTML, or PDF when pypdf is installed) into a Reporch project without losing
anything (R1).

1. `inventory(path)`: every section, heading, paragraph, list item, table, chart (Chart.js configs, including
   charts built by factory functions), quote, stat card and image, in the original order.
2. `draft(inv, …)`: a content.json draft. Nothing is dropped: an element Reporch can't map becomes a
   paragraph. Section roles are guessed from titles; anything uncertain becomes a question.
3. `lossless(inv, doc)`: every text unit and number of the original must be in the draft. Build refuses a
   migrated project until it is 100%.
"""
import base64
import json
import os
import re
import unicodedata
from html.parser import HTMLParser

BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "div", "button", "label", "caption",
         "figcaption", "blockquote", "summary", "dt", "dd", "article", "aside", "footer", "figure"}
TEXT_LEAF = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "figcaption", "caption", "dt", "dd"}
SKIP = {"script", "style", "nav", "noscript", "template"}   # never skip <header>: covers live there
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "col"}
# Containers never pass text upward: loose text inside them is recorded as its own block (B-012).
CONTAINER = {"html", "body", "main", "header", "section", "nav", "ul", "ol", "dl", "form", "table", "tbody",
             "thead", "tfoot", "tr", "details", "fieldset", "center", "font", "label"}
SKIP_CLASS = re.compile(r"\b(toc|sidebar|drawer|hamburger|menu|scroll-prog|progress|slide-num|overlay)\b", re.I)

ROLE_WORDS = [
    ("summary", r"summary|overview|tl;?dr|executive|key findings|خلاصه|چکیده|جمع‌بندی|جمع بندی"),
    ("context", r"intro|context|background|about|goal|why|مقدمه|زمینه|پیشینه|هدف"),
    ("method", r"method|approach|process|setup|task|روش|متد|فرایند|فرآیند|تسک"),
    ("participants", r"participant|persona|user group|sample|شرکت|پرسونا|نمونه"),
    ("problem", r"problem|pain|issue|finding|insight|quant|qual|stat|مسئله|مشکل|یافته|کمی|کیفی|آمار|بینش"),
    ("solution", r"solution|design|redesign|proposal|راه‌حل|راه حل|طراحی|پیشنهاد طراحی"),
    ("result", r"result|outcome|impact|metric|نتیجه|نتایج|اثر|تأثیر"),
    ("actionPlan", r"action|recommend|next step|roadmap|اقدام|پیشنهاد|گام بعد|توصیه|action plan"),
    ("limitations", r"limitation|caveat|confidence|محدودیت|بازه"),
    ("appendix", r"appendix|raw data|session|پیوست|ضمیمه|جلسه"),
]


class _Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip = [], 0
        self.sections, self.section = [], None
        self.table, self.row = None, None

    def _sec(self):
        if self.section is None:
            self.section = {"id": None, "items": []}
            self.sections.append(self.section)
        return self.section

    def _add(self, item):
        self._sec()["items"].append(item)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in VOID:
            if tag == "br" and self.stack:
                self.stack[-1][2].append("\n")
            elif tag == "img" and not self.skip:
                self._add({"kind": "image", "src": a.get("src", ""), "alt": a.get("alt", "")})
            return
        cls = a.get("class", "") + " " + a.get("id", "")
        skipper = tag in SKIP or bool(SKIP_CLASS.search(cls))
        if skipper or self.skip:
            self.skip += skipper
            self.stack.append([tag, a, [], skipper])
            return
        if tag == "section" or (tag == "div" and re.search(r"\bslide\b", a.get("class", ""))):
            self.section = {"id": a.get("id"), "items": []}
            self.sections.append(self.section)
        elif tag == "table":
            self.table = {"kind": "table", "id": a.get("id"), "rows": []}
            self._add(self.table)
        elif tag == "tr" and self.table is not None:
            self.row = []
            self.table["rows"].append(self.row)
        elif tag == "canvas":
            self._add({"kind": "chart", "canvas": a.get("id")})
        elif tag in ("video", "iframe", "svg"):
            self._add({"kind": tag, "src": a.get("src", "")})
        self.stack.append([tag, a, [], False])

    def handle_endtag(self, tag):
        while self.stack:
            t, a, parts, skipper = self.stack.pop()
            if skipper:
                self.skip -= 1
            elif not self.skip:
                self._close(t, a, parts)
            if t == tag:
                break

    def _close(self, t, a, parts):
        text = re.sub(r"[ \t\r\f\v]+", " ", "".join(parts))
        text = re.sub(r"\s*\n\s*", "\n", text).strip()
        if t in ("td", "th"):
            if self.row is not None:
                self.row.append(re.sub(r"\s+", " ", text))
            return
        if t == "tr":
            self.row = None
        elif t == "table":
            self.table = None
        if t in BLOCK or t in CONTAINER:
            # Blocks and containers record their own text (children that are blocks were recorded already).
            if text:
                self._add({"kind": "text", "tag": t, "class": a.get("class", ""), "text": text})
            return
        if self.stack and text:                       # inline elements (span, a, strong…) join their parent
            self.stack[-1][2].append(text)

    def handle_data(self, data):
        if not self.skip and self.stack:
            self.stack[-1][2].append(data)


# ------------------------------------------------------------------ Chart.js configs

def _balanced(s, i):
    pairs = {"{": "}", "[": "]", "(": ")"}
    depth, quote = 0, None
    for j in range(i, len(s)):
        c = s[j]
        if quote:
            if c == quote and s[j - 1] != "\\":
                quote = None
        elif c in "'\"`":
            quote = c
        elif c in pairs:
            depth += 1
        elif c in pairs.values():
            depth -= 1
            if depth == 0:
                return s[i:j + 1]
    return s[i:]


def _js_array(text):
    """Parse a simple JS array literal (strings, numbers, nested arrays) into Python, or None."""
    if not text or not text.startswith("["):
        return None
    t = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: json.dumps(m.group(1).replace("\\'", "'")), text)
    t = re.sub(r",\s*([\]}])", r"\1", t)
    try:
        return json.loads(t)
    except ValueError:
        return None


def _summary(cfg, canvas, defs):
    typ = re.search(r"type\s*:\s*'([^']+)'", cfg)
    lab = re.search(r"labels\s*:\s*(\[|\w+)", cfg)
    labels = None
    if lab:
        labels = _balanced(cfg, lab.start(1)) if lab.group(1) == "[" else defs.get(lab.group(1), lab.group(1))
    data = [(_balanced(cfg, d.start(1)) if d.group(1) == "[" else defs.get(d.group(1), d.group(1)))
            for d in re.finditer(r"\bdata\s*:\s*(\[|\w+)", cfg)]
    return {"canvas": canvas, "type": typ.group(1) if typ else None, "labels": labels,
            "datasetLabels": re.findall(r"\blabel\s*:\s*'([^']*)'", cfg), "data": data}


def charts(html):
    defs = {m.group(1): _balanced(html, m.end() - 1)
            for m in re.finditer(r"\b(?:const|let|var)\s+(\w+)\s*=\s*\[", html)}
    out = []
    for f in re.finditer(r"function\s+(\w+)\s*\(([^)]*)\)\s*\{", html):
        body = _balanced(html, f.end() - 1)
        m = re.search(r"new Chart\(\s*document\.getElementById\((\w+)\)\s*,\s*", body)
        if not m:
            continue
        params = [x.strip() for x in f.group(2).split(",")]
        cfg = _balanced(body, m.end())
        for call in re.finditer(re.escape(f.group(1)) + r"\(\s*'([^']+)'\s*,", html):
            args = _balanced(html, call.start() + len(f.group(1)))
            parts = [x.strip() for x in re.split(r",(?![^\[]*\])", args[1:-1])]
            local = dict(defs)
            for name, val in zip(params, parts):
                local[name] = defs.get(val, val)
            out.append(_summary(cfg, call.group(1), local))
    for m in re.finditer(r"new Chart\(\s*document\.getElementById\('([^']+)'\)\s*,\s*", html):
        out.append(_summary(_balanced(html, m.end()), m.group(1), defs))
    return out


# ------------------------------------------------------------------ inventory

def inventory(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".html", ".htm"):
        with open(path, encoding="utf-8", errors="replace") as f:
            html = f.read()
        p = _Inventory()
        p.feed(html[html.find("<body"):] if "<body" in html else html)
        secs = [s for s in p.sections if s["items"]]
        title = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        lang = re.search(r"<html[^>]*\blang=\"([a-z]{2})", html, re.I)
        return {"source": os.path.basename(path), "format": "html", "title": title.group(1).strip() if title else None,
                "lang": lang.group(1).lower() if lang else None, "sections": secs, "charts": charts(html)}
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("Reading PDFs needs pypdf. Ask the user, then: python3 -m pip install pypdf. "
                               "Or read the PDF with your own tools and build the inventory by hand.")
        reader = PdfReader(path)
        secs = []
        for n, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            items, buf = [], []
            for line in text.splitlines():           # PDF text has no paragraph marks: join lines up to a sentence end
                if line.strip():
                    buf.append(line.strip())
                if buf and (not line.strip() or re.search(r"[.!?؟:]\s*$", line)):
                    items.append({"kind": "text", "tag": "p", "class": "", "text": " ".join(buf)})
                    buf = []
            if buf:
                items.append({"kind": "text", "tag": "p", "class": "", "text": " ".join(buf)})
            images = len(getattr(page, "images", []) or [])
            items += [{"kind": "image", "src": f"pdf-page-{n}-image-{i + 1}", "alt": ""} for i in range(images)]
            if items:
                secs.append({"id": f"page-{n}", "items": items})
        return {"source": os.path.basename(path), "format": "pdf", "title": None, "lang": None,
                "sections": secs, "charts": []}
    raise ValueError("migrate reads .html or .pdf reports")


def units(inv):
    """Every piece of content in the original, as (where, text) pairs, for the lossless check."""
    out = []
    for i, s in enumerate(inv["sections"]):
        for it in s["items"]:
            if it["kind"] == "text":
                out.append((f"section {i + 1}", it["text"]))
            elif it["kind"] == "table":
                out += [(f"section {i + 1} table", c) for r in it["rows"] for c in r if c.strip()]
    for c in inv["charts"]:
        for v in (_js_array(c["labels"]) or []):
            out.append((f"chart {c['canvas']} label", str(v)))
        for d in c["data"]:
            for v in _flat(_js_array(d) or []):
                if v is not None:                       # null = no bar in the original, not content
                    out.append((f"chart {c['canvas']} data", _num(v)))
    return out


def _flat(x):
    for v in x:
        if isinstance(v, list):
            yield from _flat(v)
        else:
            yield v


def _num(v):
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


# ------------------------------------------------------------------ draft

def guess_role(title):
    """The role whose keyword appears earliest in the title ("Findings by task" → problem, not method)."""
    t = (title or "").lower()
    hits = [(m.start(), i, role) for i, (role, rx) in enumerate(ROLE_WORDS) for m in [re.search(rx, t)] if m]
    return min(hits)[2] if hits else None


def _script(text):
    fa = len(re.findall(r"[؀-ۿ]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    return "fa" if fa > lat else "en"


def draft(inv, lang, slug, project_dir=None):
    """Build a content.json draft in the original order. Returns (doc, questions)."""
    questions, sections, images = [], [], 0
    charts_by_canvas = {c["canvas"]: c for c in inv["charts"]}
    T = lambda s: {lang: s}
    participants = set()

    for i, s in enumerate(inv["sections"]):
        items = list(s["items"])
        title = None
        for k, it in enumerate(items):
            if it["kind"] == "text" and it["tag"] in ("h1", "h2"):
                title = items.pop(k)["text"]
                break
        blocks, stat, lst = [], None, None
        for it in items:
            if it["kind"] != "text":
                stat = lst = None
            if it["kind"] == "text":
                cls, tag, text = it["class"].lower(), it["tag"], it["text"]
                participants |= set(re.findall(r"\bP\d{2,}\b", text))
                if re.search(r"(label|lbl)\b", cls) and not re.search(r"chart-label", cls):
                    stat = {"label": T(text)}
                    blocks.append({"type": "stats", "items": [stat]}) if not (blocks and blocks[-1]["type"] == "stats") \
                        else blocks[-1]["items"].append(stat)
                    continue
                if stat is not None and re.search(r"(val|value|num)\b", cls) and "value" not in stat:
                    stat["value"] = T(text)
                    continue
                if stat is not None and re.search(r"(note|sub|hint)\b", cls) and "note" not in stat:
                    stat["note"] = T(text)
                    continue
                stat = None
                if tag == "li":
                    if lst is None:
                        lst = {"type": "list", "items": []}
                        blocks.append(lst)
                    lst["items"].append(T(text))
                    continue
                lst = None
                if tag in ("h3", "h4", "h5", "h6", "h1", "h2"):
                    blocks.append({"type": "heading", "text": T(text)})
                elif tag == "blockquote" or "quote" in cls:
                    pid = re.search(r"\bP\d{2,}\b", text)
                    blocks.append({"type": "quote", "text": T(text), "participant": pid.group(0) if pid else "P??",
                                   "evidence": ["M1"], "_check": "participant and original wording"})
                elif re.search(r"info|warn|crit|callout|alert|note-box", cls):
                    tone = "critical" if "crit" in cls else "warn" if "warn" in cls else "info"
                    blocks.append({"type": "callout", "tone": tone, "text": T(text)})
                else:
                    blocks.append({"type": "paragraph", "text": T(text)})
            elif it["kind"] == "table":
                rows = [r for r in it["rows"] if any(c.strip() for c in r)]
                if rows:
                    width = max(len(r) for r in rows)
                    rows = [r + [""] * (width - len(r)) for r in rows]
                    blocks.append({"type": "table", "columns": rows[0], "rows": rows[1:]})
            elif it["kind"] == "chart":
                c = charts_by_canvas.get(it["canvas"])
                labels = _js_array(c["labels"]) if c else None
                data = [_js_array(d) for d in c["data"]] if c else []
                data = [d for d in data if d is not None]
                if labels and data and all(len(d) == len(labels) for d in data):
                    names = (c["datasetLabels"] + [f"series {n + 1}" for n in range(len(data))])[:len(data)]
                    names = [n or f"series {k + 1}" for k, n in enumerate(names)]
                    cols = ["label"] + names
                    rows = [[labels[r]] + [d[r] if not isinstance(d[r], list) else "–".join(map(_num, d[r])) for d in data]
                            for r in range(len(labels))]
                    kind = {"doughnut": "doughnut", "pie": "doughnut", "line": "line"}.get(c["type"], "bar")
                    simple = all(isinstance(d[r], (int, float)) and not isinstance(d[r], bool) for d in data for r in range(len(labels)))
                    rows = [["" if v is None else v for v in row] for row in rows]
                    blk = {"type": "chart", "caption": T(it["canvas"] or "chart"), "table": {"columns": cols, "rows": rows},
                           "chart": {"kind": kind if simple else "bar", "x": "label", "series": names if simple else names[:1]}}
                    blocks.append(blk if simple else {"type": "table", "columns": cols, "rows": rows})
                else:
                    blocks.append({"type": "pending", "text": T(f"Chart {it['canvas']}: its data could not be read. Ask the designer for the numbers.")})
                    questions.append(f"Chart '{it['canvas']}' in section {i + 1}: what are its numbers?")
            elif it["kind"] == "image":
                images += 1
                src = _save_image(it["src"], project_dir, images) if project_dir else None
                if src:
                    blocks.append({"type": "image", "src": src, "caption": T(it["alt"] or ""), "alt": T(it["alt"] or "")})
                else:
                    blocks.append({"type": "image", "caption": T(it["alt"] or ""), "placeholder": {
                        "kind": "other", "description": T(f"The original image {it['src'][:80] or images} from the old report. Ask the designer for the original file.")}})
            else:
                blocks.append({"type": "pending", "text": T(f"A {it['kind']} element ({it.get('src', '')}) was in the original.")})
        role = guess_role(title)
        sections.append({"id": s["id"] or f"s{i + 1}", "role": role or "result", "title": T(title or f"Section {i + 1}"),
                         "blocks": blocks or [{"type": "pending", "text": T("Empty section in the original.")}],
                         "_originalIndex": i, "_roleGuessed": role is not None})
        if role is None:
            questions.append(f"Section {i + 1} '{title}': which part of the outline is it (problem, solution, result, …)?")

    order = [s["role"] for s in sections]
    from .content import ROLES, REQUIRED_ROLES
    if [ROLES.index(r) for r in order] != sorted(ROLES.index(r) for r in order):
        questions.append("The original order doesn't follow the outline (summary → problem → solution → result). "
                         "Keep the original order by nesting sections, or move them? (Moving needs your OK.)")
    for r in REQUIRED_ROLES:
        if r not in order:
            questions.append(f"The original has no '{r}' section. What should it say, or should it stay 'still needed'?")
    if any(b.get("participant") == "P??" for s in sections for b in s["blocks"]):
        questions.append("Some quotes have no participant id. Who said each one?")
    if images:
        questions.append(f"The original has {images} image(s). Can you give the original files (better quality than copies)?")

    doc = {
        "schema": "reporch/content@1",
        "meta": {"title": T(inv["title"] or slug), "slug": slug, "authors": [], "languages": [lang]},
        "participants": [{"id": p} for p in sorted(participants)],
        "evidence": [{"id": "M1", "source": f"inputs/original/{inv['source']}", "locator": T("original report")}],
        "analyses": [],
        "sections": sections,
        "_migration": {"source": inv["source"], "questions": questions},
    }
    return doc, questions


def _save_image(src, project_dir, n):
    m = re.match(r"data:image/(\w+);base64,(.+)", src or "", re.S)
    if not m:
        return None
    ext = {"jpeg": "jpg", "svg+xml": "svg"}.get(m.group(1), m.group(1))
    folder = os.path.join(project_dir, "assets", "images")
    os.makedirs(folder, exist_ok=True)
    name = f"migrated-{n}.{ext}"
    with open(os.path.join(folder, name), "wb") as f:
        f.write(base64.b64decode(m.group(2)))
    return f"assets/images/{name}"


# ------------------------------------------------------------------ lossless check

_FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬", "01234567890123456789.,")


def _norm(s):
    s = unicodedata.normalize("NFC", str(s)).translate(_FA).replace("‌", "").replace("ي", "ی").replace("ك", "ک")
    s = re.sub(r"[«»\"'“”‘’()\[\]،,:؛;.!?؟—–\-/|*_#`•·]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if not k.startswith("_"):
                yield from _strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield _num(o)


def lossless(inv, doc):
    corpus = " " + " ".join(_norm(x) for x in _strings({k: v for k, v in doc.items() if k != "_migration"})) + " "
    missing = []
    total = 0
    for where, text in units(inv):
        n = _norm(text)
        if not n:
            continue
        total += 1
        if f" {n} " not in corpus and n not in corpus:
            missing.append({"where": where, "text": text[:120]})
    return {"units": total, "kept": total - len(missing), "missing": missing, "complete": not missing}
