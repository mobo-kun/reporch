"""Checks before delivery (modules/qa.md). Reports go public, so problems are loud.

Static checks need only the standard library. Layout checks (phone width, charts drawn) and PDF checks
run when Playwright is available; otherwise they are listed as skipped, never as passed.
"""
import glob
import json
import os
import re
import unicodedata

from . import content, theme

FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬", "01234567890123456789.,")
ARABIC_SCRIPT = re.compile(r"[؀-ۿ]")
ARABIC_LETTERS = re.compile(r"[يك]")          # Arabic yeh and kaf in Persian text
NUMBER = re.compile(r"\d+(?:\.\d+)?")
MAX_BYTES = 40 * 1024 * 1024
# Numbers a finding may use without a table cell: confidence levels, the SUS benchmark, scale ends.
STANDARD = {"95", "90", "99", "68", "100", "0", "1", "5", "7", "10"}


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, check, where, message):
        self.items.append({"level": level, "check": check, "where": where, "message": message})

    def errors(self):
        return [i for i in self.items if i["level"] == "error"]

    def summary(self):
        by = {}
        for i in self.items:
            by[i["level"]] = by.get(i["level"], 0) + 1
        return by


def _norm(text):
    text = unicodedata.normalize("NFC", text).translate(FA_DIGITS).replace("‌", "")
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("«", '"').replace("»", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def _numbers(text):
    return set(NUMBER.findall(_norm(text)))


def _table_numbers(table):
    out = set()
    for row in table.get("rows") or []:
        for v in row:
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                raw = repr(v)
                out.add(raw.rstrip("0").rstrip(".") if "." in raw and "e" not in raw else raw)
                for x in (v, v * 100):
                    for d in (0, 1, 2):
                        out.add(f"{round(x + 1e-9, d):.{d}f}".rstrip("0").rstrip(".") or "0")
            else:
                out |= _numbers(str(v))
    return out


def check_numbers(doc, rep):
    """Every number in an analysis finding should come from its table (or be a standard constant)."""
    for a in doc.get("analyses") or []:
        values = {"rows": [[v for v in (a.get("values") or {}).values() if isinstance(v, (int, float))]]}
        known = _table_numbers(a.get("table") or {}) | _table_numbers(values) | STANDARD
        for lang, text in (a.get("finding") or {}).items():
            if not isinstance(text, str):
                continue
            missing = sorted(n for n in _numbers(text) if n not in known and n.lstrip("0") not in known)
            if missing:
                rep.add("warning", "numbers", f"analyses.{a['id']}.finding.{lang}",
                        "numbers not found in the analysis table: " + ", ".join(missing) + " (confirm their source)")


def check_quotes(doc, project_dir, rep):
    """A quote must appear word for word in the cleaned inputs (in one of its languages)."""
    corpus = ""
    for path in glob.glob(os.path.join(project_dir, "inputs", "clean", "*.txt")) + \
            glob.glob(os.path.join(project_dir, "inputs", "clean", "*.md")) + \
            glob.glob(os.path.join(project_dir, "inputs", "clean", "*.csv")):
        with open(path, encoding="utf-8") as f:
            corpus += " " + _norm(f.read())
    answers = os.path.join(project_dir, "answers.md")
    if os.path.exists(answers):
        with open(answers, encoding="utf-8") as f:
            corpus += " " + _norm(f.read())

    def blocks():
        for s in _walk(doc.get("sections") or []):
            yield from s.get("blocks") or []
        for s in (doc.get("blog") or {}).get("sections") or []:
            yield from s.get("blocks") or []
    for b in blocks():
        if b.get("type") != "quote":
            continue
        texts = [t for t in (b.get("text") or {}).values() if isinstance(t, str)]
        if not any(_norm(t).strip('"') in corpus for t in texts):
            rep.add("error", "quotes", b.get("participant", "?"),
                    f"quote not found word for word in the inputs: {texts[0][:60]!r}")


def _walk(secs):
    for s in secs:
        yield s
        yield from _walk(s.get("children") or [])


def check_outputs(doc, project_dir, rep):
    out = os.path.join(project_dir, "out")
    for lang in doc["meta"]["languages"]:
        for kind in ("report", "blog"):
            path = os.path.join(out, f"{kind}.{lang}.html")
            if not os.path.exists(path):
                rep.add("error", "outputs", path, "missing: run build")
                continue
            size = os.path.getsize(path)
            if size > MAX_BYTES:
                rep.add("error", "size", path, f"{size / 1048576:.1f} MB is over the 40 MB limit (compress images or video)")
            with open(path, encoding="utf-8") as f:
                page = f.read()
            if re.search(r'<(script|link|img|video|source)[^>]+(src|href)="(https?:)?//', page):
                rep.add("error", "offline", path, "loads a file from the network; outputs must work offline")
            body = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
            visible = re.sub(r"<[^>]+>", " ", body)
            if lang != "fa" and lang not in ("ar", "ur", "ps") and ARABIC_SCRIPT.search(visible):
                rep.add("error", "language", path, "contains Persian/Arabic script in a non-Persian document")
            if lang == "fa":
                if 'dir="rtl"' not in page[:300]:
                    rep.add("error", "rtl", path, "Persian document is not right-to-left")
                bad = ARABIC_LETTERS.findall(visible)
                if bad:
                    rep.add("error", "orthography", path, f"{len(bad)} Arabic ي/ك characters (use Persian ی/ک)")
            if "Made with Reporch by Mobo" not in page:
                rep.add("error", "credit", path, "footer credit missing")
            n = page.count('class="placeholder"')
            if n:
                rep.add("warning", "images", path, f"{n} image placeholder(s) still waiting for files")


def check_theme(doc, rep):
    primary = (doc["meta"].get("brand") or {}).get("primary")
    if primary:
        try:
            step = theme.text_step(primary)
        except ValueError as e:
            rep.add("error", "brand", "meta.brand.primary", str(e))
            return
        ratio = theme.contrast(theme.scale(primary)[step], "#FFFFFF")
        if ratio < 4.5:
            rep.add("error", "contrast", "meta.brand.primary", f"no shade reaches 4.5:1 on white ({ratio:.2f}:1)")


def check_layout(project_dir, doc, rep, width=360):
    """Phone width, sideways scroll and chart drawing, in a real browser (needs Playwright)."""
    from . import pdf
    if not pdf.available():
        rep.add("skipped", "layout", "out/", "Playwright not installed: phone-width and chart checks not run")
        return
    from playwright.sync_api import sync_playwright
    import pathlib
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for lang in doc["meta"]["languages"]:
                for kind in ("report", "blog"):
                    path = os.path.join(project_dir, "out", f"{kind}.{lang}.html")
                    if not os.path.exists(path):
                        continue
                    page = browser.new_page(viewport={"width": width, "height": 800})
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(pathlib.Path(os.path.abspath(path)).as_uri() + "?print")
                    page.wait_for_function("window.__REPORCH_CHARTS_READY__ === true", timeout=30000)
                    m = page.evaluate("""() => ({sw: document.documentElement.scrollWidth, w: innerWidth,
                        charts: document.querySelectorAll('.chart').length, drawn: document.querySelectorAll('.chart svg').length})""")
                    if m["sw"] > m["w"] + 1:
                        rep.add("error", "layout", path, f"scrolls sideways at {width} px ({m['sw']} px wide)")
                    if m["drawn"] < m["charts"]:
                        rep.add("error", "charts", path, f"{m['charts'] - m['drawn']} chart(s) not drawn")
                    for e in errors:
                        rep.add("error", "script", path, e)
                    page.close()
        finally:
            browser.close()


def check_pdfs(project_dir, doc, rep):
    for lang in doc["meta"]["languages"]:
        path = os.path.join(project_dir, "out", f"report.{lang}.pdf")
        if not os.path.exists(path):
            rep.add("skipped", "pdf", path, "no PDF yet (run pdf, or print from Chrome)")
            continue
        with open(path, "rb") as f:
            data = f.read()
        pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
        if not data.startswith(b"%PDF") or pages == 0:
            rep.add("error", "pdf", path, "not a valid PDF")
        elif os.path.getsize(path) > MAX_BYTES:
            rep.add("error", "size", path, "over 40 MB")
        else:
            rep.add("info", "pdf", path, f"{pages} pages")


def run(project_dir, layout=True):
    with open(os.path.join(project_dir, "content.json"), encoding="utf-8") as f:
        doc = json.load(f)
    rep = Report()
    for p in content.validate(doc, "final"):
        rep.add(p.level, "content", p.where, p.message)
    check_numbers(doc, rep)
    check_quotes(doc, project_dir, rep)
    check_theme(doc, rep)
    check_outputs(doc, project_dir, rep)
    if layout:
        check_layout(project_dir, doc, rep)
    check_pdfs(project_dir, doc, rep)
    return rep
