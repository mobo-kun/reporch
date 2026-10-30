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
        src = os.path.join(ROOT, "examples", "demo", "reporch-projects", "basket-checkout")
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
        shutil.rmtree(fonts)

    def test_escaping(self):
        doc = json.loads(json.dumps(self.doc))
        doc["sections"][1]["blocks"][0]["text"]["en"] = "<script>alert(1)</script> **bold**"
        page = render.Renderer(doc, "en", self.project).report()
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("<strong>bold</strong>", page)


if __name__ == "__main__":
    unittest.main()
