#!/usr/bin/env python3
"""Smoke-test built outputs against their YAML source. Used by CI.

Usage: python3 check_outputs.py qa.yaml out/
Checks: every output exists; every question has a PPTX slide and an HTML card;
the contents slide links resolve; the pocket card is exactly one page.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load  # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    d = load(sys.argv[1])
    out = Path(sys.argv[2])
    ids = [q["id"] for q in d["questions"]]
    fails = []

    for f in ("kit.html", "kit.pptx", "pocket.pdf"):
        if not (out / f).is_file() or (out / f).stat().st_size == 0:
            fails.append(f"missing or empty: {f}")
    if fails:
        sys.exit("\n".join(fails))

    page = (out / "kit.html").read_text(encoding="utf-8")
    missing = [i for i in ids if f'id="{i}"' not in page]
    if missing:
        fails.append(f"HTML missing cards: {missing}")

    from pptx import Presentation
    prs = Presentation(out / "kit.pptx")
    notes = [s.notes_slide.notes_text_frame.text if s.has_notes_slide else "" for s in prs.slides]
    missing = [i for i in ids if not any(n.startswith(f"[{i}]") for n in notes)]
    if missing:
        fails.append(f"PPTX missing question slides: {missing}")
    toc = prs.slides[1]
    links = [sh.click_action.target_slide for sh in toc.shapes if sh.click_action.target_slide is not None]
    if len(links) < 6:
        fails.append(f"PPTX contents has only {len(links)} links")

    from pypdf import PdfReader
    pages = len(PdfReader(out / "pocket.pdf").pages)
    if pages != 1:
        fails.append(f"pocket.pdf has {pages} pages (must be 1)")

    print(f"{len(ids)} questions · {len(prs.slides)} slides · {len(links)} contents links · pocket {pages} page")
    if fails:
        sys.exit("FAIL\n" + "\n".join(fails))
    print("OK")


if __name__ == "__main__":
    main()
