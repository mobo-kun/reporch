"""A report project: a folder in the user's own workspace, never inside the skill.

<root>/reporch-projects/<slug>/
  state.json      phase, choices, counters (resumable across sessions)
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
import shutil

STATE_SCHEMA = "reporch/state@1"
PHASES = ["collect", "interview", "analysis", "outline", "write", "translate", "build", "qa", "done"]
SUBDIRS = ["inputs", "assets", "out", "versions"]


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def project_dir(root, slug):
    return os.path.join(root, "reporch-projects", slug)


def init(root, slug, languages=("fa", "en")):
    path = project_dir(root, slug)
    if os.path.exists(os.path.join(path, "state.json")):
        raise FileExistsError(f"project {slug!r} already exists at {path}")
    for d in SUBDIRS:
        os.makedirs(os.path.join(path, d), exist_ok=True)
    state = {
        "schema": STATE_SCHEMA, "slug": slug, "created": _now(), "updated": _now(),
        "phase": PHASES[0], "phasesDone": [], "workflow": list(PHASES),
        "languages": list(languages), "brand": None, "questionsAsked": 0,
        "version": 0, "dependencies": [],
    }
    save_state(path, state)
    with open(os.path.join(path, "answers.md"), "w", encoding="utf-8") as f:
        f.write(f"# Interview: {slug}\n\n")
    return path


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
