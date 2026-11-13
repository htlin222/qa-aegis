# Source policy

The kit is only as strong as its weakest number. One wrong dose in front of a pharmacist costs more credibility than ten unanswered questions.

## Hierarchy

| Fact type | Acceptable source | Not acceptable |
|---|---|---|
| Efficacy and safety numbers | Primary publication (abstract or full text read this session), regulatory label section 14, congress abstract (marked as such) | Memory, review articles quoting the trial, AI summaries |
| Doses, schedules, premedication, renal/hepatic adjustment | Current regulatory label (FDA USPI via DailyMed; TFDA 仿單 when the talk is about local use), trial protocol/supplement, guideline order templates | Memory, institutional habit (label it as such if used) |
| Reimbursement (Taiwan NHI 健保) | 藥品給付規定 text with 條號 and effective date (健保署 修訂對照表) | News articles, company slides |
| Guideline position | The guideline document and version date | Secondary summaries |

## How to record it

- `sources:` in the YAML holds an id, a full citation, and a URL or PMID.
- Each question lists the source ids it relies on.
- `read:` on a source records how it was checked: `abstract`, `full text`, `label §2.6`, `rule text`.
- `verify:` on a question names what is still unchecked. It renders as **⚠ UNVERIFIED** and lands on the pocket card.
- Speaker-derived numbers (absolute differences, NNT) say `speaker's arithmetic` in the answer.

## Fetching

- PubMed: E-utilities (`esearch`, `efetch rettype=abstract`) or the PubMed connector.
- FDA labels: `https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=…` → setid → `…/spls/{setid}.xml`.
- NCCN: only through the user's licensed access; never copy guideline text into a public repository.
- NHI: search 健保署 「藥品給付規定」修訂對照表 for the drug's 條號; quote the effective date.

## Currency

Facts are checked as of the talk date. Labels, guidelines and NHI rules change several times a year; record the date checked in `meta.checked`.
