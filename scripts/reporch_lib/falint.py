"""Check the Persian text of content.json with the bundled persian-writing linter (vendor/persian-writing).

Quotes are skipped: participants' words stay exactly as said. The linter only reports; any fix to the
user's wording is asked first (SKILL.md rule 1).
"""
import os
import re
import subprocess
import sys
import tempfile

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINT = os.path.join(SKILL, "vendor", "persian-writing", "scripts", "fa_lint.py")
IGNORE = {"bidi-start", "fixable"}
SKIP_KEYS = {"evidence", "id", "src", "poster", "participant", "catalogueId", "source", "locator", "kind", "slug"}


def texts(doc, lang="fa"):
    """(where, text) for every `lang` string outside quotes."""
    out = []

    def walk(node, where):
        if isinstance(node, dict):
            if node.get("type") == "quote":
                return
            if lang in node and isinstance(node[lang], str) and set(node) <= {"en", "fa", "ar", "de", "fr", "es", lang}:
                if node[lang].strip():
                    out.append((where, node[lang]))
                return
            for k, v in node.items():
                if k not in SKIP_KEYS:
                    walk(v, f"{where}.{k}" if where else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{where}[{i}]")

    walk(doc, "")
    return out


def run(doc, lang="fa"):
    """Return (number of issues, report text with content.json locations)."""
    items = texts(doc, lang)
    if not items:
        return 0, ""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for _, t in items:
            f.write(t.replace("\n", " ") + "\n")
        tmp = f.name
    try:
        r = subprocess.run([sys.executable, LINT, "--check", tmp], capture_output=True, text=True, encoding="utf-8")
    finally:
        os.unlink(tmp)
    report = (r.stdout + r.stderr).replace(tmp, "content.json")   # the linter reports on stderr
    report = re.sub(r"L(\d+):", lambda m: (items[int(m.group(1)) - 1][0] + ":") if 0 < int(m.group(1)) <= len(items) else m.group(0), report)
    # bidi-start only matters in plain text; the pages set their own direction. "fixable" is a summary line.
    n = sum(int(c) for cat, c in re.findall(r"\[([\w-]+)\] ×(\d+)", report) if cat not in IGNORE)
    return n, report
