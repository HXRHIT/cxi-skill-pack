---
name: research-qa-skill
description: "Review research questionnaires, survey forms, and interview guides for bias, mapping gaps, domain-risk issues, and editing defects. Use when Codex needs to quality-check an instrument before fieldwork with a fixed checklist, severity labels, and Hana-finance-specific guardrails."
---

# Research QA Skill

## Overview

Use this skill to review a questionnaire, survey form, interview guide, or mixed protocol before fieldwork.
Apply the fixed checklist in [references/checklist.md](references/checklist.md) instead of inventing ad hoc criteria on each run.

## Inputs

Gather these inputs when available:
- the primary instrument file or pasted content
- an optional RQ/RH document
- optional audience or segment context
- optional notes about method constraints or compliance concerns

If an RQ/RH document is missing, do not block. Run the reverse-mapping step and propose missing RQ/RH candidates from the questions themselves.

## Workflow

### 1. Classify the instrument

Classify the input as one of:
- survey or questionnaire
- interview guide
- mixed document with separate sections

If the document is mixed, review each section with the correct branch of the checklist.

### 2. Load the fixed checklist

Read [references/checklist.md](references/checklist.md).
Use:
- A, B, and C on every instrument
- D-survey only for survey sections
- D-interview only for interview sections
- E and F once at the full-document level

### 3. Review section by section

For each issue:
- quote or point to the exact wording that triggered the flag
- assign Critical, Moderate, or Minor severity
- explain why the wording is risky
- suggest a focused fix

Do not rewrite the entire instrument unless the user explicitly asks for a full rewrite.
Prefer local edits that preserve the author's intent.

### 4. Check RQ and RH alignment

If RQ or RH context exists:
- run forward mapping to confirm each RQ or RH has supporting questions
- run reverse mapping to find questions that are out of scope

If RQ or RH context does not exist:
- skip forward mapping
- run reverse proposal only and infer likely missing RQ or RH candidates

### 5. Confirm every checklist category was actually checked

Before writing the report, go back through A, B, C, the applicable D set, E, and F one category at a time and confirm each was actually applied — not just the categories that happened to surface a finding first. A category with no issue is a valid outcome, but it must be an explicit "checked, no issue" rather than a silent omission. This step exists because a real review pass skipped A4 (order effect), D-I2 (rapport order), and B2 (method-question fit) entirely on a first attempt and only caught the gap when a user asked about it directly — treat that as the standard this step is meant to prevent.

### 6. Produce the default report

Return a markdown review with these sections:

1. Overall verdict
2. High-severity issues first
3. Issues table
4. RQ/RH mapping notes
5. Suggested rewrite snippets
6. Category coverage note — which categories had findings and which were checked with no issue (this makes silent omissions visible to the reader, not just to you)
7. Remaining review risks

Use this default issues table schema:
- ID
- Severity
- Section or question
- Checklist item
- Problematic text
- Why it matters
- Suggested fix

## Guardrails

- Use the fixed checklist categories before adding any new criterion.
- If you add a new criterion from concrete evidence, label it as a new pattern rather than silently folding it into the checklist.
- Treat placeholder leakage, stale numbering, overly positive framing, and pre-framed moderator questions as first-class issues.
- Keep domain-specific finance and privacy risks visible even if the wording looks polite.
- Do not report only the categories that happened to surface findings — state explicitly which categories were checked and came back clean, so a clean result reads as "checked" rather than "skipped."
- Distinguish document-level bias from single-question wording issues.

## Expected use cases

Use this skill for prompts such as:
- review this questionnaire before we send it
- QA this interview guide for bias and compliance risk
- check whether these questions really map to our RQ and RH
- find broken wording, leading questions, or edit leftovers in this protocol
