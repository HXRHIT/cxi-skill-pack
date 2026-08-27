---
name: interview-quant-coding-skill
description: "Convert interview free responses into fixed-tag quantitative coding workbooks by building per-question true-false matrices, frequency rankings, insight tabs, and optional scoring-based participant segments. Use when Codex needs to transform qualitative interview answers into structured question-level coding sheets or participant scoring outputs for comparison and summary."
---

# Interview Quant Coding Skill

## Overview

Use this skill when interview responses need structured, repeatable tag matrices or scoring outputs.
Keep the core workflow in this file.
Read [references/workbook-patterns.md](references/workbook-patterns.md) when you need the workbook layout, tag-matrix rules, or scoring pattern.

This skill is the quantitative counterpart to `$qual-thematic-coding-skill`.
Use it for fixed tags, matrices, and scoring.
Do not use it for open thematic synthesis or affinity mapping.

## Inputs

Gather these inputs when available:
- interview transcripts or extracted responses
- question-level fixed tag list, adjective list, or coding rubric
- participant metadata or segment fields
- optional scoring rules for persona or behavior labels
- optional target question list when only some questions need coding

If the fixed tag list does not exist, propose one first and mark it for review before treating the matrix as final.

## Workflow

### 1. Separate question-level coding targets

Identify which interview question or response set needs matrix coding.
Keep one coding unit per target question or target construct.
Do not mash unrelated questions into one combined matrix.

### 2. Build the fixed-tag matrix

Read [references/workbook-patterns.md](references/workbook-patterns.md).
For each target question:
- use the approved tag list
- code each participant as true or false for each tag when the evidence supports it
- preserve the evidence source so a reviewer can trace the code back to a response

If the evidence is ambiguous, mark it for review instead of forcing a true or false value.

### 3. Rank tags and summarize patterns

Aggregate tag frequencies by question, variant, or service option as needed.
Produce rankings and a short insight summary beside the matrix output.
Keep the summary grounded in the counts rather than rewriting the whole transcript.

### 4. Apply scoring when the project uses it

If the study has explicit scoring rules, combine coded fields into participant-level scores or segment labels.
Document the scoring logic and keep the derived fields visible in the workbook.
Do not invent composite scores without a stated rule.

### 5. Package the workbook for reuse

Return the default workbook structure described in [references/workbook-patterns.md](references/workbook-patterns.md).
Use stable sheet names so the workbook can be compared across questions or projects.

## Guardrails

- Do not replace open qualitative coding with this skill when the task needs interpretation-first synthesis.
- Do not create fixed tags and score participants as if the rubric were objective when it is still draft.
- Do not hide ambiguous evidence behind forced binary labels.
- Do not merge separate questions into one summary matrix unless the user explicitly wants that roll-up.
- Do not drop the companion insight or ranking view from the workbook.

## Expected use cases

Use this skill for prompts such as:
- build a fixed-tag coding workbook for this interview question
- code these free responses into a true-false matrix and rank the tags
- score participants from these coded interview answers
- create a question-by-question interview coding workbook with insight tabs