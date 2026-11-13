# Argdown claims map

The map holds the talk's 3–5 core claims and every attack on them. It is the seed of the question bank: each attack becomes at least one question.

## Syntax used here

```argdown
[MAIA-OS]: D-Rd prolongs overall survival vs Rd in transplant-ineligible NDMM.
  + <Final OS>: Median OS 90.3 vs 64.1 mo; HR 0.67 (Leukemia 2026).
  - <Old control>: Rd is no longer the standard comparator; VRd and quadruplets are. #undermine
    - <Indirect data>: Rd-anchored ITC vs S0777 favours D-Rd (HR 0.59), with ITC caveats. #reply
  - <Post-progression access>: Rd patients' access to anti-CD38 at relapse shapes OS. #undercut
    + <Conceded>: OS reflects timing of anti-CD38 under trial-era access, not universally. #concede
```

- `[Statement]` = a claim. `<Argument>` = a reason for or against.
- `+` supports the parent; `-` attacks it.
- Tag every attack with its type and every child of an attack with `#reply` or `#concede`.

## Three ways to attack a claim

| Type | Hits | Example question it generates |
|---|---|---|
| `#rebut` | The conclusion itself | "Isn't the OS benefit just from more deaths in the control arm early on?" |
| `#undercut` | The step from evidence to conclusion | "PFS improved — but why should that mean my patient lives longer?" |
| `#undermine` | A premise | "Rd was never the right comparator, was it?" |

Undermining attacks are the most common and the most dangerous in oncology Q&A, because they usually target the control arm or the population.

## Rules

- At most ~25 lines; the map is a map, not a manuscript.
- A `#concede` node narrows the claim — and the slide wording must narrow with it.
- Never write a reply you cannot source. A missing reply is a `#concede`.
- `build.py` renders the map with `argdown map` (SVG → PNG). Keep labels short so the graph stays legible.
