#!/usr/bin/env python3
"""Build the Q&A defense kit from one YAML source.

Usage: python3 build.py qa.yaml --out out/ [--only html,pptx,pdf]

Outputs: kit.html (self-contained), kit.pptx (with linked contents), pocket.pdf (one A4 page).
Requires: pyyaml, jinja2, python-pptx; optional: @argdown/cli + rsvg-convert (argument map), playwright (PDF).
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (BRANCH_IDS, BRANCH_LABEL, BRANCH_ROOT, BRANCHES, CYNEFIN,  # noqa: E402
                    CYNEFIN_LABEL, PERSONA_IDS, PERSONA_LABEL, PERSONAS, load, oneliner, ordered, top)

ROOT = Path(__file__).resolve().parent.parent
TAGS = ("rebut", "undercut", "undermine", "reply", "concede")


# ───────────────────────── context ─────────────────────────
def context(d):
    qs = ordered(d["questions"])
    for q in qs:
        q["_one"] = oneliner(q)
    grid = {b: Counter() for b in BRANCH_IDS}
    for q in qs:
        grid[q["branch"]][q["persona"]] += 1
    branches = [{"id": b, "label": BRANCH_LABEL[b], "root": BRANCH_ROOT[b],
                 "questions": [q for q in qs if q["branch"] == b]} for b in BRANCH_IDS]
    for b in branches:
        b["n"] = len(b["questions"])
    personas = [{"id": p, "label": PERSONA_LABEL[p], "n": sum(1 for q in qs if q["persona"] == p)} for p in PERSONA_IDS]
    cyn = [{"id": c, "label": l, "opener": o, "ids": [q["id"] for q in qs if q["cynefin"] == c]} for c, l, o in CYNEFIN]
    unverified = [(q["id"], q["verify"]) for q in qs if q.get("verify")]
    unverified += [(f"Dose: {r['item']}", r["verify"]) for r in d["dose_table"] if r.get("verify")]
    return {
        "meta": d["meta"], "questions": qs, "branches": branches, "personas": personas, "cynefin": cyn,
        "grid": grid, "top10": top(qs, 10), "dose_table": d["dose_table"], "sources": d["sources"],
        "src": {s["id"]: s for s in d["sources"]}, "unverified": unverified, "qids": {q["id"] for q in qs},
        "persona_label": PERSONA_LABEL, "cynefin_label": CYNEFIN_LABEL, "nq": len(qs),
    }


# ───────────────────────── argument map ─────────────────────────
def split_claims(text):
    """Split an Argdown file into one block per top-level [claim] so each map stays legible."""
    blocks, cur = [], []
    for line in text.splitlines():
        if line.startswith("[") and cur:
            blocks.append("\n".join(cur))
            cur = []
        if line.strip():
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def render_map(d, work):
    """Return (list of {title, svg, png}, fallback_text)."""
    rel = d["meta"].get("argdown")
    if not rel:
        return [], ""
    src = (d["_dir"] / rel).resolve()
    text = src.read_text(encoding="utf-8")
    argdown = shutil.which("argdown")
    if not argdown:
        return [{"title": "Argument map", "svg": f"<pre>{html.escape(text)}</pre>", "png": None}], text
    maps = []
    for i, block in enumerate(split_claims(text)):
        m = re.match(r"\[([^\]]+)\]", block)
        name = m.group(1) if m else f"Claim {i + 1}"
        f = work / f"claim{i}.argdown"
        f.write_text(block + "\n", encoding="utf-8")
        out = work / f"ad{i}"
        out.mkdir(exist_ok=True)
        r = subprocess.run([argdown, "map", str(f), str(out), "--format", "svg"], capture_output=True, text=True)
        svgs = list(out.glob("*.svg"))
        if r.returncode or not svgs:
            print("argdown failed, using text:", r.stderr[-300:], file=sys.stderr)
            maps.append({"title": name, "svg": f"<pre>{html.escape(block)}</pre>", "png": None, "text": block})
            continue
        svg = monochrome_svg(svgs[0].read_text(encoding="utf-8"))
        svgs[0].write_text(svg, encoding="utf-8")
        png = work / f"map{i}.png"
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-z", "2.2", "-b", "white", str(svgs[0]), "-o", str(png)], check=False)
        first = block.splitlines()[0].split(":", 1)[-1].strip()
        maps.append({"title": name, "claim": first, "svg": re.sub(r"^.*?(<svg)", r"\1", svg, flags=re.S),
                     "png": png if png.exists() else None, "text": block})
    return maps, text


def monochrome_svg(svg):
    """House style: white nodes, black outlines and text; keep green/red support/attack arrows."""
    def node_fill(m):
        return m.group(0).replace(m.group(1), "#ffffff")
    svg = re.sub(r'<path fill="(#[0-9a-fA-F]{6})" stroke="[^"]*"', lambda m: f'<path fill="#ffffff" stroke="#111111"', svg)
    svg = re.sub(r'<polygon fill="(#[0-9a-fA-F]{6})" stroke="none"', lambda m: m.group(0) if m.group(1).lower() in ("#ffffff",) else m.group(0), svg)
    svg = re.sub(r'fill="#ffffff" stroke="#[0-9a-fA-F]{6}" stroke-width="3"', 'fill="#ffffff" stroke="#111111" stroke-width="3"', svg)
    svg = re.sub(r'<text([^>]*?) fill="#[0-9a-fA-F]{6}"', r'<text\1 fill="#111111"', svg)
    for t in TAGS:
        svg = svg.replace(f" #{t}", f" [{t}]")
    return svg


# ───────────────────────── HTML ─────────────────────────
def jinja():
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    return Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape(["html", "j2"]))


def build_html(ctx, out, maps):
    page = jinja().get_template("kit.html.j2").render(**ctx, maps=maps)
    (out / "kit.html").write_text(page, encoding="utf-8")
    return out / "kit.html"


def build_pdf(ctx, out, work):
    page = jinja().get_template("pocket.html.j2").render(**ctx)
    tmp = work / "pocket.html"
    tmp.write_text(page, encoding="utf-8")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed; pocket.html written instead of PDF", file=sys.stderr)
        shutil.copy(tmp, out / "pocket.html")
        return out / "pocket.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(tmp.as_uri())
        pg.pdf(path=str(out / "pocket.pdf"), format="A4", landscape=True, print_background=True,
               margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"})
        b.close()
    return out / "pocket.pdf"


# ───────────────────────── PPTX ─────────────────────────
def build_pptx(ctx, out, maps):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Emu, Inches, Pt

    INK, WHITE, MUTE, RULE, WARN = (RGBColor(0x11, 0x11, 0x11), RGBColor(0xFF, 0xFF, 0xFF),
                                    RGBColor(0x55, 0x55, 0x55), RGBColor(0xCC, 0xCC, 0xCC), RGBColor(0x9A, 0x34, 0x12))
    FONT = "Arial"
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    blank = prs.slide_layouts[6]
    M = Inches(0.55)
    meta = ctx["meta"]
    toc_targets = []      # (label, slide)
    back_links = []       # shapes to link back to contents

    def box(slide, x, y, w, h, fill=None, line=None):
        from pptx.enum.shapes import MSO_SHAPE
        s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        if fill is None:
            s.fill.background()
        else:
            s.fill.solid()
            s.fill.fore_color.rgb = fill
        if line is None:
            s.line.fill.background()
        else:
            s.line.color.rgb = line
            s.line.width = Pt(0.75)
        s.shadow.inherit = False
        return s

    def text(slide, x, y, w, h, runs, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             fill=None, spacing=1.12, pad=0.04):
        """runs: str, or list of paragraphs; each paragraph a str or list of (text, {opts})."""
        s = box(slide, x, y, w, h, fill=fill) if fill is not None else slide.shapes.add_textbox(x, y, w, h)
        tf = s.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        for side in ("left", "right", "top", "bottom"):
            setattr(tf, f"margin_{side}", Inches(pad if fill is None else 0.12))
        paras = runs if isinstance(runs, list) else [runs]
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            segs = para if isinstance(para, list) else [(para, {})]
            for seg, opt in segs:
                r = p.add_run()
                r.text = seg
                f = r.font
                f.name = FONT
                f.size = Pt(opt.get("size", size))
                f.bold = opt.get("bold", bold)
                f.italic = opt.get("italic", False)
                f.color.rgb = opt.get("color", color)
            if isinstance(para, list) and para and para[0][1].get("space_after") is not None:
                p.space_after = Pt(para[0][1]["space_after"])
        return s

    def footer(slide, label, n):
        text(slide, M, H - Inches(0.42), Inches(8), Inches(0.3), label, size=9, color=MUTE)
        b = text(slide, W - Inches(3.0), H - Inches(0.42), Inches(1.6), Inches(0.3), "◂ Contents", size=9, color=MUTE,
                 align=PP_ALIGN.RIGHT)
        back_links.append(b)
        text(slide, W - Inches(1.3), H - Inches(0.42), Inches(0.75), Inches(0.3), str(n), size=9, color=MUTE,
             align=PP_ALIGN.RIGHT)

    def title(slide, t, kicker=None):
        if kicker:
            text(slide, M, Inches(0.35), W - 2 * M, Inches(0.3), kicker.upper(), size=10, color=MUTE, bold=True)
        text(slide, M, Inches(0.6), W - 2 * M, Inches(0.8), t, size=26, bold=True)
        ln = slide.shapes.add_connector(1, M, Inches(1.38), W - M, Inches(1.38))
        ln.line.color.rgb = INK
        ln.line.width = Pt(1.5)

    def new(label):
        s = prs.slides.add_slide(blank)
        footer(s, label, len(prs.slides))
        return s

    def table(slide, x, y, w, rows, colw, size=11, header=True, rowh=0.3):
        nr, nc = len(rows), len(rows[0])
        shp = slide.shapes.add_table(nr, nc, x, y, w, Inches(rowh * nr))
        tb = shp.table
        tbl_pr = shp._element.graphic.graphicData.tbl
        style = tbl_pr.tblPr
        style.set("bandRow", "0")
        style.set("firstRow", "0")
        for i, cw in enumerate(colw):
            tb.columns[i].width = Emu(int(w * cw))
        for r, row in enumerate(rows):
            tb.rows[r].height = Inches(rowh)
            for c, val in enumerate(row):
                cell = tb.cell(r, c)
                cell.fill.background()
                cell.margin_left = cell.margin_right = Inches(0.06)
                cell.margin_top = cell.margin_bottom = Inches(0.03)
                tf = cell.text_frame
                tf.word_wrap = True
                segs = val if isinstance(val, list) else [(str(val), {})]
                p = tf.paragraphs[0]
                for seg, opt in segs:
                    rr = p.add_run()
                    rr.text = seg
                    rr.font.name = FONT
                    rr.font.size = Pt(opt.get("size", size))
                    rr.font.bold = opt.get("bold", header and r == 0)
                    rr.font.color.rgb = opt.get("color", INK)
                _rule(cell, bottom=True, heavy=(header and r == 0))
        return shp

    def _rule(cell, bottom=True, heavy=False):
        from pptx.oxml.ns import qn
        from lxml import etree
        tcPr = cell._tc.get_or_add_tcPr()
        for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
            el = tcPr.find(qn(tag))
            if el is not None:
                tcPr.remove(el)
        for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
            ln = etree.SubElement(tcPr, qn(tag))
            if tag == "a:lnB":
                ln.set("w", str(Pt(1.25 if heavy else 0.5)))
                sf = etree.SubElement(ln, qn("a:solidFill"))
                c = etree.SubElement(sf, qn("a:srgbClr"))
                c.set("val", "111111" if heavy else "CCCCCC")
            else:
                ln.set("w", "0")
                etree.SubElement(ln, qn("a:noFill"))

    def notes(slide, paras):
        slide.notes_slide.notes_text_frame.text = "\n\n".join(paras)


    def est(s, w_in, size, spacing=1.15):
        """Estimated height (in) of wrapped Arial text."""
        import math
        cpl = max(8, int(w_in * 72 / (size * 0.58)))
        lines = sum(max(1, math.ceil(len(par) / cpl)) for par in s.split("\n"))
        return lines * size * spacing / 72 + 0.12

    LW, RX = 7.75, 8.75
    RW = 13.333 - RX - 0.55

    def question_slide(q):
        s = new(f"{q['id']} · {BRANCH_LABEL[q['branch']]}")
        risk = int(q["risk"])
        chips = [(f"{q['id']}", {"bold": True, "color": INK}),
                 (f"   {BRANCH_LABEL[q['branch']]} · {PERSONA_LABEL[q['persona']]} · {CYNEFIN_LABEL[q['cynefin']]}"
                  + (f" · {q['attack']}" if q.get("attack") else "") + f"   {'●' * risk}{'○' * (5 - risk)}", {})]
        if q.get("verify"):
            chips.append(("    ⚠ UNVERIFIED", {"bold": True, "color": WARN}))
        text(s, M, Inches(0.32), W - 2 * M, Inches(0.3), [chips], size=11, color=MUTE)
        tsize = 24 if len(q["q"]) < 90 else 20 if len(q["q"]) < 140 else 17
        text(s, M, Inches(0.62), W - 2 * M, Inches(1.15), q["q"], size=tsize, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        ln = s.shapes.add_connector(1, M, Inches(1.85), W - M, Inches(1.85))
        ln.line.color.rgb = INK
        ln.line.width = Pt(1.5)

        # left column: principle, answer, follow-ups
        avail = 7.5 - 2.05 - 0.6
        fu = q.get("followups") or []
        for size in (15, 14, 13, 12, 11, 10):
            hp = est(q["principle"], LW - 0.3, size) + 0.15
            ha = est(q["answer"], LW, size)
            hf = sum(est(f["q"] + " " + f["a"], LW - 0.2, size - 1) for f in fu) + (0.3 if fu else 0)
            if hp + ha + hf + 0.55 <= avail:
                break
        y = 2.05
        text(s, M, Inches(y), Inches(LW), Inches(0.22), "FIRST PRINCIPLE", size=9, color=MUTE, bold=True)
        y += 0.24
        text(s, M, Inches(y), Inches(LW), Inches(hp), q["principle"], size=size, color=WHITE, bold=True, fill=INK)
        y += hp + 0.12
        text(s, M, Inches(y), Inches(LW), Inches(0.22), "30-SECOND ANSWER", size=9, color=MUTE, bold=True)
        y += 0.22
        text(s, M, Inches(y), Inches(LW), Inches(ha), q["answer"], size=size)
        y += ha + 0.05
        if fu:
            text(s, M, Inches(y), Inches(LW), Inches(0.22), "FOLLOW-UPS", size=9, color=MUTE, bold=True)
            y += 0.24
            paras = []
            for f in fu:
                paras.append([("› " + f["q"] + "  ", {"bold": True}), (f["a"], {})])
            text(s, M + Inches(0.1), Inches(y), Inches(LW - 0.1), Inches(hf), paras, size=size - 1, spacing=1.08)

        # right column: shell + sources
        y = 2.05
        rs = 11
        if q.get("ai_answer"):
            for rs in (12, 11, 10, 9):
                h1 = est(q["ai_answer"], RW - 0.25, rs)
                h2 = est(q["blind_spot"], RW - 0.25, rs)
                if h1 + h2 + 0.9 < 3.6:
                    break
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(0.22), "WHAT THE AI TOLD THEM", size=9, color=MUTE, bold=True)
            y += 0.24
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(h1 + 0.1), q["ai_answer"], size=rs,
                 fill=RGBColor(0xF2, 0xF2, 0xF2))
            y += h1 + 0.22
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(0.22), "BLIND SPOT", size=9, color=MUTE, bold=True)
            y += 0.24
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(h2 + 0.1), q["blind_spot"], size=rs, bold=True,
                 fill=RGBColor(0xF2, 0xF2, 0xF2))
            y += h2 + 0.25
        if q.get("sources"):
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(0.22), "SOURCES", size=9, color=MUTE, bold=True)
            y += 0.24
            src = ctx["src"]
            lines = [[(f"[{k}] ", {"bold": True}), (src[k]["cite"], {})] for k in q["sources"]]
            ss = 9 if len(q["sources"]) <= 4 else 8
            hs = sum(est(f"[{k}] " + src[k]["cite"], RW, ss, 1.05) for k in q["sources"])
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(hs), lines, size=ss, color=MUTE, spacing=1.05)
            y += hs + 0.1
        if q.get("verify"):
            hv = est("⚠ " + q["verify"], RW, 10)
            text(s, Inches(RX), Inches(y), Inches(RW), Inches(hv), "⚠ UNVERIFIED — " + q["verify"], size=10, color=WARN, bold=True)

        np = [f"[{q['id']}] {q['q']}", "PRINCIPLE: " + q["principle"], "SAY: " + q["answer"]]
        np += [f"IF ASKED: {f['q']} — {f['a']}" for f in fu]
        if q.get("verify"):
            np.append("TO CONFIRM BEFORE PRESENTING: " + q["verify"])
        notes(s, np)

    # 1. cover
    s = prs.slides.add_slide(blank)
    box(s, 0, 0, W, H, fill=INK)
    text(s, M, Inches(0.9), W - 2 * M, Inches(0.4), (meta.get("subtitle") or "Q&A Defense Kit").upper(), size=14,
         color=WHITE, bold=True)
    text(s, M, Inches(1.4), W - 2 * M, Inches(1.6), meta["title"], size=36, color=WHITE, bold=True)
    claims = meta.get("core_claims") or []
    if claims:
        text(s, M, Inches(3.3), W - 2 * M, Inches(2.8),
             [[(f"{i + 1}.  {c}", {"space_after": 6})] for i, c in enumerate(claims)], size=15, color=WHITE)
    sub = " · ".join(x for x in [meta.get("speaker"), f"Talk {meta['talk_date']}" if meta.get("talk_date") else None,
                                 f"Sources checked {meta.get('checked')}", f"{ctx['nq']} questions"] if x)
    text(s, M, H - Inches(0.9), W - 2 * M, Inches(0.4), sub, size=11, color=WHITE)

    # 2. contents (filled at the end)
    toc = prs.slides.add_slide(blank)
    title(toc, "Contents", "Q&A defense kit")

    # 3. top 10
    s = new("Top 10 risks")
    title(s, "Top 10 questions to have cold", "Highest risk = most likely × most damaging")
    toc_targets.append(("Top 10 risks", s))
    rows = [["ID", "Question", "Core answer", "Risk"]]
    for q in ctx["top10"]:
        rows.append([[(q["id"], {"bold": True})], q["q"], q["_one"], "●" * int(q["risk"])])
    table(s, M, Inches(1.6), W - 2 * M, rows, [0.06, 0.38, 0.49, 0.07], size=10, rowh=0.48)

    # 4. argument maps, one per core claim
    for i, mp in enumerate(maps):
        s = new("Argument map")
        title(s, mp.get("claim") or mp["title"], f"Argument map {i + 1}/{len(maps)} — green supports, red attacks")
        if i == 0:
            toc_targets.append(("Argument maps", s))
        if mp.get("png"):
            from PIL import Image
            iw, ih = Image.open(mp["png"]).size
            maxw, maxh = W - 2 * M, H - Inches(2.3)
            scale = min(maxw / iw, maxh / ih)
            pw, ph = int(iw * scale), int(ih * scale)
            s.shapes.add_picture(str(mp["png"]), int((W - pw) / 2), Inches(1.6), pw, ph)
        else:
            text(s, M, Inches(1.6), W - 2 * M, H - Inches(2.3), mp.get("text", ""), size=12)

    # 5. coverage
    s = new("MECE coverage")
    title(s, f"{ctx['nq']} questions across five branches and five questioners", "MECE coverage")
    toc_targets.append(("MECE coverage", s))
    rows = [["Branch · root question"] + [p["label"] for p in ctx["personas"]] + ["Total"]]
    for b in ctx["branches"]:
        rows.append([[(b["label"], {"bold": True}), (f"  {b['root']}", {"color": MUTE})]] +
                    [str(ctx["grid"][b["id"]][p["id"]] or "·") for p in ctx["personas"]] + [[(str(b["n"]), {"bold": True})]])
    rows.append([[("Total", {"bold": True})]] + [[(str(p["n"]), {"bold": True})] for p in ctx["personas"]] +
                [[(str(ctx["nq"]), {"bold": True})]])
    table(s, M, Inches(1.7), W - 2 * M, rows, [0.34] + [0.11] * 5 + [0.11], size=13, rowh=0.55)

    # 6. cynefin
    s = new("Cynefin triage")
    title(s, "The domain decides the opener, never the honesty", "Cynefin triage")
    toc_targets.append(("Cynefin triage", s))
    rows = [["Domain", "Opener", "n", "Questions"]]
    for c in ctx["cynefin"]:
        rows.append([[(c["label"], {"bold": True})], f"“{c['opener']}”", str(len(c["ids"])), ", ".join(c["ids"])])
    table(s, M, Inches(1.7), W - 2 * M, rows, [0.13, 0.37, 0.05, 0.45], size=12, rowh=0.75)

    # 7. branches
    for b in ctx["branches"]:
        s = new(b["label"])
        box(s, 0, 0, W, H - Inches(0.5), fill=INK)
        text(s, M, Inches(1.2), W - 2 * M, Inches(0.4), f"BRANCH {BRANCH_IDS.index(b['id']) + 1} OF 5", size=12,
             color=WHITE, bold=True)
        text(s, M, Inches(1.7), W - 2 * M, Inches(1.0), b["label"], size=44, color=WHITE, bold=True)
        text(s, M, Inches(2.75), W - 2 * M, Inches(0.6), b["root"], size=22, color=WHITE)
        lst = [[(f"{q['id']}  ", {"bold": True}), (q["q"][:95] + ("…" if len(q["q"]) > 95 else ""), {})] for q in b["questions"]]
        half = (len(lst) + 1) // 2
        sz = 11 if len(lst) <= 14 else 9.5
        text(s, M, Inches(3.7), (W - 2 * M) / 2 - Inches(0.2), Inches(3.2), lst[:half], size=sz, color=WHITE)
        text(s, M + (W - 2 * M) / 2, Inches(3.7), (W - 2 * M) / 2, Inches(3.2), lst[half:], size=sz, color=WHITE)
        toc_targets.append((f"{b['label']} — {b['root']} ({b['n']})", s))
        for q in b["questions"]:
            question_slide(q)

    # dose
    s = new("Dose quick reference")
    title(s, "Dose quick reference — every number from the label", "Practice")
    toc_targets.append(("Dose quick reference", s))
    rows = [["Item", "Value", "Source"]]
    for r in ctx["dose_table"]:
        v = [(r["value"], {})] + ([(f"  ⚠ {r['verify']}", {"color": WARN, "bold": True})] if r.get("verify") else [])
        rows.append([[(r["item"], {"bold": True})], v, r.get("source", "")])
    rh = min(0.34, 5.0 / max(1, len(rows)))
    table(s, M, Inches(1.6), W - 2 * M, rows, [0.27, 0.65, 0.08], size=10.5 if len(rows) < 16 else 9, rowh=rh)

    # unverified
    s = new("Unverified")
    title(s, f"Check before the talk — {len(ctx['unverified'])} unverified items", "⚠ Unverified")
    toc_targets.append(("⚠ Unverified items", s))
    rows = [["Item", "What to check"]] + [[[(k, {"bold": True})], v] for k, v in ctx["unverified"]]
    per = 16
    for i in range(0, len(rows) - 1, per):
        if i:
            s = new("Unverified (cont.)")
            title(s, "Check before the talk (cont.)", "⚠ Unverified")
        table(s, M, Inches(1.6), W - 2 * M, [rows[0]] + rows[1 + i:1 + i + per], [0.22, 0.78], size=10, rowh=0.32)

    # references
    srcs = ctx["sources"]
    per = 12
    for i in range(0, len(srcs), per):
        s = new("References")
        title(s, "References" + (" (cont.)" if i else ""), "Sources")
        if not i:
            toc_targets.append(("References", s))
        rows = [["ID", "Citation", "Read"]] + [[[(x["id"], {"bold": True})], x["cite"], x.get("read", "")] for x in srcs[i:i + per]]
        table(s, M, Inches(1.6), W - 2 * M, rows, [0.06, 0.72, 0.22], size=10, rowh=0.4)

    # fill contents
    from pptx.action import ActionSetting  # noqa: F401
    y = Inches(1.7)
    step = min(Inches(0.42), int((H - Inches(2.4)) / max(1, len(toc_targets))))
    for label, target in toc_targets:
        num = prs.slides.index(target) + 1
        t = text(toc, M, y, W - 2 * M - Inches(1.2), step, label, size=15)
        t.click_action.target_slide = target
        n = text(toc, W - M - Inches(1.2), y, Inches(1.2), step, str(num), size=15, align=PP_ALIGN.RIGHT)
        n.click_action.target_slide = target
        y += step
    for b in back_links:
        b.click_action.target_slide = toc

    path = out / "kit.pptx"
    prs.save(path)
    return path



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml")
    ap.add_argument("--out", default="out")
    ap.add_argument("--only", default="html,pptx,pdf")
    a = ap.parse_args()
    d = load(a.yaml)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ctx = context(d)
    only = set(a.only.split(","))
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        maps, _ = render_map(d, work)
        for i, mp in enumerate(maps):
            if mp.get("png"):
                shutil.copy(mp["png"], out / f"map{i + 1}.png")
        made = []
        if "html" in only:
            made.append(build_html(ctx, out, maps))
        if "pptx" in only:
            made.append(build_pptx(ctx, out, maps))
        if "pdf" in only:
            made.append(build_pdf(ctx, out, work))
    for m in made:
        print("wrote", m)


if __name__ == "__main__":
    main()
