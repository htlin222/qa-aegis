# Changelog

All notable changes are listed here. Versions follow [SemVer](https://semver.org/); the release workflow takes the notes for a tag from the matching section below.

## [0.1.0] - 2026-11-13

### Added
- Skill workflow (`SKILL.md`): Argdown claim maps → MECE sweep (5 branches × 5 personas) → AI-shell simulation → Cynefin triage → first-principles answers → sourced build.
- References: MECE branches, personas, Cynefin playbook, first-principles library, Argdown guide, source policy, YAML schema.
- `scripts/build.py`: one YAML → `kit.html`, `kit.pptx` (linked contents, one slide per question, script in notes), `pocket.pdf` (one A4 page).
- `scripts/validate.py`: schema check, branch × persona coverage grid, unverified list.
- Worked example: MAIA (D-Rd, transplant-ineligible NDMM), 65 questions.
- CI (validate + build + output checks) and tag-driven release workflow.
