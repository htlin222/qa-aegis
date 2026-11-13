"""Shared loading and constants for qa-aegis."""
import re
import sys
from pathlib import Path

import yaml

BRANCHES = [
    ("credible", "Credible", "Is the result true?"),
    ("applicable", "Applicable", "Does it apply to my patient?"),
    ("worth", "Worth it", "Is it worth it?"),
    ("position", "Position", "Where does it sit?"),
    ("practice", "Practice", "How do I actually give it?"),
]
PERSONAS = [
    ("ai_senior", "AI-armed senior"),
    ("statistician", "Statistician"),
    ("community", "Community oncologist"),
    ("pharmacist", "Clinical pharmacist"),
    ("payer", "Payer"),
]
CYNEFIN = [
    ("clear", "Clear", "The data are clear: …"),
    ("complicated", "Complicated", "It depends on X — here's how I decide…"),
    ("complex", "Complex", "We don't have data for that. My reasoning is…"),
    ("chaotic", "Chaotic", "Let me take the part I can answer with data first…"),
    ("confused", "Confused", "If I understand correctly, you're asking…"),
]
BRANCH_IDS = [b[0] for b in BRANCHES]
PERSONA_IDS = [p[0] for p in PERSONAS]
CYNEFIN_IDS = [c[0] for c in CYNEFIN]
BRANCH_LABEL = {b[0]: b[1] for b in BRANCHES}
BRANCH_ROOT = {b[0]: b[2] for b in BRANCHES}
PERSONA_LABEL = dict(PERSONAS)
CYNEFIN_LABEL = {c[0]: c[1] for c in CYNEFIN}
CYNEFIN_OPENER = {c[0]: c[2] for c in CYNEFIN}

TARGETS = {"total": 50, "per_branch": 8, "per_persona": 6, "practice": 12}


def load(path):
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.setdefault("meta", {})
    data.setdefault("sources", [])
    data.setdefault("dose_table", [])
    data.setdefault("questions", [])
    data["_dir"] = path.parent
    for q in data["questions"]:
        q.setdefault("followups", [])
        q.setdefault("sources", [])
        q.setdefault("verify", "")
        for k in ("q", "answer", "principle", "ai_answer", "blind_spot", "oneliner"):
            if isinstance(q.get(k), str):
                q[k] = re.sub(r"\s+", " ", q[k]).strip()
    return data


def ordered(questions):
    bi = {b: i for i, b in enumerate(BRANCH_IDS)}
    return sorted(questions, key=lambda q: (bi.get(q["branch"], 99), q["id"]))


def top(questions, n=10):
    bi = {b: i for i, b in enumerate(BRANCH_IDS)}
    return sorted(questions, key=lambda q: (-int(q.get("risk", 0)), bi.get(q["branch"], 99), q["id"]))[:n]


def oneliner(q, limit=170):
    """Short answer for the Top 10 and pocket card: explicit field, else first informative sentences."""
    if q.get("oneliner"):
        return q["oneliner"]
    sents = re.split(r"(?<=[.!?])\s+", q["answer"])
    out = ""
    for s in sents:
        if not out and len(s) < 45 and s.lower().startswith(("it depends", "fair", "right", "not quite", "yes", "no", "not yet", "the data are clear", "let me")):
            continue
        if len(out) + len(s) > limit and out:
            break
        out = (out + " " + s).strip()
    return out[: limit + 40]


def die(msg):
    sys.exit(f"qa-aegis: {msg}")
