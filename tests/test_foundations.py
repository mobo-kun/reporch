import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import content, project, theme  # noqa: E402


def T(en, fa=None):
    return {"en": en, "fa": fa or "متن " + en}


def minimal_doc(n_analyses=10):
    analyses = [{
        "id": f"AN{i}", "catalogueId": "A1", "title": T(f"Analysis {i}"), "finding": T(f"Finding {i}"),
        "table": {"columns": ["task", "success"], "rows": [["T1", 0.5], ["T2", 0.9]]},
        "chart": {"kind": "bar", "x": "task", "series": ["success"]}, "evidence": ["E1"],
    } for i in range(1, n_analyses + 1)]
    sec = lambda role, blocks=None: {"id": role, "role": role, "title": T(role), "blocks": blocks or [
        {"type": "paragraph", "text": T(role + " text"), "evidence": ["E1"]}]}
    return {
        "schema": content.SCHEMA_ID,
        "meta": {"title": T("Study"), "slug": "demo-study", "authors": [{"name": "A. Designer"}],
                 "languages": ["en", "fa"], "studyGoal": "formative"},
        "participants": [{"id": "P01"}, {"id": "P02"}],
        "evidence": [{"id": "E1", "source": "inputs/notes.md", "participant": "P01"}],
        "analyses": analyses,
        "sections": [sec("summary"), sec("problem", [
            {"type": "quote", "text": T("It was hard"), "participant": "P01", "evidence": ["E1"]},
            {"type": "image", "caption": T("Checkout"), "placeholder": {
                "kind": "screenshot", "description": "Checkout page on mobile, step 2"}}]),
            sec("solution"), sec("result", [{"type": "analysis", "analysis": a["id"]} for a in analyses])],
    }


class ContentTest(unittest.TestCase):
    def test_minimal_doc_is_valid_for_final(self):
        self.assertEqual(content.errors(content.validate(minimal_doc(), "final")), [])

    def test_missing_translation_is_warning_in_draft_error_in_final(self):
        d = minimal_doc()
        d["sections"][0]["title"] = {"en": "Summary"}
        draft = content.validate(d, "draft")
        self.assertTrue(any(p.level == "warning" and "missing 'fa'" in p.message for p in draft))
        self.assertTrue(content.errors(content.validate(d, "final")))

    def test_analysis_count_bounds(self):
        for n, ok in ((9, False), (10, True), (40, True), (41, False)):
            errs = content.errors(content.validate(minimal_doc(n), "final"))
            self.assertEqual(not any(p.where == "analyses" for p in errs), ok, n)

    def test_required_sections_and_order(self):
        d = minimal_doc()
        d["sections"] = [s for s in d["sections"] if s["role"] != "solution"]
        self.assertTrue(any("solution" in p.message for p in content.validate(d)))
        d = minimal_doc()
        d["sections"].reverse()
        self.assertTrue(any("outline order" in p.message for p in content.validate(d)))

    def test_quote_needs_known_participant_and_evidence(self):
        d = minimal_doc()
        q = d["sections"][1]["blocks"][0]
        q["participant"], q["evidence"] = "P09", []
        msgs = " ".join(p.message for p in content.errors(content.validate(d)))
        self.assertIn("unknown participant P09", msgs)
        self.assertIn("no invented quotes", msgs)

    def test_participants_must_be_anonymised(self):
        d = minimal_doc()
        d["participants"][0]["id"] = "Sara"
        self.assertTrue(any("anonymised" in p.message for p in content.errors(content.validate(d))))

    def test_chart_must_match_table(self):
        d = minimal_doc()
        d["analyses"][0]["chart"]["series"] = ["time"]
        d["analyses"][1]["table"]["rows"][0] = ["T1"]
        msgs = " ".join(p.message for p in content.errors(content.validate(d)))
        self.assertIn("column 'time' is not in the table", msgs)
        self.assertIn("1 cells for 2 columns", msgs)

    def test_unknown_references(self):
        d = minimal_doc()
        d["analyses"][0]["evidence"] = ["E99"]
        d["sections"][3]["blocks"].append({"type": "analysis", "analysis": "AN99"})
        msgs = " ".join(p.message for p in content.errors(content.validate(d)))
        self.assertIn("unknown evidence E99", msgs)
        self.assertIn("unknown analysis AN99", msgs)

    def test_image_needs_src_or_described_placeholder(self):
        d = minimal_doc()
        d["sections"][1]["blocks"][1].pop("placeholder")
        self.assertTrue(any("placeholder" in p.message for p in content.errors(content.validate(d))))
        d = minimal_doc()
        d["sections"][1]["blocks"][1]["placeholder"] = {"kind": "screenshot"}
        self.assertTrue(content.errors(content.validate(d)))

    def test_unplaced_analysis_warns(self):
        d = minimal_doc()
        d["sections"][3]["blocks"].pop()
        self.assertTrue(any("not placed" in p.message for p in content.validate(d, "draft")))


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.path = project.init(self.root, "demo-study")

    def test_init_creates_folders_and_state(self):
        for d in project.SUBDIRS:
            self.assertTrue(os.path.isdir(os.path.join(self.path, d)))
        s = project.load_state(self.path)
        self.assertEqual((s["phase"], s["languages"], s["version"]), ("collect", ["fa", "en"], 0))
        self.assertIn(os.path.join("reporch-projects", "demo-study"), self.path)
        with self.assertRaises(FileExistsError):
            project.init(self.root, "demo-study")

    def test_advance_follows_workflow_and_allows_custom_jump(self):
        self.assertEqual(project.advance(self.path)["phase"], "interview")
        s = project.advance(self.path, to="write")
        self.assertEqual(s["phase"], "write")
        self.assertEqual(s["phasesDone"], ["collect", "interview"])
        with self.assertRaises(ValueError):
            project.advance(self.path, to="publish")

    def test_snapshot_keeps_versions(self):
        self.assertEqual(project.snapshot(self.path), 0)          # nothing to keep yet
        with open(os.path.join(self.path, "content.json"), "w") as f:
            json.dump(minimal_doc(), f)
        open(os.path.join(self.path, "out", "report.en.html"), "w").write("v1")
        self.assertEqual(project.snapshot(self.path), 1)
        open(os.path.join(self.path, "out", "report.en.html"), "w").write("v2")
        self.assertEqual(project.snapshot(self.path), 2)
        v1 = open(os.path.join(self.path, "versions", "v1", "out", "report.en.html")).read()
        self.assertEqual(v1, "v1")

    def test_dependencies_are_recorded(self):
        project.add_dependency(self.path, "Which SUS benchmark?", "68")
        self.assertEqual(project.load_state(self.path)["dependencies"][0]["default"], "68")


class ThemeTest(unittest.TestCase):
    def test_scale_endpoints(self):
        s = theme.scale("#754EC6")
        self.assertEqual(s[500], "#754EC6")
        self.assertGreater(theme.luminance(s[50]), theme.luminance(s[500]))
        self.assertLess(theme.luminance(s[900]), theme.luminance(s[500]))

    def test_every_text_step_meets_aa_on_white(self):
        for name, sc in theme.tokens().items():
            step = theme.text_step(sc[500])
            self.assertGreaterEqual(theme.contrast(sc[step], "#FFFFFF"), 4.5, name)

    def test_contrast_reference_values(self):
        self.assertAlmostEqual(theme.contrast("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertAlmostEqual(theme.contrast("#777777", "#FFFFFF"), 4.48, places=2)

    def test_brand_primary_replaces_default(self):
        css = theme.css("#0a66c2")
        self.assertIn("--primary-500: #0A66C2;", css)
        self.assertIn("--glow: rgba(151, 71, 255, 0.1);", css)
        with self.assertRaises(ValueError):
            theme.css("blue")

    def test_generated_css_is_current(self):
        with open(os.path.join(ROOT, "templates", "theme.css"), encoding="utf-8") as f:
            self.assertIn(theme.css(), f.read())


if __name__ == "__main__":
    unittest.main()
