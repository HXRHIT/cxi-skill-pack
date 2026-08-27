---
name: survey-basic-stats-analysis
description: "Analyze cleaned survey datasets by producing question-level descriptive statistics, respondent-versus-response percentages, Likert summary metrics such as mean, standard deviation, and top-box or bottom-box summaries, plus a RH-based hypothesis tracker with methods, decisions, and insights. Use when Codex needs to turn cleaned survey data (.xlsx, .xls, .csv) into analysis-ready stats sheets or a basic survey findings workbook for UXR reporting."
---

# Survey Basic Stats Analysis

## Overview

Use this skill to turn a cleaned survey dataset into question-level stats outputs only after the survey question map and the study's key RQ or RH context are known.
Keep the workflow in this file.
Read [references/analysis-patterns.md](references/analysis-patterns.md) when you need metric rules, the hypothesis-table schema, or default workbook structure.

Prefer cleaned input from `$survey-data-preprocessing`.
If the user only has a raw export, recommend preprocessing first before treating the file as analysis-ready.

## Inputs

Gather these inputs before running question-level stats:
- cleaned survey dataset
- reviewed codebook or variable ledger
- question map or contents sheet
- key RQ list
- key RH list, or an explicit note that the study has no formal RH
- optional analysis metric metadata such as a predefined `Analysis_Metric` field
- optional segment definitions for cross-tabs

If the codebook still shows `needs_review`, keep the output in draft status rather than final analysis status.

## Workflow

### 1. Confirm analysis readiness

Check whether the dataset is clean enough for descriptive stats:
- reviewed codebook exists or major variables are already resolved
- survey questions can be traced to a question map or contents sheet
- key RQ or RH context is present before interpretation begins
- question types are identifiable
- segment fields are stable enough for comparison
- multi-response groups are already normalized enough to count safely

If these conditions are not met, stop short of final interpretation and surface the blockers.

### 2. Build question-level stats by question type

Read [references/analysis-patterns.md](references/analysis-patterns.md).
Use the default metric bundle that matches each question type.

At minimum:
- single-choice questions get counts and percentages
- multi-response questions keep both response-based and respondent-based percentages
- Likert or scale questions get mean, standard deviation, and a documented top-box or bottom-box summary
- open-ended questions get only light structural counts here and should not be treated as coded themes

If analysis metadata already specifies the metric set, follow that instead of inventing a new one.

### 3. Run segment comparisons carefully

Use cross-tabs only when the segment field and sample size make the comparison meaningful.
Distinguish descriptive comparison from inferential testing.
Do not imply statistical significance unless an actual test is run and reported.

When a project already expects repeated segment cuts, keep the layout stable across questions so the workbook is easy to scan.

### 4. Reconnect every stats block to the planned research questions

Use the schema in [references/analysis-patterns.md](references/analysis-patterns.md).
For each RQ or RH in scope:
- record the analysis method actually used
- report the key finding
- record reject or support status only when the evidence justifies it
- add a short insight statement
- mark whether the finding is report-worthy

If the RQ or RH context is missing, do not proceed with final question-level stats. Surface the context gap as a blocker instead.

### 5. Focus on the layer that automatic survey tools miss

Do not spend effort recreating every chart or auto-report flourish from survey platforms.
Prioritize:
- reusable stats sheets
- cross-question consistency
- RH-level tracking
- concise interpretation that can be pasted into team analysis files

### 6. Hand off clearly

Return:
- the default output bundle
- any significance caveats
- unresolved review risks
- recommended next step for dashboarding, verification, or open-ended coding when relevant

## Guardrails

- Do not blur response-based and respondent-based percentages on multi-response questions.
- Do not claim significance without the actual test result and p-value.
- Do not run final question-level stats when the survey question map or key RQ/RH context is missing.
- Do not force RH decisions when the available data is only descriptive.
- Do not treat open-ended responses as themed findings inside this skill.
- Do not override project-specific analysis metrics when they are already declared.

## Expected use cases

Use this skill for prompts such as:
- analyze this cleaned survey workbook question by question
- make a basic stats workbook plus RH tracker from this survey dataset
- compute Likert summaries and segment comparisons for this study
- turn this cleaned csv into report-ready descriptive stats
