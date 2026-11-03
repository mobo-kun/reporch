"""A report project: the folder the designer made for this study, never a folder Reporch picks.

<project>/                the designer's own folder (the agent was started in it, or --dir)
  state.json      phase, choices, counters (resumable across sessions)
  TODO.md         the study plan: phases, sub-phases, acceptance criteria (written after the interview)
  READING.md      reading ledger: every input, read fully and checked critically
  MEMORY.md       decisions, confirmed facts and preferences (read at the start of every session)
  HISTORY.md      dated log of the conversation and the work
  inputs/         the user's raw material (copied or referenced)
  assets/         fonts, logo, icons, images, video supplied by the user (never published with the skill)
  answers.md      the interview, question by question
  content.json    the report content (scripts/reporch_lib/content.py)
  out/            current outputs
  versions/vN/    earlier outputs and content, kept on every rebuild (R24)
"""
import datetime
import json
import os
import re
import shutil

STATE_SCHEMA = "reporch/state@1"
PHASES = ["collect", "interview", "plan", "analysis", "outline", "write", "translate", "build", "qa", "done"]
SUBDIRS = ["inputs", "assets", "out", "versions"]
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DELIVER = "## P9"            # TODO.md items from this heading on are ticked during delivery, after qa


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def slugify(name):
    s = re.sub(r"[^\w]+", "-", name.strip().lower(), flags=re.UNICODE).strip("-")
    return s or "study"


def init(folder, slug=None, languages=("fa", "en")):
    """Make `folder` (the designer's own folder) a Reporch project. Nothing is created anywhere else."""
    path = os.path.abspath(folder)
    if path == SKILL or path.startswith(SKILL + os.sep):
        raise ValueError(f"{path} is inside the Reporch skill folder; run Reporch in the folder you made for your study")
    if os.path.exists(os.path.join(path, "state.json")):
        raise FileExistsError(f"{path} is already a Reporch project (reporch.py status {path})")
    slug = slug or slugify(os.path.basename(path))
    for d in SUBDIRS:
        os.makedirs(os.path.join(path, d), exist_ok=True)
    state = {
        "schema": STATE_SCHEMA, "slug": slug, "created": _now(), "updated": _now(),
        "phase": PHASES[0], "phasesDone": [], "workflow": list(PHASES),
        "languages": list(languages), "brand": None, "questionsAsked": 0,
        "version": 0, "dependencies": [],
    }
    save_state(path, state)
    starters = {
        "answers.md": f"# Interview: {slug}\n\n",
        "MEMORY.md": (f"# Memory: {slug}\n\nRead this file at the start of every session. Keep it short and current: "
                      "decisions, confirmed facts, the designer's preferences. Change an entry when it changes; "
                      "the dated story goes in HISTORY.md.\n\n## Decisions\n\n## Confirmed facts\n\n"
                      "## Preferences\n\n## Open questions\n\n"),
        "HISTORY.md": (f"# History: {slug}\n\nA dated log of the conversation and the work, newest last. "
                       "Add an entry after every answer from the designer and every finished step.\n\n"),
    }
    for name, text in starters.items():
        if not os.path.exists(os.path.join(path, name)):
            _write(os.path.join(path, name), text)
    log(path, "Reporch project created in this folder.", "reporch")
    return path


def _write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _append(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


# ------------------------------------------------------------------ memory and history

MEMORY_KINDS = {"decision": "## Decisions", "fact": "## Confirmed facts", "preference": "## Preferences",
                "question": "## Open questions"}


def remember(path, text, kind="decision"):
    """Add a line under the matching heading of MEMORY.md."""
    if kind not in MEMORY_KINDS:
        raise ValueError(f"kind must be one of {sorted(MEMORY_KINDS)}")
    mem = os.path.join(path, "MEMORY.md")
    lines = _read(mem).splitlines() if os.path.exists(mem) else ["# Memory", ""]
    head = MEMORY_KINDS[kind]
    if head not in lines:
        lines += ["", head, ""]
    i = lines.index(head) + 1
    while i < len(lines) and not lines[i].startswith("## "):
        i += 1
    while i > 0 and not lines[i - 1].strip():     # insert after the section's last entry
        i -= 1
    lines.insert(i, f"- {_today()[:10]}: {text.strip()}")
    if lines[i - 1] == head:
        lines.insert(i, "")
    _write(mem, "\n".join(lines).rstrip("\n") + "\n")


def log(path, text, who="agent"):
    """Append a dated entry to HISTORY.md."""
    _append(os.path.join(path, "HISTORY.md"), f"- {_today()} · {who}: {text.strip()}\n")


# ------------------------------------------------------------------ reading ledger

def ledger(path):
    """Add every ingested input to READING.md (sizes and row counts to read against). Keeps what is filled in."""
    led = os.path.join(path, "READING.md")
    s = _read(led) if os.path.exists(led) else (
        "# Reading ledger\n\nEvery input is read to the end, then read again critically (modules/reading.md). "
        "Tick a box only when it is true. Numbers to read against come from `inputs/index.json`.\n\n")
    idx_path = os.path.join(path, "inputs", "index.json")
    index = json.loads(_read(idx_path)) if os.path.exists(idx_path) else []
    added = []
    for e in index:
        if e.get("status") != "ok" or f"## {e['file']}\n" in s:
            continue
        clean = os.path.join(path, "inputs", "clean", os.path.splitext(e["file"])[0] + ".txt")
        lines = len(_read(clean).splitlines()) if os.path.exists(clean) else 0
        tables = "; ".join(f"{t['name']}: {t['rows']} rows × {t['columns']} columns" for t in e.get("tables") or [])
        s += (f"## {e['file']}\n\n- Kind: {e['kind']} · {e['chars']} characters · {lines} lines"
              + (f" · tables: {tables}" if tables else "") + "\n"
              f"- [ ] Pass 1: read to the end (lines read: … of {lines}" + (", every table row" if tables else "") + ")\n"
              "- [ ] Pass 2: read again critically; every fact below checked against the source\n\n"
              "Facts (with locator):\n\n- …\n\nUnclear, contradictory or missing (→ question for the designer):\n\n- …\n\n")
        added.append(e["file"])
    _write(led, s)
    return added


def reading_gaps(path):
    """Inputs whose two reading passes aren't ticked in READING.md."""
    idx_path = os.path.join(path, "inputs", "index.json")
    if not os.path.exists(idx_path):
        return []
    files = [e["file"] for e in json.loads(_read(idx_path)) if e.get("status") == "ok"]
    led = os.path.join(path, "READING.md")
    s = _read(led) if os.path.exists(led) else ""
    gaps = []
    for f in files:
        i = s.find(f"## {f}\n")
        part = s[i: s.find("\n## ", i + 1) if s.find("\n## ", i + 1) != -1 else len(s)] if i != -1 else ""
        if not re.search(r"- \[[xX]\] Pass 1", part) or not re.search(r"- \[[xX]\] Pass 2", part):
            gaps.append(f)
    return gaps


# ------------------------------------------------------------------ study plan (TODO.md)

TODO_TEMPLATE = """# Study plan: {slug}

Written by Reporch after the interview, in the designer's language. Work top to bottom, one task at a
time. Tick `[x]` only when every acceptance criterion (AC) under the task is true; never skip a task.
If a task is blocked, write why under it and ask the designer. Add sub-tasks for this study (one per
section, analysis or chart) before starting each phase.

## P1 · Inputs read and understood

- [ ] 1.1 Every input read to the end (READING.md, pass 1)
  - AC: every file in READING.md has pass 1 ticked; lines and rows read equal the totals
- [ ] 1.2 Every input read again critically (pass 2)
  - AC: every fact noted has a locator (file, row, line or timestamp)
  - AC: contradictions, gaps and unclear points are written down and became questions

## P2 · Interview closed

- [ ] 2.1 All blocking questions answered and saved in answers.md
  - AC: no open blocking question; non-blocking ones have a default in state.json
- [ ] 2.2 Languages, brand, fonts, audience and outputs chosen
  - AC: each choice is in MEMORY.md

## P3 · Analyses

- [ ] 3.1 10–40 analyses chosen from what the data supports (`reporch.py possible`), list below
  - AC: each analysis names its data, its method and its evidence
- [ ] 3.2 Every number calculated with `reporch.py calc`, never by hand
  - AC: every number in content.json traces back to an input or a calculation

## P4 · Outline

- [ ] 4.1 Outline proposed and approved by the designer
  - AC: the approval is in HISTORY.md

## P5 · Writing

- [ ] 5.1 One sub-task per section (add them here), written only from the designer's content
  - AC: no claim, number or quote without evidence; wording changes were asked first
  - AC: Persian text follows `vendor/persian-writing` and passes `reporch.py falint`

## P6 · Translation

- [ ] 6.1 Second language written with the glossary
  - AC: every field has both languages; terms match the glossary

## P7 · Build

- [ ] 7.1 Report, blog and slides built (`reporch.py build`)
  - AC: `reporch.py validate --final` has no errors
- [ ] 7.2 Design checked against `modules/design.md`
  - AC: slides fit the 16:9 frame without scrolling; titles two lines or fewer
- [ ] 7.3 PDF made, if the designer wants one

## P8 · Review with the designer

- [ ] 8.1 Designer reviewed the outputs; every change they asked for is done
  - AC: the review and changes are in HISTORY.md

## P9 · Deliver

- [ ] 9.1 `reporch.py qa` passes with no errors
- [ ] 9.2 Version kept (`reporch.py snapshot`) and the files handed over
"""


def plan(path, force=False):
    """Write TODO.md from the template (the agent then tailors it to the study). Returns its path."""
    todo = os.path.join(path, "TODO.md")
    if os.path.exists(todo) and not force:
        raise FileExistsError(f"{todo} exists; edit it, or pass --force to start it again")
    _write(todo, TODO_TEMPLATE.format(slug=load_state(path)["slug"]))
    return todo


def open_tasks(path):
    """Unticked TODO.md items before the delivery phase, as (line number, text). None when there is no TODO.md."""
    todo = os.path.join(path, "TODO.md")
    if not os.path.exists(todo):
        return None
    out = []
    for n, line in enumerate(_read(todo).splitlines(), 1):
        if line.startswith(DELIVER):
            break
        if re.match(r"\s*- \[ \]", line):
            out.append((n, line.strip()[6:]))
    return out


def load_state(path):
    with open(os.path.join(path, "state.json"), encoding="utf-8") as f:
        state = json.load(f)
    if state.get("schema") != STATE_SCHEMA:
        raise ValueError(f"unknown state schema {state.get('schema')!r}")
    return state


def save_state(path, state):
    state["updated"] = _now()
    tmp = os.path.join(path, "state.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, os.path.join(path, "state.json"))


def advance(path, to=None):
    """Mark the current phase done and move to the next (or to `to`, if the user changed the flow)."""
    state = load_state(path)
    flow = state["workflow"]
    if state["phase"] not in state["phasesDone"]:
        state["phasesDone"].append(state["phase"])
    if to is None:
        i = flow.index(state["phase"])
        to = flow[min(i + 1, len(flow) - 1)]
    if to not in flow:
        raise ValueError(f"{to!r} is not in this project's workflow {flow}")
    state["phase"] = to
    save_state(path, state)
    return state


def snapshot(path):
    """Keep the current outputs and content as the next version before a rebuild. Returns the version number."""
    state = load_state(path)
    out, content = os.path.join(path, "out"), os.path.join(path, "content.json")
    if not os.path.exists(content) and not os.listdir(out):
        return state["version"]
    n = state["version"] + 1
    dest = os.path.join(path, "versions", f"v{n}")
    shutil.copytree(out, os.path.join(dest, "out"))
    if os.path.exists(content):
        shutil.copy2(content, dest)
    state["version"] = n
    save_state(path, state)
    return n


def add_dependency(path, question, default, blocking=False):
    """Record a question for the user that doesn't stop the work (blocking ones are asked at once)."""
    state = load_state(path)
    state["dependencies"].append({"question": question, "default": default, "blocking": blocking,
                                  "asked": _now(), "answer": None})
    save_state(path, state)
