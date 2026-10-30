import json
import os
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import anonymise, catalogue, inputs, intake, project  # noqa: E402

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def make_docx(path):
    body = (f'<w:document {W}><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Session notes</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>Sara said: I could not find the </w:t></w:r><w:r><w:t>button.</w:t></w:r></w:p>'
            '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>task</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>ok</w:t></w:r></w:p></w:tc></w:tr>'
            '<w:tr><w:tc><w:p><w:r><w:t>T1</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>yes</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
            '</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", body)


def make_xlsx(path):
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    rns = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook {ns} {rns}><sheets><sheet name="Responses" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="x"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", f'<sst {ns}><si><t>email</t></si><si><t>score</t></si><si><t>a@b.co</t></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml",
                   f'<worksheet {ns}><sheetData>'
                   '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
                   '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="C2"><v>9</v></c></row>'
                   '</sheetData></worksheet>')


class InputsTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_docx_text_headings_and_tables(self):
        p = os.path.join(self.d, "notes.docx"); make_docx(p)
        r = inputs.read(p)
        self.assertIn("# Session notes", r["text"])
        self.assertIn("I could not find the button.", r["text"])
        self.assertEqual(r["tables"][0]["rows"], [["task", "ok"], ["T1", "yes"]])

    def test_xlsx_shared_strings_and_gaps(self):
        p = os.path.join(self.d, "form.xlsx"); make_xlsx(p)
        r = inputs.read(p)
        self.assertEqual(r["tables"][0]["name"], "Responses")
        self.assertEqual(r["tables"][0]["rows"], [["email", "score"], ["a@b.co", "", "9"]])

    def test_csv_semicolons_and_vtt(self):
        p = os.path.join(self.d, "f.csv"); open(p, "w").write("q1;q2\nyes;3\n")
        self.assertEqual(inputs.read(p)["tables"][0]["rows"], [["q1", "q2"], ["yes", "3"]])
        p = os.path.join(self.d, "t.vtt")
        open(p, "w").write("WEBVTT\n\n00:00.000 --> 00:02.000\n<v P01>Hello there\n\n2\n00:02.000 --> 00:03.000\nHello there\n")
        self.assertEqual(inputs.read(p)["text"], "P01: Hello there\nHello there")

    def test_unsupported_types_explain_why(self):
        p = os.path.join(self.d, "rec.mp4"); open(p, "w").write("x")
        with self.assertRaisesRegex(ValueError, "v2"):
            inputs.read(p)


class AnonymiseTest(unittest.TestCase):
    def test_contacts_numbers_and_names(self):
        text = ("Sara Ahmadi (sara.a@mail.com, 0912 345 6789, +98 912 345 6789, ۰۹۱۲۳۴۵۶۷۸۹) "
                "paid with 6037-9911-2233-4455. Sara liked it; Reza did not. Task took 12.5 s, 3 of 10 succeeded.")
        out, n = anonymise.anonymise(text, {"Sara Ahmadi": "P01", "Reza Karimi": "P02"})
        self.assertNotIn("Sara", out); self.assertNotIn("Reza", out); self.assertNotIn("@", out)
        self.assertNotIn("6789", out); self.assertNotIn("۶۷۸۹", out); self.assertNotIn("4455", out)
        self.assertIn("12.5 s, 3 of 10", out)                 # research numbers survive
        self.assertEqual((n["email"], n["phone"], n["card"]), (1, 3, 1))
        self.assertEqual(n["name"], 3)

    def test_persian_names_and_ambiguous_first_names(self):
        out, n = anonymise.anonymise("سارا گفت دکمه پیدا نشد. سارا محمدی موافق بود.",
                                     {"سارا احمدی": "P01", "سارا محمدی": "P02"})
        self.assertIn("P02", out)
        self.assertIn("سارا گفت", out)                         # ambiguous first name is left for the user
        self.assertEqual(n["name"], 1)


class CatalogueTest(unittest.TestCase):
    def test_catalogue_is_complete(self):
        cat = catalogue.load()
        ids = [a["id"] for a in cat["analyses"]]
        self.assertEqual(len(ids), 118)
        self.assertEqual(len(set(ids)), 118)
        for a in cat["analyses"]:
            self.assertTrue(a["needs"] and a["title"] and a["output"], a["id"])

    def test_usability_study_selection_and_gaps(self):
        fields = ["participants", "task_success", "task_time", "post_task_rating", "transcripts",
                  "issues", "issue_severity", "segment", "sus_items"]
        s = catalogue.summary(fields)
        self.assertTrue(s["enough"])
        for i in ("A1", "A3", "A17", "B1", "D1", "D4", "G1", "G2"):
            self.assertIn(i, s["possible"])
        self.assertNotIn("H5", s["possible"])
        self.assertEqual(s["gaps"][0][0], "issue_participant")   # next to existing data first

    def test_alternatives_and_unknown_fields(self):
        self.assertIn("A6", [a["id"] for a in catalogue.possible(["first_click"])])
        self.assertEqual(catalogue.unknown_fields(["task_success", "magic"]), ["magic"])


class IntakeTest(unittest.TestCase):
    def test_ingest_copies_cleans_and_indexes(self):
        root = tempfile.mkdtemp()
        path = project.init(root, "s")
        src = os.path.join(root, "notes.docx"); make_docx(src)
        bad = os.path.join(root, "clip.mov"); open(bad, "w").write("x")
        res = intake.ingest(path, [src, bad], {"Sara Ahmadi": "P01"})
        self.assertEqual([r["status"] for r in res], ["ok", "skipped"])
        with open(os.path.join(path, "inputs", "clean", "notes.txt"), encoding="utf-8") as f:
            clean = f.read()
        self.assertIn("P01 said", clean)
        self.assertTrue(os.path.exists(os.path.join(path, "inputs", "original", "notes.docx")))
        idx = self._index(path)
        self.assertEqual(idx[0]["removed"]["name"], 1)
        intake.ingest(path, [src])                               # re-ingest replaces, not duplicates
        self.assertEqual(len(self._index(path)), 2)

    @staticmethod
    def _index(path):
        with open(os.path.join(path, "inputs", "index.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_brand_mention(self):
        self.assertTrue(intake.mentions_brand("گزارش تست برای نوبیتکس"))
        self.assertTrue(intake.mentions_brand("We are the Nobitex growth team"))
        self.assertFalse(intake.mentions_brand("A fintech app"))


if __name__ == "__main__":
    unittest.main()
