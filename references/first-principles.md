# First-principles answering

Every answer starts from a `principle`: one sentence that would be true even if this trial had never been run. It is the reason the number means what it means. A questioner holding an AI summary has the number; the principle is what they usually lack, and it is what makes the room trust the rest of the answer.

**Test for a good principle:** could you use it to predict the answer to a *different* trial's version of the same question? If yes, it is a principle. If it only restates this trial's result, it is not.

## Answer shape (P → E → A)

1. **Principle** — the mechanism, statistical fact, or constraint.
2. **Evidence** — the one number from this trial (with source) that the principle makes interpretable.
3. **Application** — what you do for the patient in front of you.

> *Q: "The HR for OS is 0.67 — so a third fewer deaths?"*
> **P:** A hazard ratio compares instantaneous risk over the whole curve; it is not a proportion of patients.
> **E:** At 7 years, 53% vs 39% alive — a 14-point absolute difference.
> **A:** For my patient I quote the 7-year difference, not the HR.

## Principle library (oncology / hematology)

### Statistics and trial design
- **Relative vs absolute.** HR and RR are relative; patients live on absolute differences at a time point. The same HR means a small absolute gain at low baseline risk.
- **HR is an average over time.** Non-proportional hazards (crossing or late-separating curves) make a single HR misleading; look at landmarks.
- **Medians are one point on the curve.** "Not reached" is not "infinite"; it means fewer than half have had the event.
- **Surrogates must be validated per setting.** PFS or MRD predicts OS only where it has been shown to, and only for that drug class and line.
- **OS is confounded by what happens after progression.** If the control arm cannot get the experimental class at relapse, OS overstates the value of *timing*; if it can, OS understates it.
- **Control arm defines the question.** A trial answers "better than *this* comparator", never "better than everything".
- **Open-label + investigator-assessed endpoints** invite bias; central review and objective endpoints reduce it.
- **Subgroups test interaction, not efficacy.** A non-significant subgroup is not evidence of no effect; a significant one is often chance. Consistent direction is what to look for.
- **Indirect comparisons inherit every difference between trials** not captured by the adjustment (era, subsequent therapy, assessment schedule).
- **Interim analyses spend alpha.** An early "significant" OS crossed a stricter boundary; a later update is descriptive.
- **Absence of evidence ≠ evidence of absence**, especially in small strata (frail, Asian, very elderly).

### Pharmacology
- **Exposure = dose ÷ clearance.** Any dose adjustment follows from which organ clears the drug.
- **Monoclonal antibodies are cleared by target binding and catabolism, not kidneys**; renal failure rarely changes their dose.
- **Target expressed on normal cells → on-target toxicity and lab artefacts** (e.g. CD38 on red cells → panreactive indirect antiglobulin test; CD38 on NK cells → NK depletion).
- **A therapeutic IgG is itself a monoclonal protein**; it can appear on SPEP/IFE and mimic residual disease.
- **First-dose reactions from cytokine release fall with antigen burden**; premedication and slower first infusion, or SC route, reduce them.
- **Immunomodulatory drugs (IMiDs) are thrombogenic**, and risk rises with dexamethasone and EPO; thromboprophylaxis is matched to risk.
- **Teratogenicity class effect** of thalidomide analogues drives pregnancy-prevention programs.

### Infection and immunity
- **Myeloma is itself immunodeficiency** (hypogammaglobulinemia); anti-CD38 deepens it. Infection risk is highest early.
- **Latent viruses reactivate when cellular immunity falls** (VZV, HBV): prophylaxis or monitoring precedes therapy.

### Health economics and policy
- **Continuous therapy cost scales with how well it works**: the better the PFS, the longer the drug is paid for.
- **Payers cap duration or require re-authorization** to bound budget impact; caps are a policy choice, not evidence of when to stop.
- **Reimbursement follows local evidence review and budget**, not FDA approval; always quote the rule's effective date.

### Clinical reasoning
- **Fitness, not age, predicts tolerance**; frailty scores (age + comorbidity + PS) outperform age alone.
- **The best first-line therapy is the one the patient can keep taking**; discontinuation erases benefit.
- **Using the best drug first vs saving it** is a bet on attrition: in older patients, many never reach second line.
