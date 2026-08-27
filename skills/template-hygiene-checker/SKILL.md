---
name: template-hygiene-checker
description: Inspect reusable UXR template files and skill-pack artifacts for leftover real project data, confidential identifiers, unresolved comments, placeholders, and editing residue before team reuse or distribution. Report findings first; do not modify originals by default.
---

# Template Hygiene Checker

Use this skill when the user asks to inspect a reusable template, report deck, document, spreadsheet, generated skill pack, or template folder for hygiene issues before reuse or distribution.

This skill is for template artifacts, not participant research data. For participant transcript or survey PII checks, use `transcript-anonymizer-skill` instead.

## Default behavior

- Run in `report-only` mode unless the user explicitly asks for a cleaned copy.
- Never modify source templates in place.
- Treat detected high-risk items as escalation findings, not auto-deletion targets.
- Preserve comments that may be evidence of unresolved data-quality or verification issues.
- If a file is inside `native/`, read only and do not write beside it.

## What to inspect

Typical targets:

- `.pptx`, `.docx`, `.xlsx`, `.csv`, `.md`, `.html`, `.json`
- exported Google Slides/Docs/Sheets files
- `.agents/skills/*` content before team distribution
- `website/` and generated catalog artifacts before sharing
- distribution bundles created by `discovery-catalog`

## Finding categories

Read [references/hygiene-taxonomy.md](references/hygiene-taxonomy.md) when classifying findings or changing detection rules.

Core categories:

- `real_project_identifier`: actual project, service, organization, location, schedule, or deck title left in a reusable template
- `direct_pii`: names, phone numbers, email addresses, account-like numbers, IDs
- `placeholder_conflict`: placeholder tokens coexist with plausible real values for the same field
- `editing_residue`: repeated dummy text, broken text, unresolved TODOs, duplicate outline labels
- `comment_unresolved`: comments or notes that mention data mismatch, quote reliability, sample size, or verification needs
- `distribution_leak`: internal paths, drive locations, local user names, API keys, or environment-specific secrets in files intended for team sharing

## Recommended workflow

1. Confirm target paths and output directory.
2. Scan files with `scripts/scan_template_hygiene.py`.
3. Review `hygiene_report.md` first, then CSV/JSON if detailed triage is needed.
4. Escalate high-risk findings to the researcher or template owner.
5. Only create a cleaned copy when the user explicitly asks and the change is low-risk.

## Script

Run:

```bash
python .agents/skills/template-hygiene-checker/scripts/scan_template_hygiene.py <target_path> --output-dir validation_runs/template-hygiene-checker/<run_name>
```

Outputs:

- `hygiene_report.md`
- `hygiene_findings.csv`
- `hygiene_findings.json`

The scanner is intentionally conservative. It detects text residue and likely sensitive values, but it does not prove a file is safe. Human review remains required for release.

## Severity

- `critical`: direct secrets, account-like identifiers, or explicit participant/customer identifiers in reusable artifacts
- `high`: actual project/service/location/schedule residue, unresolved verification comments, internal paths in distributed artifacts
- `medium`: placeholder conflicts, TODOs, broken text, ambiguous organization names
- `low`: cosmetic dummy text, repeated filler, weak residue signals

## Related skills

- `transcript-anonymizer-skill`: participant data PII inspection
- `research-qa-skill`: questionnaire/interview-guide QA
- `survey-analysis-verification`: data and finding consistency checks
- `discovery-catalog`: distribution packaging and catalog sync
