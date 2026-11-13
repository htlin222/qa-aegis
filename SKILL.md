---
name: qa-aegis
description: Build a Q&A defense kit for an oncology or hematology talk — anticipate every audience question (MECE sweep across five branches and five questioner personas), predict the AI-generated answer a questioner may already hold, triage each question with Cynefin, map the talk's claims and their attack points in Argdown, and answer from first principles with sourced numbers and doses. Outputs one YAML source built into an HTML kit, a PPTX with table of contents, and a one-page PDF pocket card. Use when the user says Q&A 防禦, QA 防禦術, 被考倒, 台下會問什麼, 預測提問, anticipate questions, defend my talk, rehearse Q&A, or hands over a slideset or trial and asks what they will be asked.
---

# Aegis — Q&A Defense Kit

A speaker loses the room in Q&A for one of three reasons: a question nobody anticipated, a number they could not source, or an answer that was right but sounded like a recital. This skill removes the first two before the talk and fixes the third by making every answer start from the underlying logic.

There is a new kind of questioner: the senior who asked an AI the same question in the back row and is now checking the speaker against it. The AI answer is usually a guideline-level summary. It is weakest exactly where a speaker can be strongest — trial design detail, who was excluded, absolute numbers, local reimbursement, and what happened after the data cutoff. So for every question the kit records what that AI answer probably says and where it is thin.

Slides and the kit are in English. Talk with the user in Traditional Chinese.

## Inputs to settle first

Ask in one round, only what the material does not already answer:

1. **Source.** Slideset, paper(s), or a topic only. For a slideset, read every slide first.
2. **The talk's 3–5 core claims.** If the user has none written, draft them from the source and confirm.
3. **Audience and venue.** Department, regional meeting, sponsored talk. A sponsored venue shifts which questions are dangerous (off-label, comparator fairness).
4. **Date of the talk.** Reimbursement and labels change; facts are checked as of that date.

## Workflow

### 1. Claims → Argdown map

Write `claims.argdown`: each core claim, its supporting evidence (`+`), and every way it can be attacked (`-`). Classify each attack by what it hits — read `references/argdown-guide.md`:

- **rebut** — attacks the conclusion directly ("OS benefit is not real")
- **undercut** — attacks the inference ("PFS gain does not imply OS gain here")
- **undermine** — attacks a premise ("the control arm is not today's standard")

Under each attack write a reply, or a `Conceded` node that narrows the claim. Never invent a rebuttal. Every attack becomes at least one question in step 2.

### 2. MECE sweep — five branches × five personas

Generate the question bank. Read `references/mece-branches.md` and `references/personas.md`.

| Branch | Root question |
|---|---|
| `credible` | Is the result true? (internal validity) |
| `applicable` | Does it apply to my patient? (external validity) |
| `worth` | Is it worth it? (absolute benefit vs harm, cost) |
| `position` | Where does it sit? (comparators, sequencing, what replaces it) |
| `practice` | How do I actually give it? (dose, schedule, premedication, modifications, monitoring, interactions, toxicity management) |

Personas: `ai_senior` (the AI-armed senior), `statistician`, `community` (community oncologist), `pharmacist`, `payer`.

Targets for the carpet sweep: **≥50 questions; every branch ≥8; every persona ≥6; `practice` ≥12.** Run `scripts/validate.py` to check coverage; it prints the empty cells of the branch × persona grid. Fill the gaps it reports rather than adding more of what is already dense.

Exhaustive does not mean padded. Two questions with the same answer are one question.

### 3. Shell simulation — what the AI already told them

For each `ai_senior` question, and any other where it helps, write `ai_answer`: the 1–2 sentence answer a general AI tool would give (guideline-level, relative effects, no local context). Then `blind_spot`: the specific thing that answer gets wrong or leaves out. Generate the AI answer yourself from general knowledge; do not need OpenEvidence. The blind spot must be checkable against a source.

### 4. Cynefin triage — choose the answer strategy

Classify every question. Read `references/cynefin-playbook.md` for the full openers.

| Domain | The question is… | Opener |
|---|---|---|
| `clear` | answerable with one number or rule | "The data are clear: …" |
| `complicated` | answerable, but depends on a variable | "It depends on X — here's how I decide…" |
| `complex` | not answered by any data yet | "We don't have data for that. My reasoning is…, and the trial that would answer it is…" |
| `chaotic` | an ambush, multi-part, or hostile | "Let me take the part I can answer with data first…" |
| `confused` | unclear what is being asked | "If I understand correctly, you're asking…" |

The domain decides the opener; it never decides honesty. A `complex` question gets "we don't know", not a confident guess.

### 5. Answer from first principles

Every answer has three parts, in this order. Read `references/first-principles.md`.

1. **`principle`** — the underlying logic, in one sentence that would still be true if the trial had never been run: the mechanism, the statistical fact, or the economic constraint. ("A hazard ratio is relative; the patient lives on the absolute difference.")
2. **`answer`** — the 30-second spoken answer: Cynefin opener, then the evidence with its number, then what it means for the patient in front of you.
3. **`followups`** — the next 1–2 questions the same person asks, each with a short answer. Required for every question with risk ≥4.

Prefer an answer that teaches the room how to reason over one that only states a result. That is what defeats the shell: the AI can recite the number; it rarely explains why the number means what it means.

### 6. Sources — the hard rule

Read `references/source-policy.md`. In short:

- Every number traces to a source in `sources:` that was read in this session (abstract, label, guideline page, regulation). Record which.
- **Doses come only from a label, a trial protocol, or a guideline order template.** Never from memory. Cite section numbers.
- **Taiwan NHI (健保) rules** come from the current 藥品給付規定 text, with the effective date (e.g. 115/4/1). Summarize in English on the slide; put the 條號 in the source.
- Anything not verified gets `verify: "what to check"`. It renders as **⚠ UNVERIFIED** on every output and is listed on the pocket card. Never fill a gap with a plausible number.
- Your own arithmetic (absolute differences, NNT) is labelled `speaker's arithmetic`.

### 7. Risk score and Top 10

`risk` 1–5 = likelihood the question is asked × damage if fumbled. 5 means "asked at most talks, and a wrong answer ends your credibility" (typically dosing errors and the comparator question). The build ranks the Top 10 automatically by risk, then by branch order.

### 8. Build

```bash
python3 scripts/validate.py qa.yaml          # coverage grid, missing fields, unverified list
python3 scripts/build.py qa.yaml --out out/  # → kit.html, kit.pptx, pocket.pdf
```

`build.py` renders `claims.argdown` with the Argdown CLI (`npm i -g @argdown/cli`) to SVG for the HTML and PNG for the PPTX. Without the CLI it falls back to an indented text map. PDF uses Playwright Chromium (`pip install playwright && playwright install chromium`).

Outputs:

- **kit.html** — one self-contained file; filter by branch, persona, Cynefin domain and risk; search; every card expands to principle, answer, follow-ups, AI answer and blind spot, sources.
- **kit.pptx** — cover · contents (linked) · Top 10 · argument map · MECE coverage grid · Cynefin matrix · a divider per branch · one slide per question · dose quick reference · references. The answer script is also in the speaker notes. Monochrome, Arial.
- **pocket.pdf** — one A4 page: the Top 10 with one-line answers, the dose quick reference, and every ⚠ UNVERIFIED item.

### 9. Check before handing over

Open the HTML, render the PPTX (`soffice --headless --convert-to pdf`) and look at the contents slide, a dense question slide and the dose table. Re-check every dose and every NHI statement against its source one last time. Then tell the user, in a few lines: question count by branch, the Top 3 risks, what is still unverified, and anything the source material contradicted in the user's claims.

## Data schema

See `references/schema.md` and the worked example in `examples/maia/`. Minimum per question:

```yaml
- id: P03
  branch: practice
  persona: pharmacist
  cynefin: clear
  risk: 5
  q: "CrCl is 35. What lenalidomide dose?"
  principle: "Lenalidomide is ~80% renally cleared unchanged, so exposure rises as CrCl falls."
  answer: "The label is clear: CrCl 30–60, 10 mg daily…"
  sources: [L3]
```

## Bundled files

| File | Use |
|---|---|
| `scripts/build.py` | YAML → kit.html, kit.pptx, pocket.pdf |
| `scripts/validate.py` | Coverage grid, schema check, unverified list |
| `templates/kit.html.j2`, `templates/pocket.html.j2` | HTML and pocket-card templates |
| `references/mece-branches.md` | What each branch covers; a question bank skeleton |
| `references/personas.md` | The five questioners and what each one probes |
| `references/cynefin-playbook.md` | Domain tests and spoken openers |
| `references/first-principles.md` | Principle library for oncology/hematology answers |
| `references/argdown-guide.md` | Claims map syntax and the three attack types |
| `references/source-policy.md` | Source hierarchy for numbers, doses, NHI |
| `references/schema.md` | Full YAML schema |
| `examples/maia/` | Worked example: MAIA (D-Rd, transplant-ineligible NDMM) |
