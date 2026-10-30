#!/usr/bin/env python3
"""Reporch command line. Python 3.9+, standard library only.

  reporch.py init <slug> [--root DIR] [--languages fa,en]
  reporch.py status <project>
  reporch.py advance <project> [--to PHASE]
  reporch.py validate <project> [--final]
  reporch.py snapshot <project>
  reporch.py theme [--primary #RRGGBB]
  reporch.py ingest <project> FILE... [--names names.json]
  reporch.py profile <project> --fields a,b,c        (record which data fields the inputs contain)
  reporch.py possible <project>                      (analyses the data supports, and the gaps to ask about)
  reporch.py calc <function> '<JSON arguments>'       (statistics, e.g. calc proportion '{"successes": 3, "n": 10}')
  reporch.py build <project> [--markdown] [--draft]  (HTML report and blog for each language)
  reporch.py pdf <project>                           (PDF from the report HTML; needs Playwright)
  reporch.py qa <project> [--no-layout]              (checks before delivery)
  reporch.py migrate <project> <report.html|.pdf> --lang fa   (existing report → draft content.json)
  reporch.py lossless <project>                      (is every part of the original in content.json?)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reporch_lib import catalogue, content, intake, migrate, pdf, project, qa, render, stats, theme  # noqa: E402


CALC = ["proportion", "mean_ci", "time_summary", "outliers", "sus", "nps", "top_box", "lostness", "efficiency",
        "problem_discovery", "t_test", "anova", "chi_square", "fisher_exact", "two_proportions", "correlation",
        "z_scores", "funnel", "retention", "stickiness", "customer_lifetime_value", "net_revenue_retention"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="reporch")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("slug"); p.add_argument("--root", default=os.getcwd())
    p.add_argument("--languages", default="fa,en")
    p = sub.add_parser("status"); p.add_argument("project")
    p = sub.add_parser("advance"); p.add_argument("project"); p.add_argument("--to")
    p = sub.add_parser("validate"); p.add_argument("project"); p.add_argument("--final", action="store_true")
    p = sub.add_parser("snapshot"); p.add_argument("project")
    p = sub.add_parser("theme"); p.add_argument("--primary")
    p = sub.add_parser("ingest"); p.add_argument("project"); p.add_argument("files", nargs="+")
    p.add_argument("--names", help="JSON file mapping real names to participant ids")
    p = sub.add_parser("profile"); p.add_argument("project"); p.add_argument("--fields", required=True)
    p = sub.add_parser("possible"); p.add_argument("project")
    p = sub.add_parser("calc"); p.add_argument("function", choices=CALC); p.add_argument("args")
    p = sub.add_parser("build"); p.add_argument("project"); p.add_argument("--markdown", action="store_true")
    p.add_argument("--draft", action="store_true", help="build a preview even with open problems (never for delivery)")
    p = sub.add_parser("pdf"); p.add_argument("project")
    p = sub.add_parser("qa"); p.add_argument("project"); p.add_argument("--no-layout", action="store_true")
    p = sub.add_parser("migrate"); p.add_argument("project"); p.add_argument("file"); p.add_argument("--lang", required=True)
    p = sub.add_parser("lossless"); p.add_argument("project")
    a = ap.parse_args(argv)

    if a.cmd == "init":
        langs = [l.strip() for l in a.languages.split(",") if l.strip()]
        print(project.init(a.root, a.slug, langs))
    elif a.cmd == "status":
        print(json.dumps(project.load_state(a.project), ensure_ascii=False, indent=2))
    elif a.cmd == "advance":
        print(project.advance(a.project, a.to)["phase"])
    elif a.cmd == "validate":
        with open(os.path.join(a.project, "content.json"), encoding="utf-8") as f:
            problems = content.validate(json.load(f), "final" if a.final else "draft")
        for pr in problems:
            print(pr)
        errs = content.errors(problems)
        print(f"{len(errs)} error(s), {len(problems) - len(errs)} warning(s)")
        return 1 if errs else 0
    elif a.cmd == "snapshot":
        print(f"v{project.snapshot(a.project)}")
    elif a.cmd == "ingest":
        names = json.load(open(a.names, encoding="utf-8")) if a.names else None
        for r in intake.ingest(a.project, a.files, names):
            print(json.dumps(r, ensure_ascii=False))
    elif a.cmd == "profile":
        fields = sorted({f.strip() for f in a.fields.split(",") if f.strip()})
        bad = catalogue.unknown_fields(fields)
        if bad:
            print("unknown fields: " + ", ".join(bad) + " (see references/analyses.json)", file=sys.stderr)
            return 1
        state = project.load_state(a.project)
        state["dataFields"] = fields
        project.save_state(a.project, state)
        print(f"{len(fields)} fields recorded")
    elif a.cmd == "possible":
        fields = project.load_state(a.project).get("dataFields", [])
        print(json.dumps(catalogue.summary(fields), ensure_ascii=False, indent=1))
    elif a.cmd == "calc":
        args = json.loads(a.args)
        fn = getattr(stats, a.function)
        result = fn(**args) if isinstance(args, dict) else fn(*args)
        print(json.dumps(result, ensure_ascii=False, indent=1))
    elif a.cmd == "build":
        doc = _load(a.project)
        errs = content.errors(content.validate(doc, "draft" if a.draft else "final"))
        if errs and not a.draft:
            for e in errs:
                print(e, file=sys.stderr)
            print(f"{len(errs)} error(s): fix them (or use --draft for a preview)", file=sys.stderr)
            return 1
        if errs:
            print(f"preview only: {len(errs)} error(s) still open", file=sys.stderr)
        for path in render.build(doc, a.project, a.markdown):
            print(path)
    elif a.cmd == "pdf":
        if not pdf.available():
            print("Playwright is not installed. Ask the user, then run:\n  " + pdf.INSTALL, file=sys.stderr)
            return 2
        doc = _load(a.project)
        for lang in doc["meta"]["languages"]:
            src = os.path.join(a.project, "out", f"report.{lang}.html")
            if not os.path.exists(src):
                print(f"missing {src}: run build first", file=sys.stderr)
                return 1
            print(pdf.render(src, os.path.join(a.project, "out", f"report.{lang}.pdf")))
    elif a.cmd == "qa":
        rep = qa.run(a.project, layout=not a.no_layout)
        for i in rep.items:
            print(f"{i['level'].upper():8} {i['check']:12} {i['where']}: {i['message']}")
        print(json.dumps(rep.summary()))
        return 1 if rep.errors() else 0
    elif a.cmd == "migrate":
        import shutil
        try:
            inv = migrate.inventory(a.file)
        except (RuntimeError, ValueError) as e:
            print(e, file=sys.stderr)
            return 2
        mdir = os.path.join(a.project, "migration")
        os.makedirs(os.path.join(a.project, "inputs", "original"), exist_ok=True)
        os.makedirs(mdir, exist_ok=True)
        shutil.copy2(a.file, os.path.join(a.project, "inputs", "original"))
        with open(os.path.join(mdir, "inventory.json"), "w", encoding="utf-8") as f:
            json.dump(inv, f, ensure_ascii=False, indent=1)
        slug = project.load_state(a.project)["slug"]
        doc, questions = migrate.draft(inv, a.lang, slug, a.project)
        target = os.path.join(a.project, "content.json")
        if os.path.exists(target):
            target = os.path.join(mdir, "content.migrated.json")
        with open(target, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        res = migrate.lossless(inv, doc)
        print(f"{target}\nsections {len(inv['sections'])}, charts {len(inv['charts'])}, "
              f"units kept {res['kept']}/{res['units']}")
        for q in questions:
            print("QUESTION: " + q)
        return 0 if res["complete"] else 1
    elif a.cmd == "lossless":
        with open(os.path.join(a.project, "migration", "inventory.json"), encoding="utf-8") as f:
            inv = json.load(f)
        res = migrate.lossless(inv, _load(a.project))
        print(json.dumps({k: v for k, v in res.items() if k != "missing"}))
        for m in res["missing"][:50]:
            print(f"MISSING  {m['where']}: {m['text']}")
        return 0 if res["complete"] else 1
    elif a.cmd == "theme":
        sys.stdout.write(theme.css(a.primary))
    return 0


def _load(project_dir):
    with open(os.path.join(project_dir, "content.json"), encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    sys.exit(main())
