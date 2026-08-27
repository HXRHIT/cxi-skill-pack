---
name: survey-analysis-verification
description: "Verify survey analysis outputs before reporting by checking N counts, exclusion rules, stale-data risk, AI-generated claims, low-base handling, and the mapping from RQ or RH to findings. Use when Codex needs to compare survey findings against source data, cleaned inputs, basic-stats outputs, or plan-level RH sheets before dashboards, reports, or stakeholder readouts are finalized."
---

# Survey Analysis Verification

## Overview

Use this skill after survey preprocessing and basic stats analysis, but before reporting or dashboard handoff.
Keep the main verification flow in this file.
Read [references/verification-patterns.md](references/verification-patterns.md) when you need the default output files, verification checklist, low-base rules, or the `verified_key_findings.json` schema.

Prefer inputs from `$survey-data-preprocessing`, `$survey-basic-stats-analysis`, and the plan artifacts that defined RQ or RH.

## Inputs

Gather these inputs when available:
- cleaned survey dataset and codebook
- question-level stats outputs
- RH or RQ document
- source raw data for spot verification
- AI-generated insight draft or summary if one exists
- prior SSOT findings file if one exists

If a supposedly final finding cannot be traced back to a source question, metric, and base size, do not treat it as verified.

## Workflow

### 1. Run the integrity gate

Read [references/verification-patterns.md](references/verification-patterns.md).
Check:
- total N consistency across raw, cleaned, and analyzed outputs
- exclusion-rule consistency
- segment subtotal consistency where relevant
- stale or test-mode artifacts still leaking into final analysis
- codebook and question-map alignment

Record every mismatch explicitly.
Do not silently normalize conflicting N values.

### 2. Verify AI or analyst claims against the numbers

Compare narrative claims to the actual stats rather than to other prose.
At minimum verify:
- directionality such as A is higher than B
- numeric values such as means, shares, and top-box results
- segment differences against the actual test or cross-tab result
- low-base safeguards
- warning markers for borderline base sizes

If a claim cannot be verified numerically, downgrade it to unverified or interpretation-only status.

### 3. Reconnect findings to RQ and RH

Use the plan-level RQ or RH structure when it exists.
Build a matrix that shows:
- which question or metric informed each RH
- which method was used
- whether the result supports, rejects, or leaves the RH inconclusive
- what insight is safe to carry forward
- whether the result should be included in reporting

If a planned RH was never actually tested, label it as unverified rather than pretending the coverage is complete.

### 4. Promote only verified findings into SSOT

Create or update `verified_key_findings.json` using the schema in [references/verification-patterns.md](references/verification-patterns.md).
Only include findings that pass the integrity and evidence checks.
Carry caveats, base size, and source references with each promoted finding.

### 5. Hand off the verification pack

Return the default three markdown files plus the SSOT json file.
Make it obvious which issues block reporting, which issues are warnings, and which findings are fully verified.

## Guardrails

- Do not trust AI-generated survey insight text without checking the underlying numbers.
- Do not let stale caches, test-mode files, or outdated N values pass as final results.
- Do not promote low-base findings into SSOT without the required warning or block.
- Do not mark an RH as supported or rejected if the evidence is only descriptive.
- Do not let findings lose traceability back to the source question, metric, and base size.

## Expected use cases

Use this skill for prompts such as:
- verify these survey findings before we report them
- check whether the AI analysis matches the actual survey data
- confirm our RH tracker and reporting numbers are consistent
- build a final SSOT findings file from these survey outputs