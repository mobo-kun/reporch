import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import content, migrate, project, render  # noqa: E402

# A fictional old-style report: slide sections, a TOC to skip, stat cards, a table, a quote, Chart.js
# charts (one direct, one from a factory function, one with a null value) and an embedded image.
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
HTML = f"""<!doctype html><html lang="en"><head><title>Old checkout report</title></head><body>
<nav class="sidebar"><a href="#s1">Summary</a><a href="#s2">Findings</a></nav>
<header class="mobile-header"><span>Old checkout report</span></header>
<main>
<section class="slide" id="s1"><h2 class="slide-title">Summary</h2>
  <div class="stat-card"><div class="sc-label">Success, task 3</div><div class="sc-val">12%</div><div class="sc-note">1 of 8, unaided</div></div>
  <p>Most people <strong>filled the basket</strong> easily.</p>
  <ul><li>Discount field hidden</li><li>Pay button below the fold</li></ul>
</section>
<section class="slide" id="s2"><h2 class="slide-title">Findings by task</h2>
  <div class="quote-block">P02: “I know I have a code, but there's nowhere to put it.”</div>
  <div class="quote-block">“So where do I pay?”</div>
  <div class="info-box info-warn">Eight people is a small sample.</div>
  <table><tr><th>Task</th><th>Success</th></tr><tr><td>T1</td><td>8/8</td></tr><tr><td>T3</td><td>1/8</td></tr></table>
  <canvas id="chartTasks"></canvas><canvas id="chartDevice"></canvas><canvas id="chartMixed"></canvas>
  <img src="data:image/png;base64,{PNG}" alt="Old payment step">
</section>
<section class="slide" id="s3"><h2 class="slide-title">Untitled thoughts</h2><div>Something the designer wrote.</div></section>
</main>
<script>
const deviceData = [5, 3];
new Chart(document.getElementById('chartTasks'), {{ type:'bar', data:{{ labels:['T1','T2','T3'],
  datasets:[{{ label:'Success %', data:[100, 62.5, 12.5] }}] }} }});
function makeDevice(canvasId, labels) {{ return new Chart(document.getElementById(canvasId), {{ type:'doughnut',
  data:{{ labels:labels, datasets:[{{ data:deviceData }}] }} }}); }}
makeDevice('chartDevice', ['Mobile','Desktop']);
new Chart(document.getElementById('chartMixed'), {{ type:'bar', data:{{ labels:['A','B'],
  datasets:[{{ label:'x', data:[1, null] }}] }} }});
</script></body></html>"""


class MigrateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "old.html")
        with open(self.src, "w", encoding="utf-8") as f:
            f.write(HTML)
        self.project = project.init(os.path.join(self.tmp, "old-checkout"), None, ["en"])
        self.inv = migrate.inventory(self.src)
        self.doc, self.questions = migrate.draft(self.inv, "en", "old-checkout", self.project)

    def test_inventory_skips_navigation_but_keeps_header(self):
        texts = [it["text"] for s in self.inv["sections"] for it in s["items"] if it["kind"] == "text"]
        self.assertNotIn("Findings", texts)                        # TOC link skipped
        self.assertIn("Old checkout report", texts)                # <header> kept: covers live there
        self.assertIn("Most people filled the basket easily.", texts)   # inline <strong> stays in its paragraph

    def test_charts_including_factory_and_null(self):
        by = {c["canvas"]: c for c in self.inv["charts"]}
        self.assertEqual(set(by), {"chartTasks", "chartDevice", "chartMixed"})
        self.assertEqual(migrate._js_array(by["chartDevice"]["data"][0]), [5, 3])
        self.assertEqual(migrate._js_array(by["chartMixed"]["data"][0]), [1, None])

    def test_draft_is_lossless(self):
        res = migrate.lossless(self.inv, self.doc)
        self.assertTrue(res["complete"], res["missing"])
        self.assertGreater(res["units"], 15)

    def test_lossless_catches_a_dropped_or_changed_piece(self):
        doc = json.loads(json.dumps(self.doc))
        sec = {x["id"]: x for x in doc["sections"]}
        para = next(b for b in sec["s1"]["blocks"] if b["type"] == "paragraph")
        para["text"]["en"] = "Most people filled the basket."          # reworded
        sec["s2"]["blocks"] = [b for b in sec["s2"]["blocks"] if b["type"] != "table"]   # dropped
        res = migrate.lossless(self.inv, doc)
        missing = {m["text"] for m in res["missing"]}
        self.assertIn("Most people filled the basket easily.", missing)
        self.assertIn("8/8", missing)

    def test_blocks_mapped(self):
        blocks = [b for s in self.doc["sections"] for b in s["blocks"]]
        kinds = {b["type"] for b in blocks}
        self.assertTrue({"stats", "paragraph", "list", "quote", "callout", "table", "chart", "image"} <= kinds, kinds)
        stats = next(b for b in blocks if b["type"] == "stats")["items"][0]
        self.assertEqual((stats["label"]["en"], stats["value"]["en"], stats["note"]["en"]), ("Success, task 3", "12%", "1 of 8, unaided"))
        quotes = [b for b in blocks if b["type"] == "quote"]
        self.assertEqual([q["participant"] for q in quotes], ["P02", "P??"])
        image = next(b for b in blocks if b["type"] == "image")
        self.assertTrue(os.path.exists(os.path.join(self.project, image["src"])))
        chart = next(b for b in blocks if b["type"] == "chart" and b["chart"]["kind"] == "doughnut")
        self.assertEqual(chart["table"]["rows"], [["Mobile", 5], ["Desktop", 3]])

    def test_roles_and_questions(self):
        roles = {s["id"]: s["role"] for s in self.doc["sections"]}
        self.assertEqual((roles["s1"], roles["s2"]), ("summary", "problem"))
        q = " ".join(self.questions)
        self.assertIn("Untitled thoughts", q)                       # role unknown → ask
        self.assertIn("no participant id", q)
        self.assertIn("'solution'", q)
        self.assertIn("original files", q)

    def test_draft_previews_and_never_validates_silently(self):
        self.assertTrue(content.errors(content.validate(self.doc, "final")))   # questions still open
        self.doc["meta"]["authors"] = [{"name": {"en": "A. Designer"}}]
        html = render.Renderer(self.doc, "en", self.project).report()
        self.assertIn("Most people filled the basket easily.", html)
        self.assertIn("data:image/png;base64,", html)


if __name__ == "__main__":
    unittest.main()
