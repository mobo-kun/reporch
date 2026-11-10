"""content.json: the single source of truth for one report.

Every user-facing text is a dict of language code -> string, so one file holds all languages and each
output document is rendered in one language. `validate(doc, stage)` returns a list of Problems; the
build refuses to run while any problem has level "error".

Stages: "draft" (while writing; missing translations and too few analyses are warnings) and "final"
(before building outputs; they become errors).
"""
import json
import re

SCHEMA_ID = "reporch/content@1"

# Section roles in their fixed order (references/outline.md). Required roles must appear.
ROLES = ["summary", "context", "method", "participants", "problem", "solution", "result",
         "actionPlan", "limitations", "appendix"]
REQUIRED_ROLES = ["summary", "problem", "solution", "result"]

BLOCK_TYPES = {
    "heading": ["text"],
    "paragraph": ["text"],
    "callout": ["tone", "text"],
    "quote": ["text", "participant"],
    "stats": ["items"],
    "table": ["columns", "rows"],
    "chart": ["chart", "table"],
    "image": ["caption"],
    "video": ["caption"],
    "list": ["items"],
    "analysis": ["analysis"],
    "actionPlan": ["items"],
    "persona": ["name", "text"],
    "flow": ["steps"],
    "timeline": ["items"],
    "pending": ["text"],
    "compare": ["before", "after"],
}
STUDY_TYPES = {"redesign", "current-state", "new", "other"}
CALLOUT_TONES = {"info", "warn", "critical", "success"}
CHART_KINDS = {"bar", "barHorizontal", "stackedBar", "line", "doughnut", "scatter", "funnel", "heatmap",
               "radar", "box", "rangeBar", "sankey"}
PARTICIPANT_ID = re.compile(r"^P\d{2,}$")
ANALYSES_MIN, ANALYSES_MAX = 10, 40


class Problem:
    def __init__(self, level, where, message):
        self.level, self.where, self.message = level, where, message

    def __repr__(self):
        return f"{self.level.upper()} {self.where}: {self.message}"


ROLE_ONLY = re.compile(r"(?i)(product |ux |ui |senior |lead )*(designer|researcher|طراح( محصول)?|پژوهشگر|محقق)( \S+)?")


def _walk_sections(sections, path="sections"):
    for i, s in enumerate(sections or []):
        here = f"{path}[{i}]"
        yield here, s
        yield from _walk_sections(s.get("children"), here + ".children")


def _texts(obj, where):
    """Yield (where, localized dict) for every localized text inside obj."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("text", "title", "caption", "label", "note", "name", "finding", "description", "value",
                     "headline", "alt", "dek") and isinstance(v, dict):
                yield f"{where}.{k}", v
            elif isinstance(v, (dict, list)):
                yield from _texts(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _texts(v, f"{where}[{i}]")


def validate(doc, stage="draft"):
    out = []
    err = lambda w, m: out.append(Problem("error", w, m))
    soft = lambda w, m: out.append(Problem("error" if stage == "final" else "warning", w, m))

    if doc.get("schema") != SCHEMA_ID:
        err("schema", f"must be {SCHEMA_ID!r}")
    meta = doc.get("meta") or {}
    langs = meta.get("languages") or []
    if not langs or not all(isinstance(l, str) and re.fullmatch(r"[a-z]{2}", l) for l in langs):
        err("meta.languages", "list one or two ISO 639-1 codes, e.g. ['fa', 'en']")
    if len(langs) > 2:
        err("meta.languages", "at most two languages")
    for key in ("title", "slug", "authors"):
        if not meta.get(key):
            err(f"meta.{key}", "required")
    for i, au in enumerate(meta.get("authors") or []):
        name = au.get("name") if isinstance(au, dict) else None
        texts = list(name.values()) if isinstance(name, dict) else [name or ""]
        if any(not str(t).strip() or ROLE_ONLY.fullmatch(str(t).strip()) for t in texts):
            out.append(Problem("warning", f"meta.authors[{i}].name", "ask the designer's own name (a role goes in 'role')"))
    if meta.get("slug") and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["slug"]):
        err("meta.slug", "lowercase words joined by hyphens")
    if meta.get("studyType") not in (None, *STUDY_TYPES):
        err("meta.studyType", " , ".join(sorted(STUDY_TYPES)))
    if meta.get("studyType") == "redesign" and '"compare"' not in json.dumps(doc.get("sections") or []):
        out.append(Problem("warning", "sections", "a redesign study has no before/after comparison: ask the designer "
                                                  "for the old and new design (shots or videos) and add a compare block"))
    if meta.get("studyGoal") not in (None, "formative", "summative", "mixed"):
        err("meta.studyGoal", "formative, summative or mixed")

    # Localized texts: every language present, none empty.
    for where, t in _texts(doc, "$"):
        if t.get("_pendingTranslation"):
            soft(where, "translation pending")
            continue
        for l in langs:
            if not (isinstance(t.get(l), str) and t[l].strip()):
                soft(where, f"missing {l!r} text")

    # Participants are anonymised.
    pids = set()
    for i, p in enumerate(doc.get("participants") or []):
        pid = p.get("id", "")
        if not PARTICIPANT_ID.match(pid):
            err(f"participants[{i}].id", f"{pid!r} is not an anonymised id like P01")
        if pid in pids:
            err(f"participants[{i}].id", f"duplicate {pid}")
        pids.add(pid)

    evidence = {}
    for i, e in enumerate(doc.get("evidence") or []):
        if not e.get("id") or not e.get("source"):
            err(f"evidence[{i}]", "id and source are required")
        if e.get("id") in evidence:
            err(f"evidence[{i}].id", f"duplicate {e['id']}")
        if e.get("participant") and e["participant"] not in pids:
            err(f"evidence[{i}].participant", f"unknown participant {e['participant']}")
        evidence[e.get("id")] = e

    analyses = {}
    for i, a in enumerate(doc.get("analyses") or []):
        w = f"analyses[{i}]"
        for key in ("id", "catalogueId", "title", "finding"):
            if not a.get(key):
                err(f"{w}.{key}", "required")
        if a.get("id") in analyses:
            err(f"{w}.id", f"duplicate {a['id']}")
        if not a.get("evidence"):
            err(f"{w}.evidence", "every analysis links to its evidence")
        analyses[a.get("id")] = a
        _check_refs(a, w, evidence, err)
        if a.get("chart"):
            _check_chart(a["chart"], a.get("table"), w, err)
    n = len(analyses)
    if not ANALYSES_MIN <= n <= ANALYSES_MAX:
        soft("analyses", f"{n} analyses; a report needs {ANALYSES_MIN}-{ANALYSES_MAX}")

    # Sections: known roles, fixed order, required ones present.
    seen_roles, ids = [], set()
    top = doc.get("sections") or []
    for where, s in _walk_sections(top):
        if not s.get("id"):
            err(where, "id required")
        elif s["id"] in ids:
            err(where, f"duplicate section id {s['id']}")
        ids.add(s.get("id"))
        for j, b in enumerate(s.get("blocks") or []):
            _check_block(b, f"{where}.blocks[{j}]", pids, evidence, analyses, err)
    for i, s in enumerate(top):
        role = s.get("role")
        if role not in ROLES:
            err(f"sections[{i}].role", f"{role!r} is not one of {ROLES}")
        else:
            seen_roles.append(role)
    order = [ROLES.index(r) for r in seen_roles]
    if order != sorted(order):
        err("sections", "top-level sections must follow the outline order: " + " → ".join(ROLES))
    for r in REQUIRED_ROLES:
        if r not in seen_roles:
            err("sections", f"missing required section {r!r}")

    blog = doc.get("blog")
    if not blog:
        soft("blog", "the blog post is missing")
    else:
        if not blog.get("title"):
            err("blog.title", "required")
        for i, s in enumerate(blog.get("sections") or []):
            for j, b in enumerate(s.get("blocks") or []):
                _check_block(b, f"blog.sections[{i}].blocks[{j}]", pids, evidence, analyses, err)
        if not blog.get("sections"):
            soft("blog.sections", "the blog post has no sections")

    used = {b.get("analysis") for _, s in _walk_sections(top) for b in s.get("blocks") or []}
    for aid in analyses:
        if aid not in used:
            soft(f"analyses.{aid}", "not placed in any section")
    return out


def _check_refs(obj, where, evidence, err):
    for ref in obj.get("evidence") or []:
        if ref not in evidence:
            err(f"{where}.evidence", f"unknown evidence {ref}")


def _check_chart(chart, table, where, err):
    if chart.get("kind") not in CHART_KINDS:
        err(f"{where}.chart.kind", f"{chart.get('kind')!r} is not one of {sorted(CHART_KINDS)}")
    if not table:
        err(f"{where}.table", "every chart has its source table (charts must match their data)")
        return
    cols = table.get("columns") or []
    rows = table.get("rows") or []
    for k, row in enumerate(rows):
        if len(row) != len(cols):
            err(f"{where}.table.rows[{k}]", f"{len(row)} cells for {len(cols)} columns")
    needed = [chart.get("x"), *chart.get("series", []), *chart.get("range", []), *chart.get("box", [])]
    needed += [chart[k] for k in ("y", "target") if k in chart]
    if chart.get("kind") == "heatmap" and "y" not in chart:
        err(f"{where}.chart.y", "a heatmap names its y column")
    if chart.get("kind") == "sankey" and "target" not in chart:
        err(f"{where}.chart.target", "a sankey names its target column")
    if chart.get("kind") == "box" and len(chart.get("box", [])) != 5:
        err(f"{where}.chart.box", "a box plot names five columns: min, q1, median, q3, max")
    for key in needed:
        if key is None:
            err(f"{where}.chart", "x and series name table columns")
        elif key not in cols:
            err(f"{where}.chart", f"column {key!r} is not in the table")


def _check_block(b, where, pids, evidence, analyses, err):
    t = b.get("type")
    if t not in BLOCK_TYPES:
        err(where, f"unknown block type {t!r}")
        return
    for key in BLOCK_TYPES[t]:
        if key not in b:
            err(f"{where}.{key}", "required")
    _check_refs(b, where, evidence, err)
    if t == "callout" and b.get("tone") not in CALLOUT_TONES:
        err(f"{where}.tone", f"one of {sorted(CALLOUT_TONES)}")
    if t == "quote":
        if b.get("participant") not in pids:
            err(f"{where}.participant", f"unknown participant {b.get('participant')}")
        if not b.get("evidence"):
            err(f"{where}.evidence", "a quote needs its evidence (no invented quotes)")
    if t == "analysis" and b.get("analysis") not in analyses:
        err(f"{where}.analysis", f"unknown analysis {b.get('analysis')}")
    if t == "chart":
        _check_chart(b.get("chart") or {}, b.get("table"), where, err)
    if t == "table":
        cols = b.get("columns") or []
        for k, row in enumerate(b.get("rows") or []):
            if len(row) != len(cols):
                err(f"{where}.rows[{k}]", f"{len(row)} cells for {len(cols)} columns")
    if t == "compare":
        for side in ("before", "after"):
            s = b.get(side) or {}
            if not s.get("src") and not s.get("placeholder"):
                err(f"{where}.{side}", "needs src (a file in assets/) or a placeholder describing the shot needed")
    if t in ("image", "video"):
        if not b.get("src") and not b.get("placeholder"):
            err(where, "needs src (a file in assets/) or a placeholder describing the image needed")
        ph = b.get("placeholder")
        if ph and (ph.get("kind") not in PLACEHOLDER_KINDS or not ph.get("description")):
            err(f"{where}.placeholder", f"kind (one of {sorted(PLACEHOLDER_KINDS)}) and description required")


PLACEHOLDER_KINDS = {"design", "screenshot", "analytics", "illustration", "wireframe", "photo", "diagram",
                     "video", "logo", "other"}


def errors(problems):
    return [p for p in problems if p.level == "error"]
