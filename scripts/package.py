#!/usr/bin/env python3
"""Package the skill for installation and print release notes.

Usage:
  python3 package.py [--tag vX.Y.Z] [--out dist/]   → dist/qa-aegis-vX.Y.Z.zip
  python3 package.py --notes vX.Y.Z                 → CHANGELOG section for that version

The zip unpacks to a single `qa-aegis/` folder (SKILL.md at its root), ready to drop into a skills directory.
Built example outputs are excluded; they are attached to the release separately.
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDE = ["SKILL.md", "README.md", "LICENSE", "VERSION", "CHANGELOG.md", "requirements.txt",
           "references", "scripts", "templates", "examples", "assets"]
EXCLUDE = re.compile(r"(/out/|__pycache__|\.pyc$|\.DS_Store$)")


def version():
    return (ROOT / "VERSION").read_text().strip()


def notes(v):
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^## \[{re.escape(v)}\][^\n]*\n(.*?)(?=^## \[|\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"CHANGELOG.md has no section for {v}")
    return m.group(1).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", help="release tag; must equal v + VERSION")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--notes", metavar="TAG", help="print release notes for TAG and exit")
    a = ap.parse_args()
    v = version()
    if a.notes:
        print(notes(a.notes.lstrip("v")))
        return
    if a.tag and a.tag.lstrip("v") != v:
        sys.exit(f"tag {a.tag} does not match VERSION {v}")
    notes(v)  # fail early if the changelog was not updated
    head = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    if not re.search(r"^name:\s*qa-aegis\s*$", head, re.M):
        sys.exit("SKILL.md frontmatter must declare name: qa-aegis")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    zpath = out / f"qa-aegis-v{v}.zip"
    n = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = ROOT / item
            files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
            for f in files:
                rel = f.relative_to(ROOT).as_posix()
                if EXCLUDE.search("/" + rel):
                    continue
                z.write(f, f"qa-aegis/{rel}")
                n += 1
    print(f"{zpath} ({n} files)")


if __name__ == "__main__":
    main()
