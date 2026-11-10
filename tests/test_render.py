import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import content, render  # noqa: E402

ARABIC = re.compile(r"[؀-ۿ]")


class DemoRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_demo.py")], check=True, capture_output=True)
        src = os.path.join(ROOT, "examples", "demo", "basket-checkout")
        cls.project = os.path.join(cls.tmp, "basket-checkout")
        shutil.copytree(src, cls.project)
        with open(os.path.join(cls.project, "content.json"), encoding="utf-8") as f:
            cls.doc = json.load(f)
        cls.paths = render.build(cls.doc, cls.project, markdown_too=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def read(self, name):
        with open(os.path.join(self.project, "out", name), encoding="utf-8") as f:
            return f.read()

    def test_demo_is_valid(self):
        self.assertEqual(content.errors(content.validate(self.doc, "final")), [])
        self.assertGreaterEqual(len(self.doc["analyses"]), 10)

    def test_all_outputs_written(self):
        names = sorted(os.path.basename(p) for p in self.paths)
        self.assertEqual(names, sorted(f"{k}.{l}.{e}" for k in ("report", "blog") for l in ("en", "fa") for e in ("html", "md")))

    def test_offline_single_file(self):
        for name in ("report.en.html", "report.fa.html", "blog.en.html", "blog.fa.html"):
            page = self.read(name)
            self.assertNotRegex(page, r'<(script|link|img|video)[^>]+(src|href)="https?://', name)
            self.assertIn("data:font/woff2;base64,", page)
            self.assertLess(len(page.encode()), 40 * 1024 * 1024)

    def test_single_language_and_direction(self):
        en, fa = self.read("report.en.html"), self.read("report.fa.html")
        self.assertIn('<html lang="en" dir="ltr">', en)
        self.assertIn('<html lang="fa" dir="rtl">', fa)
        body = re.sub(r"<script.*?</script>|<style.*?</style>", "", en, flags=re.S)
        self.assertIsNone(ARABIC.search(body), "Persian text leaked into the English report")
        self.assertIn("۸ از ۸", fa)

    def test_charts_match_content(self):
        page = self.read("report.en.html")
        n = sum(1 for a in self.doc["analyses"] if a.get("chart"))
        self.assertEqual(page.count('data-chart="chart-'), n)
        specs = re.findall(r'<script type="application/json" id="chart-\d+-data">(.*?)</script>', page)
        self.assertEqual(len(specs), n)
        loc = lambda v: v["en"] if isinstance(v, dict) else v
        tables = [[[loc(v) for v in r] for r in a["table"]["rows"]] for a in self.doc["analyses"] if a.get("chart")]
        for spec in specs:                                                     # each chart is drawn from its own table
            self.assertIn(json.loads(spec)["table"]["rows"], tables)
        fa = self.read("report.fa.html")
        self.assertIn('"سبد"', fa)                                            # chart categories are localized
        self.assertIn('"بدون کمک"', fa)                                       # and so are series names
        self.assertIn("echarts", page)

    def test_credit_placeholders_and_evidence(self):
        page = self.read("report.en.html")
        self.assertIn(render.CREDIT, page)
        self.assertIn('class="placeholder"', page)
        self.assertIn('id="ev-E6"', page)
        self.assertNotIn('href="#ev-', self.read("blog.en.html"))           # the blog has no evidence index

    def test_persian_numbers_in_tables(self):
        r = render.Renderer(self.doc, "fa", self.project)
        self.assertEqual(r.num(0.125, "percent"), "۱۲٫۵٪")
        self.assertEqual(r.num(63.125), "۶۳٫۱۲")
        self.assertEqual(r.num("T1"), "T1")                                    # codes keep Latin digits
        self.assertEqual(render.Renderer(self.doc, "en", self.project).num(1.0, "percent"), "100%")

    def test_overlay_hidden_outside_phones(self):
        with open(os.path.join(ROOT, "templates", "report.css"), encoding="utf-8") as f:
            css = f.read()
        top_level = css.split("@media")[0]
        self.assertIn(".scrim { display: none; }", top_level)                 # B-016

    def test_markdown(self):
        md = self.read("report.en.md")
        self.assertTrue(md.startswith("# Basket checkout usability test"))
        self.assertIn("| task | success | low | high | successes | n |", md)
        self.assertIn(render.CREDIT, md)

    def test_brand_font_only_from_assets(self):
        self.assertEqual(render.brand_font(self.project)[0], "")
        fonts = os.path.join(self.project, "assets", "fonts")
        os.makedirs(fonts, exist_ok=True)
        with open(os.path.join(fonts, "Brand-Bold.woff2"), "wb") as f:
            f.write(b"wOF2")
        face, stack = render.brand_font(self.project)
        self.assertIn("font-weight: 700", face)
        self.assertTrue(stack.startswith('"ReporchBrand"'))
        page = render.Renderer(self.doc, "fa", self.project).report()
        shutil.rmtree(fonts)
        self.assertIn('--font: "Vazirmatn"', page)                      # body text stays Vazirmatn (B-026)
        self.assertIn('--font-display: "ReporchBrand"', page)          # brand font: titles and big numbers only

    def test_deck_is_built_from_content(self):
        page = self.read("report.en.html")
        end = page[page.index('<section class="slide s-end">'):]
        end = end[: end.index("</section>")]
        self.assertIn("Nora Vale", end)                                # B-033: the designer, not Reporch
        self.assertEqual(end.count("Made with Reporch"), 1)
        self.assertIn('class="s-credit"', end)                         # B-034: only the small footer line
        slides = re.findall(r'<section class="slide ([\w -]+)"', page)
        self.assertEqual(slides[0], "s-cover")
        self.assertEqual(slides[-1], "s-end")
        self.assertEqual(sum("s-analysis" in s for s in slides), sum(1 for _ in re.finditer(r'class="analysis"', page)))
        for cid in re.findall(r'data-deck-chart="([\w-]+)"', page):        # deck charts reuse the report's data
            self.assertIn(f'id="{cid}"', page)

    def test_compare_and_impact_stats(self):
        page = self.read("report.fa.html")
        self.assertIn('<div class="compare">', page)
        self.assertIn('class="tag">قبل<', page)
        self.assertIn('<section class="slide s-compare">', page)
        self.assertIn('<div class="detail">۸ نفر از ۸ نفر</div>', page)    # raw numbers under the impact value
        md = self.read("report.en.md")
        self.assertIn("**Before:**", md)
        self.assertIn("(8 of 8 people)", md)

    def test_evidence_runs_and_heading_levels(self):
        doc = json.loads(json.dumps(self.doc))
        sec = doc["sections"][0]
        para = {"type": "paragraph", "text": {"en": "One", "fa": "یک"}, "evidence": ["E1"]}
        sec["blocks"] = [para, dict(para), dict(para, evidence=["E2"])]
        html_ = render.Renderer(doc, "en", self.project).report()
        part = html_[html_.index(f'id="{sec["id"]}"'):]
        part = part[: part.index("</section>")]
        self.assertEqual(part.count('href="#ev-E1"'), 1)               # B-028: once after the run
        self.assertEqual(part.count('href="#ev-E2"'), 1)
        page = self.read("report.en.html")
        for sub in re.finditer(r'<section class="sec[^"]*" id="[^"]+"><h3>.*?</section>', page):
            self.assertNotIn('class="analysis" id="an-', re.sub(r'<div class="analysis" id="an-[^"]+"><h4>', "", sub.group(0)))

    def test_evidence_shows_original_file_names(self):
        name = render._source_names(self.project)
        self.assertEqual(name("notes/x.md"), "notes/x.md")
        os.makedirs(os.path.join(self.project, "inputs"), exist_ok=True)
        idx = os.path.join(self.project, "inputs", "index.json")
        with open(idx, "w") as f:
            json.dump([{"file": "observation sheet.xlsx"}], f)
        name = render._source_names(self.project)
        os.remove(idx)
        self.assertEqual(name("inputs/clean/observation sheet.tables.json"), "observation sheet.xlsx")
        self.assertEqual(name("inputs/clean/other.txt"), "other.txt")

    def test_escaping(self):
        doc = json.loads(json.dumps(self.doc))
        doc["sections"][1]["blocks"][0]["text"]["en"] = "<script>alert(1)</script> **bold**"
        page = render.Renderer(doc, "en", self.project).report()
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("<strong>bold</strong>", page)


if __name__ == "__main__":
    unittest.main()
