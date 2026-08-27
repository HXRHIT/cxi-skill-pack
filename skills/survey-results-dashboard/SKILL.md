---
name: survey-results-dashboard
description: "Turn validated survey analysis outputs into dashboard artifacts by separating a researcher workbench from a stakeholder-facing report, while preserving low-base warnings, segment cross-tabs, and AI insight guardrails. Use when Codex needs to build a survey dashboard or reporting view from cleaned survey stats, RH trackers, or verified analysis workbooks."
---

# Survey Results Dashboard

## Overview

Use this skill to package survey findings into two complementary views: a researcher workbench and a stakeholder-facing report.
Keep the decision workflow in this file.
Read [references/dashboard-patterns.md](references/dashboard-patterns.md) when you need the default module layout, question-block pattern, AI insight layers, low-base rule, or renderer-selection guidance.

Prefer upstream outputs from `$survey-basic-stats-analysis` and `$survey-analysis-verification`.
If the source is still a raw export or unresolved stats draft, route it back upstream before treating the dashboard as report-ready.

## Inputs

Gather these inputs when available:
- validated survey stats workbook or structured summary tables
- question labels, contents sheet, or questionnaire map
- segment comparison outputs
- optional RH or RQ tracker
- optional open-ended coding summary from `$survey-open-ended-coding-skill`
- optional brand tokens or reporting constraints

If the user only says "make a dashboard," default to the dual-output model: researcher workbench plus stakeholder report.

## Workflow

### 1. Confirm dashboard readiness

Check that the survey layer is stable enough to visualize:
- denominators are known
- low-base cases are already identifiable
- significance claims, if any, come from actual tests
- question labels are clean enough for display
- segment outputs are stable enough to compare

If those conditions are not met, stop short of polished storytelling and surface the blockers first.

### 2. Split the audience before choosing the renderer

Build the information architecture around audience first.
Use the dual-output pattern from [references/dashboard-patterns.md](references/dashboard-patterns.md):
- researcher workbench for QA, filters, full cross-tabs, and traceable detail
- stakeholder report for curated interpretation, approved highlights, and lighter navigation

Do not force both audiences into one overloaded surface unless the user explicitly wants that compromise.

### 3. Build the overview layer

Start with the blocks that orient the reader quickly:
- study overview
- sample profile
- key highlights or key risks
- question navigator or contents layer
- optional RH or RQ tracker

Keep the same question naming and metric language the team already uses in the analysis workbook.

### 4. Build one question block at a time

Read [references/dashboard-patterns.md](references/dashboard-patterns.md).
For each question or metric block:
- show the main result clearly
- attach the relevant segment comparison or cross-tab
- keep the low-base or significance note near the claim
- add open-ended evidence only as a companion layer, not as a substitute for the numeric result

Prefer repeatable modules over bespoke page-by-page improvisation.

### 5. Keep AI insight layers explicit

When the dashboard includes generated narrative, separate it into three layers:
- data only
- AI interpretation
- needs judgment

Do not present model-written interpretation as if it were a verified conclusion.
Keep review responsibility visible.

### 6. Choose the rendering layer last

Use the renderer that fits the audience and distribution mode:
- prefer Streamlit or a comparable interactive app when the researcher workbench needs live filtering
- prefer static HTML or document-like views when the stakeholder report needs easy sharing

Treat renderer choice as a delivery layer.
Keep the module structure stable even if the final implementation surface changes.

### 7. Hand off with caveats and next steps

Return:
- which view or views were built
- low-base or significance caveats
- any unresolved AI-review flags
- the recommended next step for report writing, dashboard polishing, or verification

Point downstream to `$report-type-splitter` when the user is really asking for an interim or final report rather than a dashboard surface.

## Guardrails

- Do not let the model free-write conclusions from raw CSV rows.
- Do not hide low-base warnings behind polished charts.
- Do not blur descriptive cross-tabs with inferential significance.
- Do not bury the segment table far away from the claim it supports.
- Do not overload stakeholder views with researcher QA detail by default.
- Do not collapse dashboard and interim-report work into the same artifact unless the user explicitly wants that hybrid.

## Expected use cases

Use this skill for prompts such as:
- build a survey dashboard from this validated analysis workbook
- make a researcher workbench and stakeholder report view for this survey
- turn these survey stats into question-by-question dashboard modules
- create a survey results dashboard with segment highlights and low-base guardrails