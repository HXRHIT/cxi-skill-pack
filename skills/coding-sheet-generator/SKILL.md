---
name: coding-sheet-generator
description: "Generate blank or prewired coding workbook skeletons for structured interview activities such as Likert scales, adjective cards, rankings, multiple-choice coding, and short open-response batteries. Use when Codex needs to read an interview guide, protocol, or activity list and build a reusable spreadsheet scaffold before quantitative coding, frequency ranking, or downstream use with interview-quant-coding-skill."
---

# Coding Sheet Generator

## Overview

Use this skill to create workbook skeletons before coding begins.
Read [references/generation-patterns.md](references/generation-patterns.md) when you need workbook packaging patterns, sheet-set rules, or activity-specific layout guidance.
Use `$interview-quant-coding-skill` after this skill when the workbook needs actual coding, ranking, or scoring content.

## Inputs

Gather these inputs when available:
- interview guide, protocol, or activity list
- question ids and answer labels
- participant roster or PID convention
- optional segment or demographic fields
- optional packaging preference such as one workbook per round or one workbook per activity

If the source mixes structured activities with fully open interview prompts, isolate the structured activities first.

## Workflow

### 1. Inventory coding activities

Detect which structured activity types appear in the source.
Common targets include:
- Likert or fixed-scale questions
- adjective cards or label-pick activities
- ranking tasks
- multiple-choice or variant-choice coding
- short open-response batteries that still need structured columns

Keep one sheet group per activity or per tightly coupled question block.
Do not mash unrelated activities into one combined sheet.

### 2. Choose workbook packaging

Default to one workbook per interview round or guide, with separate sheets per activity.
Use one workbook per activity only when the study already maintains separate activity files or the user explicitly wants split delivery.

### 3. Build the sheet skeleton

Read [references/generation-patterns.md](references/generation-patterns.md).
Create only the sheet types supported by the activity.
Typical outputs include:
- participant or metadata sheet
- raw or source sheet when links, images, or note-taking inputs matter
- one matrix, scale, ranking, or response sheet per activity
- count, ranking, or segment summary sheet
- optional insight placeholder sheet when the team expects narrative commentary beside counts

### 4. Keep downstream compatibility

Use human-readable option labels as column headers when labels are available.
Keep PID and stable segment fields on the left.
Keep question ids visible in sheet names or section labels.
Use stable naming so `$interview-quant-coding-skill` can fill or extend the workbook without reorganizing it.

### 5. Prewire formulas, not judgments

Formula helpers are appropriate.
Examples include:
- count formulas
- rank formulas
- concat helpers
- blank summary placeholders

Do not invent coded values, insights, or participant segments unless the source data already exists and the user explicitly asked for prefilling.

## Guardrails

- Do not merge unrelated activities into one tab just to reduce sheet count.
- Do not use opaque code values as primary headers when readable labels are available.
- Do not treat scaffold generation as completed coding.
- Do not drop raw or source holding sheets when the activity depends on links, screenshots, or note-taking support.
- Do not force one packaging style across every project; use the default, but preserve explicit project conventions.

## Expected use cases

Use this skill for prompts such as:
- build a coding workbook from this interview guide
- create the sheet skeleton for these card-sort and adjective questions
- generate a participant-by-option workbook before coding starts
- turn this round-two guide into tabs that `$interview-quant-coding-skill` can use