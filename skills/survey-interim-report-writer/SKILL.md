---
name: survey-interim-report-writer
description: "Turn validated survey analysis outputs into a formal survey interim report that preserves key metrics, base counts, competitive or driver evidence, and a bridge to the next interview phase. Use when Codex needs to draft or refine a document-style survey interim report from verified survey findings, update an existing interim report by appending a new latest version, or generate a polished markdown draft before producing a docx draft."
---

# Survey Interim Report Writer

## Overview

Use this skill to write survey interim reports in two stages:
1. improve a high-quality markdown draft
2. generate a docx draft and append it as the latest version when an existing interim document is being updated

Keep the decision workflow in this file.
Read [references/report-patterns.md](references/report-patterns.md) when you need the default section order, append-latest rule, dashboard boundary, or report-quality checklist.

Prefer upstream outputs from `$survey-basic-stats-analysis` and `$survey-analysis-verification`.
If the source is still a raw export or an unresolved stats mismatch, route it upstream before treating it as report-ready.

## Inputs

Gather these inputs when available:
- validated survey stats workbook or structured summary tables
- verification notes, denominator checks, or RH/RQ mapping outputs
- segment or base definitions
- benchmark, ranking, or driver-analysis tables
- existing survey interim document when the task is an update rather than a fresh draft
- audience or tone constraints if the team has them

If the user asks for a survey report without saying whether it is a new draft or an update, infer update mode when an existing interim document is already in scope. Otherwise start with a fresh markdown draft.

## Workflow

### 1. Confirm interim-report readiness

Check that the survey layer is stable enough to report formally:
- bases and denominators are known
- low-base cases are identifiable
- significance or driver claims come from actual analysis, not guesswork
- key labels are clean enough for reporting
- the findings are stable enough to hand off into interview planning

If those conditions are not met, stop short of polished reporting and surface the blockers first.

### 2. Draft the report in markdown first

Read [references/report-patterns.md](references/report-patterns.md).
Use its default section order unless the project already has a stronger house structure.

Build a markdown report draft that:
- leads with clear claims, not dashboard labels
- keeps metrics, bases, and comparisons close to the claim
- preserves survey-specific evidence rather than blending in other methods
- ends with a `next_interview_plan` bridge when unresolved questions remain

### 3. Raise draft quality before touching docx

Before generating a docx draft, tighten the markdown version:
- strengthen headings into complete claim sentences
- remove unsupported interpretation
- keep low-base and uncertainty caveats visible
- check that each major section still reads like a formal interim report, not a dashboard page

If the markdown draft is still structurally weak, keep working there instead of formatting early.

### 4. Generate the docx draft after the markdown is stable

Use the improved markdown draft as the source for the docx draft.
Preserve report structure, tables, and bridge sections rather than re-improvising from scratch during document formatting.

If document tooling is available in the environment, use it for the docx conversion stage rather than relying on plain-text formatting alone.

### 5. Append and mark the latest version by default

When an existing interim document is present:
- append the new version block instead of overwriting the previous one
- preserve earlier versions for traceability
- mark the appended block as the latest version
- match the file's visible versioning convention when possible

Only replace rather than append if the user explicitly asks for a clean replacement workflow.

### 6. Hand off with reporting caveats

At the end of the draft, list:
- assumptions you had to make
- unresolved verification or low-base caveats
- what should flow into the next interview phase

Point downstream to `$report-type-splitter` when the user is actually deciding among report families rather than drafting a survey interim specifically.

## Guardrails

- Do not write a formal interim report from raw exports or unresolved stats drafts.
- Do not hide low-base warnings behind polished prose.
- Do not blur descriptive patterns with significance claims unless the analysis really supports them.
- Do not collapse survey dashboard work into interim-report writing by default.
- Do not overwrite existing interim versions when update mode is in scope.
- Do not generate the docx draft before the markdown draft is logically and stylistically stable.

## Expected use cases

Use this skill for prompts such as:
- turn this validated survey analysis into an interim report draft
- update our existing survey interim document with the latest findings
- write a formal survey report that ends with the next interview plan
- make a polished markdown survey interim report, then produce a docx draft
