# Reporch for Codex and other agents

This repository is one agent skill. Its instructions are in [`SKILL.md`](SKILL.md): read it first and
follow it exactly, including the first-run greeting, the non-negotiable rules and the workflow.

- Install for Codex: clone into `~/.agents/skills/reporch` (or run `install.sh`).
- Tools: `python3 scripts/reporch.py --help` (Python 3.9+, standard library only).
- Never write user projects inside this folder; the project is the folder the designer opened for the study (see SKILL.md, "Project folder").

## Working on Reporch itself

- Run the tests before every commit: `python3 -m unittest discover -s tests`.
- `templates/theme.css` and `references/analyses.{json,md}` are generated: edit
  `scripts/reporch_lib/theme.py` and `tools/catalogue_source.md` + `tools/build_catalogue.py` instead.
- Keep the repository free of personal data, real study data and third-party fonts that aren't open.
