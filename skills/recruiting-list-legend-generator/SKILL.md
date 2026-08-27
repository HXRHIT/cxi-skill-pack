---
name: recruiting-list-legend-generator
description: "Generate usage and legend sheets for recruiting rosters, participant-profile workbooks, and screener handoff files. Use when Codex needs to inspect a recruiting workbook and explain file purpose, stage, columns, PID conventions, and stage-specific flow before recruiting, screening, or transcript linkage."
---

# Recruiting List Legend Generator

## Overview

Use this skill to make recruiting workbooks self-explanatory.
Read [references/legend-patterns.md](references/legend-patterns.md) when you need observed stage-packaging rules, PID standards, or guide-sheet patterns.
Use `$transcript-anonymizer-skill` when names or PII must be replaced.
This skill is about workbook explanation, stage structure, and linkage clarity.

## Inputs

Gather these inputs when available:
- recruiting roster, participant-profile workbook, or screener handoff file
- study stage or recruiting plan
- PID convention or `pid_map.csv` if it already exists
- optional downstream linkage needs such as transcript, coding, or survey joins

If the workbook mixes several recruiting stages, identify each stage before writing the guide sheet.

## Workflow

### 1. Classify the workbook stage

Determine whether the file is primarily:
- candidate pool
- selected shortlist
- confirmed schedule
- screener handoff
- mixed-stage workbook with separate tabs
- **sample-composition summary** — a distribution sheet (성별 / 연령대 / 세그먼트 counts) that sits beside a roster rather than listing participants
- **raw / final split** — two separate files for the same participants, where `final` is a column-level rework of `raw` (see step 4a)

Do not assume every recruiting workbook serves the same stage.

A sample-composition summary is almost always hard-coded, not formula-driven. In `24.ST.GBI`'s `요약` sheet every count is a literal value (0 formula cells), so editing the roster does not update it. Always check for formulas and warn in the guide when the summary cannot self-update.

### 2. Generate the guide sheet

The guide sheet must end up at **index 0**, not merely appended. Use `scripts/add_guide_sheet.py`, which does the reorder and then verifies it (`guide_is_first_sheet`).

Before writing column explanations, check where the screener question text lives. Three cases occur in real workbooks and they need different guide text:

| Case | Example | What the guide says |
|---|---|---|
| Question number + full text in the header | `25.S.HANAEZ`: `Q27: 참여하신 분의 이름과 이메일을 알려주세요.` / `24.ST.GBI`: 6 Likert items whose full sentences are the column names | State that the header is the question. Do not ask for a separate questionnaire link |
| Question number only | `25.S.1QPLAY`: `Q1`~`Q6` with no text anywhere in the file | Say the text is not recoverable from this file and point to the questionnaire/guide document |
| No question columns | roster-only files | Nothing to say |

Create a leading guide or usage sheet that explains:
- file purpose
- current stage or covered stages
- who updates the sheet
- when key columns are filled
- which columns are source data versus derived fields
- how the workbook connects to later research artifacts

### 3. Generate the PID legend

Read [references/legend-patterns.md](references/legend-patterns.md).
Default to the simple sequential PID pattern such as `P001`, `P002`, and `P003`.
Explain segment, round, cohort, or session grouping through separate columns or lookup tables rather than encoding them inside the PID itself.
When `pid_map.csv` exists, align the legend with that map instead of inventing a parallel scheme.

**Read the project's existing PID before applying the default.** Observed reality (2026-08-27 forward validation) does not match the default, and the default must never overwrite a live convention:

| Project | Actual PID |
|---|---|
| `24.ST.GBI` | `P19` ~ `P26` — no zero padding, and the **2차 roster starts at 19: numbering continues across rounds rather than resetting** |
| `25.S.1QPLAY` | three coexisting identifiers — `user_id` / `UserID` / `스터디 식별 번호` |
| `25.S.HANAEZ` | **no PID column at all** — only the vendor platform's own `ID` (24, 25, 36 …), non-contiguous |

Consequences to honor:
- Never renumber a later round from 1. Continue from the highest PID already issued in the project.
- When only a vendor ID exists, assign researcher PIDs but keep the vendor ID as its own `vendor_id` column — it is the only key for going back to the recruiting vendor. Keep the PID ↔ vendor_id mapping in a separate `pid_map.csv`, not inside the roster.
- `$transcript-anonymizer-skill` writes PIDs in bracketed form (`[P001]`). This skill writes bare (`P001`). That inconsistency is unresolved — state which form the project uses in the guide rather than silently picking one. No `pid_map.csv` has been found in any native project yet, so treat it as a convention to create, not one to read.

### 4. Preserve stage separation

When the workbook clearly represents multiple recruiting stages, prefer separate sheets or separate files rather than collapsing everything into one status column.
If the source already uses one stable sheet with a well-defined status workflow, document that structure rather than forcing a refactor.

### 4a. Describe the raw → final relation when the project splits them

When a project keeps `raw` and `final` as separate files for the same participants, the guide's job is to state the transformation, not just to label each file. Measure it rather than assuming:

- which columns were **dropped** (and whether a `//…제외` marker explains why)
- which columns were **split or merged** — `24.ST.GBI`: raw's `현재 보유 및 납부 중 연금` became final's `보유중인 개인 연금` + `보유 중인 퇴직연금`
- whether the **row set changed** — in `24.ST.GBI` it did not (8 participants, P19~P26, identical in both). raw→final was a column rework, not a filter
- which file downstream work should read (normally `final`; `raw` is for checking what was asked and discarded)

### 5. Flag risky or stale fields

Call out columns or prompts that are unclear, unnecessary, or risky for the current study.
Common examples include:
- hard-coded screener questions that do not match the current project
- missing explanation for consent, contact, or attendance fields
- ambiguous stage labels
- unlabeled derived columns or copied formulas
- **hard-coded aggregate sheets** — a summary whose counts are literals, so it silently goes stale when the roster changes (`24.ST.GBI` `요약`: 0 formula cells)
- **derived columns with no visible formula** — `24.ST.GBI` `금융 관심도` holds values like `4.1666666…` that look like the mean of the 6 Likert columns, but no formula exists anywhere in the file. Say what it appears to be *and* that the derivation is unrecorded; do not present the guess as fact
- **header whitespace and inconsistent value spellings** — `24.ST.GBI` final has a column named `' 로보어드바이저 …'` with a leading space, and `1~3년` / `1 ~ 3년` both appear as values. Both break joins quietly
- **vendor platform metadata mistaken for participant data** — `25.S.HANAEZ`: `ID · Time Started · Active Time · Progress · Quality score` come from the recruiting vendor's tool. Mark them as non-analytic, and note when the scoring rule is not in the file

### 5a. Preserve the team's own deprecation markers

Teams already annotate dead columns in the header. `24.ST.GBI`'s raw roster marks three columns `//2차 사전설문에서 제외`, and the final file actually drops them.

That marker is often the **only** record of why a column disappeared. When you rewrite or copy a workbook, keep it verbatim. Do not clean it up, and do not invent a competing notation.

## Guardrails

- Do not expose real PII in legend examples.
- Do not invent stage meaning without workbook evidence or a study brief.
- Do not replace the project PID convention with a new one unless the user explicitly asks.
- Do not merge distinct stage sheets unless the user explicitly wants that simplification.
- Do not treat this skill as a replacement for anonymization, recruiting operations, or live participant management.

## Expected use cases

Use this skill for prompts such as:
- add a usage and PID legend sheet to this recruiting workbook
- make this participant-profile file understandable for a new researcher
- explain the columns and stages in this screener handoff file
- align this recruiting list with the project PID standard before transcript work starts