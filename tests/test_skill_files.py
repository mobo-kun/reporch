import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class SkillFilesTest(unittest.TestCase):
    def test_skill_front_matter(self):
        m = re.match(r"^---\nname: (\S+)\ndescription: (.+?)\n---\n", read("SKILL.md"), re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "reporch")
        self.assertLess(len(m.group(2)), 1024)            # agent skill description limit

    def test_referenced_files_exist(self):
        """Every modules/ or references/ path named in SKILL.md exists (enforced as phases land)."""
        text = read("SKILL.md")
        missing = [p for p in re.findall(r"`((?:modules|references)/[\w./-]+\.(?:md|json))`", text)
                   if not os.path.exists(os.path.join(ROOT, p))]
        pending = {"modules/analysis.md", "modules/write.md", "modules/build.md", "modules/qa.md",
                   "modules/migrate.md"}
        self.assertEqual(sorted(set(missing) - pending), [])

    def test_generated_catalogue_is_current(self):
        src = read("tools/catalogue_source.md")
        self.assertTrue(read("references/analyses.md").endswith(src))


if __name__ == "__main__":
    unittest.main()
