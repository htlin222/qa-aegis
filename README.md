# Aegis — Q&A Defense Kit

A Claude skill that prepares an oncology or hematology speaker for Q&A.

The new hazard in Q&A is the senior who asks an AI tool the same question during your talk and then checks you against it. Aegis anticipates that: for every question it records what the AI answer probably says, where it is thin, and how to answer from first principles with sourced numbers.

## What it does

| Step | Framework | Output |
|---|---|---|
| Map the talk's claims and how each can be attacked (rebut / undercut / undermine) | **Argdown** | Argument maps |
| Sweep questions across 5 branches × 5 questioner personas, ≥50 questions | **MECE** | Coverage grid, question bank |
| Triage each question by what kind of answer is honest | **Cynefin** | Opener per question |
| Answer: principle → evidence → application, with follow-ups | **First principles** | 30-second answers |
| Every number sourced; doses from the label; NHI rules with effective date; gaps flagged | Source policy | ⚠ UNVERIFIED list |

**Branches:** credible · applicable · worth · position · practice (dose, schedule, premedication, modifications, prophylaxis, lab interference).
**Personas:** AI-armed senior · statistician · community oncologist · clinical pharmacist · payer.

One YAML source builds three outputs:

- `kit.html` — self-contained, filterable, with a rehearsal mode that hides answers
- `kit.pptx` — cover · linked contents · Top 10 · argument maps · coverage · Cynefin · one slide per question (script in speaker notes) · dose reference · unverified · references
- `pocket.pdf` — one A4 page: Top 10 with principles, Cynefin openers, dose reference, unverified items

## Example

`examples/maia/` — MAIA (daratumumab-lenalidomide-dexamethasone, transplant-ineligible NDMM): 65 questions, 3 argument maps, sources checked 2026-11-13. Built outputs are in `examples/maia/out/`.

> The example is a demonstration of the method, not clinical guidance. Items marked ⚠ UNVERIFIED have not been checked; verify everything against current labels, guidelines and reimbursement rules before use.

## Use

```bash
pip install pyyaml jinja2 python-pptx playwright && playwright install chromium
npm i -g @argdown/cli           # argument maps (optional; falls back to text)
# rsvg-convert (librsvg) converts the maps to PNG for the PPTX

python3 scripts/validate.py examples/maia/qa.yaml
python3 scripts/build.py examples/maia/qa.yaml --out examples/maia/out
```

As a Claude skill, copy the folder into your skills directory; `SKILL.md` holds the workflow.

## Layout

```
SKILL.md                 workflow
references/              MECE branches, personas, Cynefin playbook, first-principles library,
                         Argdown guide, source policy, YAML schema
scripts/build.py         YAML → HTML / PPTX / PDF
scripts/validate.py      schema, coverage grid, unverified list
templates/               HTML and pocket-card templates
examples/maia/           worked example
```

No guideline text (e.g. NCCN) or company slides are included; sources are cited by reference only.

MIT License.
