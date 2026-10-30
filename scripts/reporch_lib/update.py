"""Optional update check: one request to GitHub, only after the user agrees, at most once a day.

The answer is stored in ~/.config/reporch/settings.json ("updateCheck": true/false). Nothing about the
user or their projects is sent; the request only asks GitHub for Reporch's latest release.
"""
import json
import os
import time
import urllib.request

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
API = "https://api.github.com/repos/mobo-kun/reporch/releases/latest"
CONFIG = os.path.join(os.path.expanduser("~"), ".config", "reporch", "settings.json")


def current():
    with open(os.path.join(SKILL, "VERSION"), encoding="utf-8") as f:
        return f.read().strip()


def settings(path=CONFIG):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(values, path=CONFIG):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = settings(path) | values
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


def _parse(v):
    return tuple(int(x) for x in v.lstrip("v").split("-")[0].split(".") if x.isdigit())


def newer(latest, mine):
    return _parse(latest) > _parse(mine)


def check(path=CONFIG, fetch=None, now=None):
    """Returns {"status": "off"|"asked-recently"|"current"|"update"|"error", …}."""
    s = settings(path)
    if s.get("updateCheck") is not True:
        return {"status": "off", "message": "Update check is off. Ask the user first, then: reporch.py settings update-check on"}
    now = now or time.time()
    if s.get("lastCheck") is not None and now - s["lastCheck"] < 86400:
        return {"status": "asked-recently", "latest": s.get("latest"), "current": current()}
    try:
        if fetch:
            latest = fetch()
        else:
            req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json", "User-Agent": "reporch"})
            with urllib.request.urlopen(req, timeout=5) as r:
                latest = json.load(r)["tag_name"]
    except Exception as e:  # network, rate limit, no release yet
        return {"status": "error", "message": f"could not check for updates: {e}"}
    save_settings({"lastCheck": now, "latest": latest}, path)
    mine = current()
    if newer(latest, mine):
        return {"status": "update", "latest": latest, "current": mine,
                "message": f"Reporch {latest} is available (you have {mine}). Update: git -C \"{SKILL}\" pull --ff-only"}
    return {"status": "current", "latest": latest, "current": mine}
