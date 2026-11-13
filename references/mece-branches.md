# The five MECE branches

The branches follow the order in which a clinician decides: is it true → is it my patient → is it worth it → what else could I do → how do I give it. A question belongs to the branch whose root question it ultimately tests. If it tests two, put it where a wrong answer would hurt most and note the other in `tags`.

## 1. `credible` — Is the result true?

- Design: randomization, open-label vs blinded, who assessed the endpoint (central vs investigator)
- Control arm: was it the standard *at enrollment*; is it the standard *now*
- Endpoint: primary endpoint choice, surrogate validity (PFS, MRD → OS), hierarchical testing, alpha spending at interim
- Maturity: events, median follow-up, censoring pattern, tail of the curve
- Post-progression therapy: crossover, access to the experimental drug class at relapse (confounds OS both ways)
- Multiplicity: subgroups, exploratory endpoints presented as findings
- Assay artefacts: anything that changes how response or progression is measured (e.g. a therapeutic antibody seen on SPEP/IFE)
- Sponsor role, early stopping, protocol amendments

## 2. `applicable` — Does it apply to my patient?

- Eligibility and the excluded: age, PS, organ function (renal, hepatic, cardiac), CNS, prior malignancy
- Population mix: region, ethnicity (Asian proportion), frailty, cytogenetic/molecular risk
- Subgroups: consistent direction vs underpowered; the interaction test, not the subgroup p-value
- Label vs trial population; local approval wording

## 3. `worth` — Is it worth it?

- Absolute differences (landmark rates, median gains), not only HR
- NNT at a stated time point (speaker's arithmetic)
- Toxicity: grade ≥3, serious AEs, treatment-related deaths, class-specific toxicity
- Quality of life, time on treatment, visit burden
- Cost and reimbursement; duration-of-therapy caps

## 4. `position` — Where does it sit?

- The comparator the room uses today; head-to-head data or the lack of it
- Indirect comparisons and their assumptions
- Newer regimens that challenge it (quadruplets, bispecifics, CAR-T)
- Sequencing: what is left at first relapse if this is used first
- Guideline positions (NCCN, ESMO, EHA-EMN, national societies) and their dates

## 5. `practice` — How do I actually give it?

The branch the AI shell is weakest at and the room is least forgiving about. Aim for ≥12 questions.

- Dose, schedule, cycle length, duration; IV vs SC; split first dose
- Premedication and post-medication; infusion rates
- Dose modifications: renal, hepatic, hematologic, age-based (e.g. dexamethasone in >75)
- Required prophylaxis: antiviral, thromboprophylaxis, PJP, vaccination, IVIG thresholds
- Pre-treatment tests that cannot be done afterwards (e.g. type and screen)
- Monitoring and lab interference
- Drug interactions; pregnancy-prevention programs
- Toxicity management algorithms; when to hold vs reduce vs stop

## Coverage targets

≥50 questions; every branch ≥8; every persona ≥6; `practice` ≥12. `validate.py` prints the branch × persona grid with empty cells marked.
