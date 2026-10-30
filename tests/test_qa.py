import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import qa, render  # noqa: E402


class QaTest(unittest.TestCase):
    """QA must pass the demo and catch errors seeded into a broken copy of it."""

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_demo.py")], check=True, capture_output=True)
        cls.src = os.path.join(ROOT, "examples", "demo", "reporch-projects", "basket-checkout")

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.project = os.path.join(self.tmp, "p")
        shutil.copytree(self.src, self.project)
        self.doc = self.load()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def load(self):
        with open(os.path.join(self.project, "content.json"), encoding="utf-8") as f:
            return json.load(f)

    def save_and_build(self, doc):
        with open(os.path.join(self.project, "content.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        render.build(doc, self.project)

    def checks(self, rep, level="error"):
        return {i["check"] for i in rep.items if i["level"] == level}

    def test_demo_passes(self):
        self.save_and_build(self.doc)
        rep = qa.run(self.project, layout=False)
        self.assertEqual(rep.errors(), [])
        self.assertEqual(self.checks(rep, "warning"), {"images"})          # demo placeholders only

    def test_invented_quote_is_an_error(self):
        q = self.doc["sections"][4]["blocks"][4]
        self.assertEqual(q["type"], "quote")
        q["text"] = {"en": "I loved every second of it.", "fa": "هر لحظه‌اش را دوست داشتم."}
        self.save_and_build(self.doc)
        self.assertIn("quotes", self.checks(qa.run(self.project, layout=False)))

    def test_changed_number_is_flagged(self):
        a = self.doc["analyses"][0]
        a["finding"]["en"] = a["finding"]["en"].replace("12.5%", "21.5%")
        self.save_and_build(self.doc)
        rep = qa.run(self.project, layout=False)
        self.assertTrue(any(i["check"] == "numbers" and "21.5" in i["message"] for i in rep.items))

    def test_language_leak_arabic_letters_and_credit(self):
        self.save_and_build(self.doc)
        out = os.path.join(self.project, "out")
        with open(os.path.join(out, "report.en.html"), encoding="utf-8") as f:
            page = f.read()
        page = page.replace("<h1>", "<h1>خلاصه ", 1).replace(render.CREDIT, "")
        with open(os.path.join(out, "report.en.html"), "w", encoding="utf-8") as f:
            f.write(page)
        with open(os.path.join(out, "report.fa.html"), encoding="utf-8") as f:
            fa = f.read()
        with open(os.path.join(out, "report.fa.html"), "w", encoding="utf-8") as f:
            f.write(fa.replace("<h1>", "<h1>كيك ", 1))
        found = self.checks(qa.run(self.project, layout=False))
        self.assertTrue({"language", "credit", "orthography"} <= found, found)

    def test_network_file_and_missing_output(self):
        self.save_and_build(self.doc)
        out = os.path.join(self.project, "out")
        with open(os.path.join(out, "blog.en.html"), "a", encoding="utf-8") as f:
            f.write('<img src="https://example.com/x.png">')
        os.remove(os.path.join(out, "blog.fa.html"))
        found = self.checks(qa.run(self.project, layout=False))
        self.assertTrue({"offline", "outputs"} <= found, found)

    def test_bad_brand_colour(self):
        self.doc["meta"]["brand"]["primary"] = "not-a-colour"
        self.save_and_build_safe()
        self.assertIn("brand", self.checks(qa.run(self.project, layout=False)))

    def save_and_build_safe(self):
        with open(os.path.join(self.project, "content.json"), "w", encoding="utf-8") as f:
            json.dump(self.doc, f, ensure_ascii=False)

    def test_layout_is_skipped_not_passed_without_browser(self):
        self.save_and_build(self.doc)
        rep = qa.run(self.project, layout=True)
        from reporch_lib import pdf
        if not pdf.available():
            self.assertIn("layout", self.checks(rep, "skipped"))


if __name__ == "__main__":
    unittest.main()
