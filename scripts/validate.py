#!/usr/bin/env python3
"""Validate a qa-aegis question bank: schema, coverage grid, sources, unverified items.

Usage: python3 validate.py qa.yaml [--strict]
Exit code 1 on schema errors (and on coverage gaps with --strict).
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (BRANCH_IDS, BRANCH_LABEL, CYNEFIN_IDS, PERSONA_IDS, PERSONA_LABEL,  # noqa: E402
                    TARGETS, load)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml")
    ap.add_argument("--strict", action="store_true", help="fail on coverage gaps too")
    a = ap.parse_args()
    d = load(a.yaml)
    qs = d["questions"]
    src_ids = {s["id"] for s in d["sources"]}
    errors, warns = [], []

    seen = set()
    for q in qs:
        qid = q.get("id", "?")
        if qid in seen:
            errors.append(f"{qid}: duplicate id")
        seen.add(qid)
        for f in ("branch", "persona", "cynefin", "risk", "q", "principle", "answer"):
            if not q.get(f):
                errors.append(f"{qid}: missing {f}")
        if q.get("branch") not in BRANCH_IDS:
            errors.append(f"{qid}: branch '{q.get('branch')}' not in {BRANCH_IDS}")
        if q.get("persona") not in PERSONA_IDS:
            errors.append(f"{qid}: persona '{q.get('persona')}' not in {PERSONA_IDS}")
        if q.get("cynefin") not in CYNEFIN_IDS:
            errors.append(f"{qid}: cynefin '{q.get('cynefin')}' not in {CYNEFIN_IDS}")
        if not 1 <= int(q.get("risk", 0)) <= 5:
            errors.append(f"{qid}: risk must be 1-5")
        if q.get("persona") == "ai_senior" and not (q.get("ai_answer") and q.get("blind_spot")):
            errors.append(f"{qid}: ai_senior questions need ai_answer and blind_spot")
        if int(q.get("risk", 0)) >= 4 and not q.get("followups"):
            warns.append(f"{qid}: risk ≥4 without follow-ups")
        if not q.get("sources") and q.get("cynefin") not in ("complex", "confused") and not q.get("verify"):
            errors.append(f"{qid}: no sources and no verify note")
        for s in q.get("sources", []):
            if s not in src_ids:
                errors.append(f"{qid}: unknown source '{s}'")
        words = len(q.get("answer", "").split())
        if words > 120:
            warns.append(f"{qid}: answer is {words} words (aim ≤100 for 30 s)")
    for r in d["dose_table"]:
        if r.get("source") and r["source"] not in src_ids:
            errors.append(f"dose_table '{r.get('item')}': unknown source '{r['source']}'")

    # coverage grid
    grid = Counter((q["branch"], q["persona"]) for q in qs)
    bcount = Counter(q["branch"] for q in qs)
    pcount = Counter(q["persona"] for q in qs)
    ccount = Counter(q["cynefin"] for q in qs)
    w = 13
    print(f"\nCoverage — {len(qs)} questions\n")
    print(" " * w + "".join(f"{p[:11]:>12}" for p in PERSONA_IDS) + f"{'total':>8}")
    for b in BRANCH_IDS:
        row = "".join(f"{(grid[(b, p)] or '·'):>12}" for p in PERSONA_IDS)
        print(f"{b:<{w}}{row}{bcount[b]:>8}")
    print(f"{'total':<{w}}" + "".join(f"{pcount[p]:>12}" for p in PERSONA_IDS))
    print("\nCynefin: " + ", ".join(f"{c} {ccount[c]}" for c in CYNEFIN_IDS))
    print("Risk:    " + ", ".join(f"{r}★ {sum(1 for q in qs if int(q['risk']) == r)}" for r in (5, 4, 3, 2, 1)))

    gaps = []
    if len(qs) < TARGETS["total"]:
        gaps.append(f"total {len(qs)} < {TARGETS['total']}")
    for b in BRANCH_IDS:
        need = TARGETS["practice"] if b == "practice" else TARGETS["per_branch"]
        if bcount[b] < need:
            gaps.append(f"branch {BRANCH_LABEL[b]}: {bcount[b]} < {need}")
    for p in PERSONA_IDS:
        if pcount[p] < TARGETS["per_persona"]:
            gaps.append(f"persona {PERSONA_LABEL[p]}: {pcount[p]} < {TARGETS['per_persona']}")
    empty = [f"{b}×{p}" for b in BRANCH_IDS for p in PERSONA_IDS if not grid[(b, p)]]

    unverified = [(q["id"], q["verify"]) for q in qs if q.get("verify")]
    unverified += [(f"dose:{r['item']}", r["verify"]) for r in d["dose_table"] if r.get("verify")]

    print("\nCoverage gaps: " + ("; ".join(gaps) if gaps else "none"))
    print("Empty cells:   " + (", ".join(empty) if empty else "none"))
    print(f"\n⚠ UNVERIFIED ({len(unverified)}):")
    for k, v in unverified:
        print(f"  {k}: {v}")
    if warns:
        print(f"\nWarnings ({len(warns)}):")
        for x in warns:
            print("  " + x)
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for x in errors:
            print("  " + x)
    sys.exit(1 if errors or (a.strict and gaps) else 0)


if __name__ == "__main__":
    main()
