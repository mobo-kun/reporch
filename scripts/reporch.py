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
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reporch_lib import catalogue, content, intake, project, stats, theme  # noqa: E402


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
    elif a.cmd == "theme":
        sys.stdout.write(theme.css(a.primary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
