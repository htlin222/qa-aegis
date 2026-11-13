# YAML schema (`qa.yaml`)

```yaml
meta:
  title: "MAIA: D-Rd in transplant-ineligible NDMM"   # talk title
  subtitle: "Q&A Defense Kit"
  speaker: "Name, Institution"
  talk_date: 2026-11-20
  checked: 2026-11-13            # date sources were verified
  argdown: claims.argdown        # path relative to qa.yaml
  core_claims:                   # 3–5 sentences, shown on the cover
    - "…"

sources:
  - id: S1
    cite: "Facon T, et al. N Engl J Med 2019;380:2104-2115"
    url: "https://pubmed.ncbi.nlm.nih.gov/31141632/"
    read: "abstract"             # abstract | full text | label §x | rule text

dose_table:                      # practice quick reference (pocket card + appendix)
  - item: "Daratumumab IV"
    value: "16 mg/kg …"
    source: L1
    verify: ""                   # optional

questions:
  - id: C01                      # unique; prefix by branch letter is conventional
    branch: credible             # credible | applicable | worth | position | practice
    persona: ai_senior           # ai_senior | statistician | community | pharmacist | payer
    cynefin: complicated         # clear | complicated | complex | chaotic | confused
    risk: 5                      # 1–5, likelihood × damage
    attack: undermine            # optional: rebut | undercut | undermine (from the Argdown map)
    q: "…"                       # the question as it would be asked
    oneliner: "…"                # optional: dense answer for Top 10 / pocket card (else derived from answer)
    ai_answer: "…"               # optional (required for ai_senior): what an AI tool would say
    blind_spot: "…"              # optional (required with ai_answer): what that answer misses
    principle: "…"               # required: first-principles sentence
    answer: "…"                  # required: 30-second spoken answer, Cynefin opener first
    followups:                   # required when risk ≥ 4
      - q: "…"
        a: "…"
    sources: [S1, L1]            # required unless cynefin is complex/confused
    verify: ""                   # optional: what is still unchecked → ⚠ UNVERIFIED
```

Field order in the outputs: question → principle → answer → follow-ups → AI answer / blind spot → sources.
