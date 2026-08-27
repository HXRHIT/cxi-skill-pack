# Verification patterns for survey-analysis-verification

## 1. Default output pack

Produce this pack as the default verification bundle:
- data_integrity_check.md
- ai_verification_report.md
- rq_rh_verification_matrix.md
- verified_key_findings.json

Treat the json file as the promoted SSOT for verified numeric findings in v1.
Do not use it as a dumping ground for tentative interpretations.

## 2. Integrity checklist

Check at least these items:
- total N matches across raw, cleaned, and analysis artifacts
- exclusion rules are consistent
- segment counts roll up correctly
- valid-response counts match the codebook expectations
- stale or test-mode artifacts are not being used as final sources
- version or filename drift is documented

Use clear statuses such as:
- pass
- warning
- fail

## 3. AI verification report rule

Compare prose claims to numbers, not to other prose.
Use these default result labels:
- match
- mismatch
- warning
- unverifiable

For each checked claim, capture:
- claim_id
- claim_text
- source_metric
- source_value
- comparison_result
- explanation

## 4. Low-base rule

Apply the team-style base-size gate:
- base_n < 30 -> block insight promotion
- base_n 30 to 49 -> allow only with a visible low-base warning
- base_n 50+ -> normal handling unless another risk exists

If a segment insight violates the base rule, keep it out of `verified_key_findings.json`.

## 5. RQ and RH verification matrix schema

Use this default schema:
- RQ_number
- RH_number
- source_question_ids
- analysis_method
- key_result
- p_value_or_basis
- decision
- insight
- report_include
- verification_note

Use `descriptive_only` or `inconclusive` when formal testing was not actually run.

## 6. SSOT json schema for v1

Each promoted finding should carry enough traceability to survive downstream reuse.
Use this minimal schema per finding object:
- finding_id
- rq_ids
- rh_ids
- source_question_ids
- metric_name
- metric_value
- segment
- base_n
- exclusion_rule
- verification_status
- caveat
- narrative_summary

Keep values grounded in already-verified numbers.
If a field is unknown, leave it empty or null rather than inventing it.

## 7. Stale-data rule

If multiple candidate truth sources exist, prefer the explicitly maintained SSOT or the latest verified generated source.
When a stale N or stale file is detected:
- record the mismatch
- identify the promoted source of truth
- keep the stale value out of final reporting

## 8. What this skill is and is not

This skill is for validation, gating, and traceability.
It is not the place to:
- rerun the entire preprocessing workflow
- invent new hypotheses late in the process
- create the full dashboard layer
- replace open-ended coding or qualitative synthesis