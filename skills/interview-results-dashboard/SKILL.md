---
name: interview-results-dashboard
description: "Turn interview coding outputs into dashboard-style synthesis artifacts by combining participant profile views, cross-interview theme summaries, and optional issue-catalog packaging. Use when Codex needs to convert qualitative interview findings, coding workbooks, or quick-summary notes into a shareable interview results dashboard, quick summary table, or reusable component and issue library before executive one-pagers or report writing."
---

# Interview Results Dashboard

## Overview

Use this skill to package interview findings into connected dashboard layers: a quick summary surface for immediate reading, a browsable dashboard page for inspection, an optional report-style detail layer for deeper review, and an optional issue-catalog layer for downstream reuse.
Keep the main decision workflow in this file.
Read [references/dashboard-patterns.md](references/dashboard-patterns.md) when you need the default summary structure, participant-card rule, theme-block rule, issue-catalog schema, or nearby-skill boundaries.

Prefer upstream outputs from `$qual-thematic-coding-skill`.
Use `$interview-quant-coding-skill` or `$survey-basic-stats-analysis` only as companion evidence layers when the interview summary needs structured counts or supporting metrics.
If the source is still raw transcript text, fragmented notes, or unresolved coding, route it back upstream before presenting the work as a dashboard artifact.

## Inputs

Gather these inputs when available:
- participant metadata such as PID, segment, involvement level, or notable context
- participant-level coding files or grounded summary notes
- cross-interview synthesis or affinity outputs
- optional companion metrics from quantitative coding or related survey work
- optional menu, feature, or component taxonomy
- optional reporting constraints or an existing quick-summary shell

If the user only says "make an interview dashboard," default to:
- quick summary
- participant and theme dashboard blocks

Add the issue-catalog layer only when downstream reuse or taxonomy-based lookup is part of the request.
If the user asks to align with an existing internal dashboard reference, prefer the layered surface pattern in [references/dashboard-patterns.md](references/dashboard-patterns.md) instead of stopping at a flat summary page.

## Workflow

### 1. Confirm evidence readiness

Check whether the input is stable enough to summarize:
- participant-level evidence exists
- cross-interview themes are grounded in real quotes or coding output
- contradictions or segment splits are not being flattened away
- any companion numeric metric has a known source

If those conditions are not met, stop short of polished dashboard packaging and surface the missing evidence first.

If transcript quality is poor, recommend `$transcript-verification-enhancer` or `$transcript-pipeline-skill`.
If identifiers remain in shareable materials, recommend `$transcript-anonymizer-skill` before wider distribution.

### 2. Choose the output layer before choosing the renderer

Build the package around the use case first.
Use the default layering from [references/dashboard-patterns.md](references/dashboard-patterns.md):
- quick summary for immediate reading and circulation
- participant and theme view for inspection and discussion
- optional report-style detail view for long-form review
- optional issue catalog for downstream reuse

Do not force every project into a reusable issue library if the actual need is only a concise summary.
Likewise, do not stop at a single overview block if the user clearly needs participant-level traceability.

### 3. Build the quick-summary spine

Start from the compressed summary layer.
Use the observed two-column summary pattern when it fits the material:
- study or phase basics
- participant mix or context
- prior behavior or relevant background
- cross-interview theme blocks
- trust, expectation, or attitude blocks when relevant
- recommendation or implication block

Keep this layer easy to scan.
Treat it as a fast reading surface, not a full interim report.
Treat the Top 3 as evidence-backed summary labels, not blind raw top-N output.
Semantic merging or researcher override is acceptable when generic buckets would hide the real design signal.
Do not force every project into the same shell.
If the source pack behaves more like an executive bullet memo with a compact profile table, keep that summary style instead of converting it into a fake `구분 | 상세 내용` table.

If the user wants a reference-dashboard-like surface, add:
- hero summary
- top priority or key-theme jump cards
- a visible project overview block
- direct links to deeper theme or participant sections

### 4. Build participant and cross-interview views together

The default dashboard should preserve both perspectives:
- participant-level cards or blocks
- overall theme synthesis

Do not choose only one by default.
For each participant block, keep the summary compact and evidence-backed.
For each theme block, include the qualitative Top 3 pattern and keep contradictions or segment splits visible.

When companion metrics exist, place them next to the relevant theme instead of separating qualitative and quantitative evidence into different worlds.
For PAYAI-style mixed-method rows, a practical micro-pattern is:
- current behavior or usage split
- qualitative Top 3 theme labels
- AI expectation or intention metric
When building a longer HTML surface, prefer theme-first blocks with:
- one headline summary
- which participants or segments support it
- quotes or grounded evidence
- contradiction or split note
- implication or improvement direction

If the surface becomes long, use a sticky table of contents or jump navigation so readers can move between summary, themes, participants, and appendix-like sections.

### 5. Expand into an issue catalog only when the project supports it

If the project already has a menu, feature, or component taxonomy, or if the user explicitly wants a reusable issue library, normalize the findings into the issue-catalog layer.
Read [references/dashboard-patterns.md](references/dashboard-patterns.md).
Typical columns include:
- related menu or flow
- component
- component detail
- issue summary
- user evidence or quote
- improvement guide
- source section or link

Treat this as a reuse asset, not as the mandatory default output.
If the project lacks a stable taxonomy, keep the issue layer lighter or state that a component catalog was not generated.
If what the project actually needs is category-grouped improvement recommendations rather than a reusable menu/component lookup, do not stretch the issue-catalog schema to fit — use the lighter compact recommendation table instead (see [references/dashboard-patterns.md](references/dashboard-patterns.md) §6A-2).

### 6. Choose the rendering layer last

Select the delivery surface that fits the audience:
- markdown or docx-style tables for quick summary circulation
- static HTML blocks when a readable dashboard surface is enough
- workbook tables when the issue catalog will be maintained or filtered later

For reference-dashboard-like HTML, keep these layers visually distinct:
- summary page
- dashboard page
- report-style page

Do not confuse those layers with separate research conclusions.
They are alternate reading depths over the same evidence pack.

Treat the renderer as the final wrapper.
Keep the information architecture stable even if the final output format changes.

### 7. Hand off with caveats and next steps

Return:
- which output layers were built
- which quick-summary variant was used
- whether participant and theme views were both preserved
- whether a report-style detail layer was added
- whether companion metrics were included
- whether an issue catalog was generated or intentionally omitted
- the main caveats around sample spread, contradictions, or taxonomy gaps

Point downstream to:
- `$executive-one-pager-skill` when the user wants an executive condensation
- `$report-type-splitter` when the user is really asking for an interim or final report body, not just a compact block pulled out of one — see [references/dashboard-patterns.md](references/dashboard-patterns.md) §8A for the signal checklist
- `$heuristic-evidence-linker` when the user needs screenshot-to-issue evidence linkage rather than summary packaging — see §8B

## Guardrails

- Do not present raw transcript impressions as if they were already coded findings.
- Do not collapse participant-level variation into a single generic team summary.
- Do not invent numeric backing for a qualitative claim.
- Do not treat a vivid single quote as a universal pattern.
- Do not force a component or menu taxonomy onto a project that never used one.
- Do not confuse a dashboard artifact with a full narrative report.
- Do not mistake appendix comparison tables or report chapter scorecards for the quick-summary shell.
- Do not hide contradictions just to make the summary look cleaner.
- It is fine to pull one compact block (such as a recommendation table) out of an otherwise narrative report, but do not rewrite or restructure that report's narrative body — hand that off to `$report-type-splitter`. See [references/dashboard-patterns.md](references/dashboard-patterns.md) §8A.
- Do not match or re-link screenshots to issues yourself. Only show an image when it is already reliably linked; otherwise point to `$heuristic-evidence-linker` instead of fabricating a placeholder. See §8B.

## Expected use cases

Use this skill for prompts such as:
- turn these interview coding files into a quick summary dashboard
- make participant cards and a cross-interview theme view from these interview findings
- package these interview insights into a shareable summary plus reusable issue catalog
- create an interview results dashboard before writing the executive summary
