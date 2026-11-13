#!/usr/bin/env python3
"""Generate the Aegis logo (original design in the manner of an Attic red-figure cup tondo).

Writes logo.svg, logo-512.png, favicon-64.png, social-preview.svg/.png (1280x640) next to this file.
Requires rsvg-convert for PNGs. Fonts for the social preview: Noto Serif CJK TC.
"""
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
INK = "#16100c"      # black gloss
CLAY = "#d0783c"     # terracotta
CLAY_D = "#a65424"   # dilute glaze line
CX = CY = 256


def polar(r, a):
    return CX + r * math.cos(a), CY + r * math.sin(a)


def meander(r0, r1, n=26, w=5.5):
    """Running Greek key between radii r0 (inner) and r1 (outer)."""
    parts = []
    span = 2 * math.pi / n
    hook = [(0.12, 0.0), (0.12, 0.82), (0.86, 0.82), (0.86, 0.22), (0.44, 0.22), (0.44, 0.56)]
    for i in range(n):
        a0 = -math.pi / 2 + i * span
        pts = [polar(r0 + v * (r1 - r0), a0 + u * span) for u, v in hook]
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        parts.append(d)
    body = "".join(f'<path d="{d}"/>' for d in parts)
    return (f'<g fill="none" stroke="{CLAY}" stroke-width="{w}" stroke-linecap="square" stroke-linejoin="miter">{body}</g>'
            f'<circle cx="{CX}" cy="{CY}" r="{r0}" fill="none" stroke="{CLAY}" stroke-width="{w}"/>'
            f'<circle cx="{CX}" cy="{CY}" r="{r1 + 6}" fill="none" stroke="{CLAY}" stroke-width="3"/>')


def ring(r, w=2, color=None):
    return f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{color or CLAY}" stroke-width="{w}"/>'


def beads(r, n, size):
    out = []
    for i in range(n):
        x, y = polar(r, -math.pi / 2 + 2 * math.pi * i / n)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{size}" fill="{CLAY}"/>')
    return "".join(out)


def wolf_teeth(r0, r1, n):
    """Alternating outward/inward triangles (black-figure 'wolf tooth' band)."""
    out = []
    span = 2 * math.pi / n
    for i in range(n):
        a = -math.pi / 2 + i * span
        p = [polar(r0, a), polar(r1, a + span / 2), polar(r0, a + span)]
        q = [polar(r1, a + span / 2), polar(r0, a + span), polar(r1, a + 1.5 * span)]
        out.append('<path d="M' + " L".join(f"{x:.2f},{y:.2f}" for x, y in p) + f'Z" fill="{CLAY}"/>')
        out.append('<path d="M' + " L".join(f"{x:.2f},{y:.2f}" for x, y in q) + f'Z" fill="none" stroke="{CLAY}" stroke-width="1.4"/>')
    return "".join(out)


def deflections(r_shield, r_out, n=12):
    """A ring of questions striking the shield and glancing off: each is a V whose apex touches the rim."""
    out = []
    span = 2 * math.pi / n
    for i in range(n):
        a = -math.pi / 2 + i * span
        apex = polar(r_shield + 4, a)
        inn = polar(r_out, a - span * 0.42)
        outp = polar(r_out, a + span * 0.42)
        out.append(f'<path d="M{inn[0]:.2f},{inn[1]:.2f} L{apex[0]:.2f},{apex[1]:.2f}" stroke="{CLAY}" stroke-width="3" '
                   f'stroke-dasharray="5 4" fill="none"/>')
        out.append(f'<path d="M{apex[0]:.2f},{apex[1]:.2f} L{outp[0]:.2f},{outp[1]:.2f}" stroke="{CLAY}" stroke-width="3.2" '
                   f'stroke-linecap="round" fill="none"/>')
        # arrowhead at the outgoing end
        ang = math.atan2(outp[1] - apex[1], outp[0] - apex[0])
        h1 = (outp[0] - 9 * math.cos(ang - 0.45), outp[1] - 9 * math.sin(ang - 0.45))
        h2 = (outp[0] - 9 * math.cos(ang + 0.45), outp[1] - 9 * math.sin(ang + 0.45))
        out.append(f'<path d="M{h1[0]:.2f},{h1[1]:.2f} L{outp[0]:.2f},{outp[1]:.2f} L{h2[0]:.2f},{h2[1]:.2f}" '
                   f'stroke="{CLAY}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
        out.append(f'<circle cx="{apex[0]:.2f}" cy="{apex[1]:.2f}" r="3.4" fill="{CLAY}"/>')
        if i % 2 == 0:  # a small '?' at the tail of every other strike
            qx, qy = polar(r_out + 2, a - span * 0.42)
            out.append(f'<text x="{qx:.1f}" y="{qy + 6:.1f}" font-family="DejaVu Serif, Georgia, serif" font-weight="700" '
                       f'font-size="17" fill="{CLAY}" text-anchor="middle">?</text>')
    return "".join(out)


def star(r_out, r_in, n, color, w=1.6, fill="none"):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        pts.append(polar(r, -math.pi / 2 + math.pi * i / n))
    return ('<path d="M' + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) +
            f'Z" fill="{fill}" stroke="{color}" stroke-width="{w}" stroke-linejoin="miter"/>')


def emblem():
    """Hoplite shield (aspis) with a geometric rosette; the blazon is an answered question."""
    R = 98
    g = [ring(184, 2.2), wolf_teeth(166, 184, 36), ring(166, 2.2), beads(158, 60, 1.9),
         deflections(R + 6, 150, 12)]
    g.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{CLAY}"/>')
    g.append(ring(R - 7, 3, INK))
    # rosette: two interlaced 12-point stars, a 24-ray burst, then the black boss
    for k in range(24):
        a = -math.pi / 2 + k * math.pi / 12
        x0, y0 = polar(54, a)
        x1, y1 = polar(R - 12, a)
        g.append(f'<path d="M{x0:.2f},{y0:.2f} L{x1:.2f},{y1:.2f}" stroke="{CLAY_D}" stroke-width="1.2"/>')
    g.append(star(R - 12, 62, 12, INK, 2.2))
    g.append(star(R - 24, 58, 12, INK, 1.2))
    g.append(ring(62, 2, INK))
    g.append(f'<circle cx="{CX}" cy="{CY}" r="54" fill="{INK}"/>')
    g.append(ring(48, 1.4, CLAY))
    g.append(beads(42, 24, 1.3))
    # blazon on the boss: question mark whose dot is a check
    sx, sy = CX, CY - 2
    q = (f'M{sx - 14},{sy - 14} C{sx - 14},{sy - 30} {sx + 16},{sy - 32} {sx + 16},{sy - 14} '
         f'C{sx + 16},{sy - 3} {sx},{sy - 1} {sx},{sy + 10}')
    g.append(f'<path d="{q}" fill="none" stroke="{CLAY}" stroke-width="8" stroke-linecap="round"/>')
    g.append(f'<path d="M{sx - 9},{sy + 22} L{sx - 1},{sy + 30} L{sx + 13},{sy + 16}" fill="none" stroke="{CLAY}" '
             f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(g)


def logo_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<title>Aegis — Q&amp;A Defense Kit</title>
<circle cx="{CX}" cy="{CY}" r="252" fill="{INK}"/>
<circle cx="{CX}" cy="{CY}" r="246" fill="none" stroke="{CLAY}" stroke-width="2"/>
{meander(212, 236)}
{ring(204, 1.6)}{beads(198, 72, 2.1)}{ring(192, 1.6)}
{emblem()}
</svg>
'''


def social_svg(logo_inner):
    inner = logo_inner.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640">
<rect width="1280" height="640" fill="{INK}"/>
<g transform="translate(70,84) scale(0.92)">{inner}</g>
<g font-family="Noto Serif CJK TC, DejaVu Serif, serif" fill="{CLAY}">
  <text x="620" y="232" font-size="104" font-weight="700" letter-spacing="14">AEGIS</text>
  <text x="624" y="300" font-size="40" font-weight="700">QA 防禦術 · Q&amp;A Defense Kit</text>
  <text x="624" y="372" font-size="27" fill="#e9c9a8">Out-answer the AI-armed questioner (考考男)</text>
  <text x="624" y="414" font-size="27" fill="#e9c9a8">before you step on stage.</text>
  <text x="624" y="500" font-size="20" fill="{CLAY}" letter-spacing="1">MECE · CYNEFIN · ARGDOWN · FIRST PRINCIPLES</text>
  <text x="624" y="536" font-size="20" fill="{CLAY}" letter-spacing="1">→ HTML · PPTX · PDF</text>
</g>
<rect x="620" y="448" width="560" height="3" fill="{CLAY}"/>
</svg>
'''


def main():
    svg = logo_svg()
    (HERE / "logo.svg").write_text(svg, encoding="utf-8")
    soc = social_svg(svg)
    (HERE / "social-preview.svg").write_text(soc, encoding="utf-8")
    for src, dst, w in [("logo.svg", "logo-512.png", 512), ("logo.svg", "favicon-64.png", 64),
                        ("social-preview.svg", "social-preview.png", 1280)]:
        subprocess.run(["rsvg-convert", "-w", str(w), str(HERE / src), "-o", str(HERE / dst)], check=True)
    print("wrote logo.svg, logo-512.png, favicon-64.png, social-preview.svg, social-preview.png")


if __name__ == "__main__":
    main()
