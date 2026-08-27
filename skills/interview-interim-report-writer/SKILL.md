---
name: interview-interim-report-writer
description: "Turn qualitative interview coding output into a formal interview interim report — Executive Summary, research overview, topic-grouped claim-sentence insights with representative quotes, an improvement-direction section, and an appendix — matching the team's real interview interim report structure. Use when Codex needs to draft or update a document-style interview interim report from coded interview findings, as distinct from an interview results dashboard or a quick-summary artifact."
---

# Interview Interim Report Writer

## Overview

Use this skill to write formal interview interim reports — the report body itself, not a dashboard or a compressed summary. Keep the core decision workflow in this file.
Read [references/interview-interim-patterns.md](references/interview-interim-patterns.md) when you need the full section skeleton, the exact quote-citation format, the native evidence behind them, or the boundary rules with nearby skills.

Prefer upstream output from `$qual-thematic-coding-skill` (individual participant coding plus cross-interview synthesis). Use `$interview-quant-coding-skill` output as a companion when structured tags or scores exist.
If the source is still raw transcript text or unresolved coding, route it back upstream before treating it as report-ready.

This skill produces a different artifact than `$interview-results-dashboard`: that skill compresses findings into a fast-reading circulation surface (quick summary, participant cards, theme dashboard); this skill writes the formal document that goes out as the interim deliverable itself, with a different citation convention (see [Workflow §4](#4-cite-representative-quotes-in-the-report-citation-format), not the dashboard's traceability-tag format). If the user's actual need is the lighter circulation surface, point to `$interview-results-dashboard` instead of writing a full report here.

## Inputs

Gather these inputs when available:
- participant-level coding output and cross-interview synthesis (ideally from `$qual-thematic-coding-skill`)
- participant metadata (PID, demographics, segment/persona label)
- a study overview: purpose, what was observed, method, period
- an existing interview interim document, when the task is an update rather than a fresh draft
- companion quantitative context (survey scores, base counts) when the study is mixed-method

If the source material's location isn't already known — not provided in the conversation and not clearly identifiable — ask the user to send it or point to it rather than guessing a path or drafting from assumption.

## Workflow

### 1. Confirm interim-report readiness

Check that the qualitative layer is stable enough to report formally:
- claims are grounded in actual coded evidence, not raw impressions
- participant-level variation and contradictions are visible, not flattened into one voice
- quotes are traceable back to a specific participant and moment
- any companion quantitative figure has a known source

If those conditions are not met, stop short of polished reporting and surface the blockers first.

### 2. Draft the report in markdown first

Read [references/interview-interim-patterns.md](references/interview-interim-patterns.md) for the full section skeleton. Use it unless the project already has a stronger house structure.
Build a markdown draft with, in order: Executive Summary, research overview, topic-grouped insight sections, an improvement-direction section, and an appendix.

### 3. Group insights by topic, not by theme-discovery order

Cluster findings into topic areas that match how the study was actually structured — screen or flow areas for a usability study (as in the native example: 홈 화면, 상품 탐색·가입, 자산관리, ...), or concept areas for a more open-ended study (e.g. trust conditions, information design, segment differences). Within each topic area, write one claim-sentence heading per distinct finding (a complete assertion, e.g. "홈이 '대표 계좌 확인 화면'에 머물러 주사용 기능의 시작점이 되지 못함" — not a topic label like "홈 화면 문제").
Under each claim heading, write 2-4 synthesis paragraphs: what was observed, where it split by segment or contradicted, and the implied direction — before any quotes.

### 4. Cite representative quotes in the report citation format

This report uses a different citation format than `$interview-results-dashboard`. For each representative quote:
```
▍ [screen or context label] (situational clause describing what the participant was doing or reacting to) "quote text"
— PID  gender, age band · short segment/persona descriptor
```
Do not substitute the dashboard's traceability-tag format (question number + source + demographics on one line) — that format serves lookup, this one serves readability in a submitted document. Keep 2-3 representative quotes per claim, not every quote that touched the topic.

### 5. Write the improvement-direction section without quotes

After the insight sections, add a claim-sentence-headed improvement-direction section (no Heading-2 topic grouping needed here — flat claim headings are the native pattern). Each item states a concrete direction in 1-2 paragraphs, grounded in the insight sections above. Do not introduce new findings here that weren't already established in the insight sections.

### 6. Build the appendix

Include what the project actually has — do not fabricate placeholder appendix sections. Common native components: interview question guide, participant screening survey responses, the codebook, and companion survey results when the study is mixed-method. Label each appendix item plainly (부록 A/B/C/...).

### 7. Handle updates as append, not overwrite

Native interim reports commonly accumulate multiple versions in one file across rounds (the same pattern documented for `$survey-interim-report-writer`). When an existing interview interim document is present:
- append the new version block instead of replacing the previous one
- mark the appended block as the latest version
- match the file's existing versioning convention when one is visible

Only replace instead of append if the user explicitly asks for a clean-replacement workflow.

### 8. Generate the docx

Draft in markdown first, then generate docx — the docx is the deliverable, not the markdown draft. Use plain built-in Word styles only (`Heading 1`/`Heading 2`/`Heading 3`/`Heading 4` for section levels, `Normal` for body text, `Table Grid` for tables). Native's real interview interim report carries no custom branding — do not invent color schemes or custom fonts. Use `python-docx` for generation.

### 9. Hand off with caveats

Return:
- which topics/claims came from strong, well-supported evidence versus thinner support
- any segment splits or contradictions that were preserved rather than smoothed over
- whether this is a fresh draft or an appended update, and what version marker was used
- what the appendix does and doesn't cover

Point to `$interview-results-dashboard` when the user's actual need is a lighter circulation surface rather than the formal report body.
Point to `$report-type-splitter` when the user is deciding among report families rather than drafting an interview interim specifically.

## Guardrails

- Do not write a formal interim report from raw transcripts or unresolved coding.
- Do not flatten participant-level contradictions or segment splits into one smoothed voice.
- Do not use the dashboard's citation/traceability-tag format here — use the report citation format in Workflow §4.
- Do not skip the improvement-direction section — native evidence treats it as a required closing section, not optional.
- Do not fabricate appendix sections the project doesn't actually have.
- Do not overwrite an existing interim document by default — append and mark the latest version.
- Do not treat a markdown draft as the finished deliverable — generate the docx using plain built-in Word styles, no custom branding.
- Do not guess the source material's location when it's unknown — ask the user rather than searching speculatively or drafting from assumption.

## Expected use cases

Use this skill for prompts such as:
- turn these interview coding files into a formal interview interim report
- update our existing interview interim document with this round's findings
- write the interview interim report body — not a dashboard, the actual document
- draft the improvement-direction section from these coded insights
