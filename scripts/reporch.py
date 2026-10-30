#!/usr/bin/env python3
"""Reporch command line. Python 3.9+, standard library only.

  reporch.py init <slug> [--root DIR] [--languages fa,en]
  reporch.py status <project>
  reporch.py advance <project> [--to PHASE]
  reporch.py validate <project> [--final]
  reporch.py snapshot <project>
  reporch.py theme [--primary #RRGGBB]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reporch_lib import content, project, theme  # noqa: E402


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
    elif a.cmd == "theme":
        sys.stdout.write(theme.css(a.primary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
