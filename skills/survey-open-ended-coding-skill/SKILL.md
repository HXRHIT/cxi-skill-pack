---
name: survey-open-ended-coding-skill
description: "Turn open-ended survey responses into structured coding workbooks by generating draft codebooks, applying 1-3 codes per response, summarizing code frequencies, extracting representative quotes, and flagging surprises or outliers. Use when Codex needs to analyze free-text survey responses from .xlsx, .xls, .csv, or extracted response tables for UXR reporting."
---

# Survey Open Ended Coding Skill

## Overview

Use this skill to code free-text survey responses into a reusable workbook-first evidence pack.
Keep the core workflow in this file.
Read [references/workbook-patterns.md](references/workbook-patterns.md) when you need the default sheet set, response-level column schema, codebook rule, or quote and outlier packaging pattern.

Prefer cleaned input from `$survey-data-preprocessing`.
If the source file is still a raw export with unresolved schema issues, clean it before treating the coding output as analysis-ready.

## Inputs

Gather these inputs when available:
- open-ended survey responses in `.xlsx`, `.xls`, `.csv`, or extracted table form
- question labels or a contents sheet
- respondent ID, row ID, or another stable record key
- optional segment fields such as product, cohort, or channel
- optional existing codebook, research questions, or analysis goals
- optional language or translation constraints

If the workbook contains multiple open-ended questions, keep them distinguishable instead of collapsing unrelated prompts into one theme pool by default.

## Workflow

### 1. Isolate the coding target and unit

Identify which question or question set needs coding.
Use one response record as the default coding unit.
Preserve the original response text and stable row identifier so a reviewer can trace every code back to source.

If several open-ended questions ask clearly different things, keep the coding summaries separated by question even when you hand off one combined workbook.

### 2. Draft or adopt the codebook

Read [references/workbook-patterns.md](references/workbook-patterns.md).
If the project already has an approved codebook, use it.
If not, draft a practical starter codebook:
- usually 8 to 15 codes
- one plain-language definition per code
- optional parent theme when roll-up helps
- enough distinction that nearby codes are not synonyms

Treat an AI-generated codebook as draft until reviewed.
Do not pretend the code set is final if the wording still overlaps or the team has not approved the labels.

### 3. Apply 1 to 3 codes per response

Code each response with the smallest set that captures the meaning.
Default to 1 to 3 codes per response.
Allow a review marker or no-code status for blanks, nonsense, off-topic text, or ambiguous cases.

Preserve the exact response text in the coded sheet.
Add a short coder note only when it helps explain ambiguity, nuance, or an outlier decision.

### 4. Summarize frequencies and patterns

Aggregate the coded responses into code-level counts and percentages.
When segment fields exist and the sample is usable, add segment cuts without changing the underlying coding logic.

Keep the summary descriptive.
Do not imply statistical significance from code frequency alone.
If the denominator changes by question or segment, make that visible in the workbook.

### 5. Pull representative quotes and surprises

Select up to two representative quotes per code when the responses are articulate enough to support them.
Also keep a separate place for:
- rare but important responses
- contradictory or surprising responses
- responses that could not be coded confidently

Use this layer to preserve nuance that a pure count table would hide.

### 6. Package the workbook for reuse

Return the default workbook structure described in [references/workbook-patterns.md](references/workbook-patterns.md).
Hand off:
- the response-level coded table
- the codebook sheet
- the summary sheet
- the representative quote sheet
- the outlier or review sheet
- any caveat about draft codes, low base sizes, or unresolved ambiguity

When the coding output is meant to feed a broader survey readout, point the next step toward `$survey-basic-stats-analysis` or `$survey-analysis-verification` as appropriate.

## Guardrails

- Do not merge unrelated open-ended questions into one undifferentiated code pool unless the user explicitly wants that roll-up.
- Do not force more than three codes onto a single response just to make the codebook look complete.
- Do not treat blank, boilerplate, or machine-noise text as meaningful evidence.
- Do not drop the raw response text or stable row identifier from the response-level coding sheet.
- Do not present code frequencies as if they were inferential test results.
- Do not replace interview-first thematic synthesis; use `$qual-thematic-coding-skill` for that workflow.

## Expected use cases

Use this skill for prompts such as:
- code these open-ended survey responses into a workbook
- build a codebook and frequency summary for this survey free-text question
- tag each response with 1 to 3 codes and pull representative quotes
- make an open-ended coding workbook from this cleaned survey export
