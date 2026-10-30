"""Bring the user's files into a project: copy, read, anonymise, index.

<project>/inputs/original/   the files as given (stay on the user's machine)
<project>/inputs/clean/      anonymised text (.txt) and tables (.json) the agent works from
<project>/inputs/index.json  one entry per file: kind, size, tables, counts of removed personal data
"""
import json
import os
import shutil

from . import anonymise, inputs

BRAND_WORDS = ("nobitex", "نوبیتکس")


def ingest(project_path, files, names=None):
    orig = os.path.join(project_path, "inputs", "original")
    clean = os.path.join(project_path, "inputs", "clean")
    os.makedirs(orig, exist_ok=True)
    os.makedirs(clean, exist_ok=True)
    index_path = os.path.join(project_path, "inputs", "index.json")
    index = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    results = []
    for f in files:
        name = os.path.basename(f)
        entry = {"file": name}
        try:
            data = inputs.read(f)
        except (ValueError, KeyError, OSError) as e:
            entry.update(status="skipped", reason=str(e))
            results.append(entry)
            continue
        if os.path.abspath(f) != os.path.abspath(os.path.join(orig, name)):
            shutil.copy2(f, orig)
        text, counts = anonymise.anonymise(data["text"], names)
        stem = os.path.splitext(name)[0]
        with open(os.path.join(clean, stem + ".txt"), "w", encoding="utf-8") as out:
            out.write(text)
        if data.get("tables"):
            tables = []
            for t in data["tables"]:
                rows = [[anonymise.anonymise(str(c), names)[0] for c in r] for r in t["rows"]]
                tables.append({"name": t["name"], "rows": rows})
            with open(os.path.join(clean, stem + ".tables.json"), "w", encoding="utf-8") as out:
                json.dump(tables, out, ensure_ascii=False, indent=1)
            entry["tables"] = [{"name": t["name"], "rows": len(t["rows"]),
                                "columns": len(t["rows"][0]) if t["rows"] else 0} for t in tables]
        entry.update(status="ok", kind=data["kind"], chars=len(text), removed=counts)
        results.append(entry)
    index = [e for e in index if e["file"] not in {r["file"] for r in results}] + results
    with open(index_path, "w", encoding="utf-8") as out:
        json.dump(index, out, ensure_ascii=False, indent=1)
    return results


def mentions_brand(text):
    """True when the user's own words name the first adopters' company (R19)."""
    low = text.lower()
    return any(w in low for w in BRAND_WORDS)
