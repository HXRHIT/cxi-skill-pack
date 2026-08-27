---
name: survey-data-preprocessing
description: "Prepare raw survey exports for analysis by detecting survey schema, preserving team missing-value conventions, normalizing wide-format multi-select or ranked questions, generating a cleaned dataset plus codebook or variable ledger, and enforcing a human review gate before downstream analysis. Use when Codex needs to convert raw survey response files (.csv, .xlsx, .xls) into analysis-ready survey data."
---

# Survey Data Preprocessing

## Overview

Use this skill when a survey export must become an analysis-ready dataset plus a companion codebook.
Keep the workflow in this file.
Read [references/preprocessing-rules.md](references/preprocessing-rules.md) when you need the question-type rules, output schema, join policy, or review-gate details.

## Inputs

Gather these inputs when available:
- raw survey response file or workbook
- questionnaire, contents sheet, or question map if one exists
- prior codebook or variable notes if one exists
- notes about prescreener joins or participant IDs
- wave or version context when multiple exports exist

If multiple exports or waves are present, inspect schema drift before combining anything.

## Workflow

### 1. Inspect the export structure

Classify the source before editing it:
- identify workbook sheets or csv sections
- separate meta fields, profile fields, and question fields
- detect column-count or version drift across files
- classify question families with the reference type system

### 2. Preserve the default missing-value convention

Treat blank cells as the default for no response or not applicable.
Do not introduce coded missing values such as 99 or -99 unless the user or a downstream tool explicitly requires them.
If you must recode blanks, record that decision in the codebook or variable ledger.

### 3. Normalize complex question layouts

Keep wide format as the default when the export already spreads multi-select or ranked answers across columns.
Validate multi-response groups rather than collapsing them too early.
If duplicate PathA or PathB columns capture the same logical question, merge them and log the exact rule used.

### 4. Build the companion codebook

Always produce the cleaned dataset together with a codebook or variable ledger.
Use the ledger schema in [references/preprocessing-rules.md](references/preprocessing-rules.md).
Mark:
- question type
- scale or measurement level
- missing-value handling
- derived variables
- source columns
- preprocessing decisions
- needs_review status

### 5. Protect downstream analysis

If the codebook is still draft or `needs_review` is true, do not present the output as fully analysis-ready.
Surface unresolved type mismatches, schema drift, join failures, or duplicate-question ambiguity.
Include a short review checklist with the output so a human can clear the gate.

### 6. Maintain join readiness

Preserve or create stable PID keys when prescreener data and main survey responses must be joined later.
Record join keys, unmatched records, and any assumptions about participant identity.
Do not silently merge participant-level data on weak identifiers.

## Guardrails

- Do not silently collapse multi-response questions into a single text field.
- Do not replace blanks with coded missing values unless the workflow truly needs it.
- Do not merge waves with incompatible column layouts without a drift summary.
- Do not bypass the codebook review gate just because a cleaned file exists.
- Keep raw source files unchanged.

## Expected use cases

Use this skill for prompts such as:
- clean this raw survey export for analysis
- make a codebook and variable ledger from this survey workbook
- compare two survey exports and prepare one cleaned analysis file
- preprocess this csv before stats and dashboard work