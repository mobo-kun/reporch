"""Which analyses the user's data supports, and what to ask for when it supports too few.

The agent records the data it found as field keys (references/analyses.json "fields") in the project
state ("dataFields"). A need "a|b" is met by either field.
"""
import json
import os

REF = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "references")


def load(path=None):
    with open(path or os.path.join(REF, "analyses.json"), encoding="utf-8") as f:
        return json.load(f)


def _missing(analysis, fields):
    return [n for n in analysis["needs"] if not any(alt in fields for alt in n.split("|"))]


def possible(fields, cat=None):
    cat = cat or load()
    fields = set(fields)
    return [a for a in cat["analyses"] if not _missing(a, fields)]


def unknown_fields(fields, cat=None):
    cat = cat or load()
    return sorted(set(fields) - set(cat["fields"]))


def gaps(fields, cat=None, limit=40):
    """Analyses one field away from possible, grouped by the missing field (most analyses unlocked first).

    Returns [(need, [analysis ids it would unlock], example needsText)], for building interview questions.
    """
    cat = cat or load()
    fields = set(fields)
    by_need = {}
    for a in cat["analyses"]:
        miss = _missing(a, fields)
        if len(miss) == 1:
            by_need.setdefault(miss[0], []).append(a)
    # Gaps next to data the user already has (the analysis has other needs, all met) come first;
    # stand-alone gaps ("do you also have card-sort data?") come after.
    related = lambda items: any(len(a["needs"]) > 1 for a in items)
    ranked = sorted(by_need.items(), key=lambda kv: (not related(kv[1]), -len(kv[1]), kv[0]))
    return [(need, [a["id"] for a in items], items[0]["needsText"]) for need, items in ranked][:limit]


def summary(fields, cat=None):
    cat = cat or load()
    ok = possible(fields, cat)
    return {"possible": [a["id"] for a in ok], "count": len(ok), "enough": len(ok) >= 10,
            "unknownFields": unknown_fields(fields, cat), "gaps": gaps(fields, cat)}
