---
name: executive-one-pager-skill
description: "Compress a report, analysis output, or project-related material into an executive-facing narrative in the team's preferred structure mode (timeline narrative, conclusion-first/Minto, or RQ-first), then render it as one-pager copy, an intro summary slide outline, or an executive-summary section draft. Most commonly this summarizes an already-written report, but it can also work directly from analysis content or project files when no full report exists yet or one isn't needed. Use when Codex needs to produce an executive one-pager or executive-summary section."
---

# Executive One-Pager Skill

## Overview

Use this skill to compress existing work into an executive-facing narrative, not to generate new findings.
Most often that existing work is an already-written report: team practice, confirmed directly by a researcher (2026-08-19), is that an executive summary is **typically written after the full report, as a compression of it**. Treat this as the common case, not a hard prerequisite — the same researcher also confirmed this skill needs to work directly from **analysis content or project-related files** when that's what's available, without requiring a polished report to exist first. Both paths are legitimate; note in the hand-off which one was used so the reader knows what the summary is grounded in.
Treat "one-pager" as a compression target, not a literal single-page requirement — team precedent renders this as a summary slide or a report's opening section just as often as a standalone single page.
Keep the core decision workflow in this file.
Read [references/one-pager-patterns.md](references/one-pager-patterns.md) when you need the three structure-mode skeletons, the native evidence behind them, or the boundary rules with nearby skills.

A stable or finished report draft from `$report-type-splitter`'s child skills is the most common source. Dashboard outputs (`$survey-results-dashboard`, `$interview-results-dashboard`), verified analysis (`$survey-analysis-verification`), or raw analysis/project files are equally valid sources when a full report isn't available or isn't what the task calls for — this is not a fallback to apologize for, just a different starting material.
Prefer `$action-matrix-generator-skill` output for the recommendation or next-action block when it exists.
If the source findings are still unverified or clearly unstable (not just "not yet formatted as a report"), route back upstream before compressing them into an executive narrative.

## Inputs

Gather these inputs when available:
- the material to summarize — most commonly an interim/final report draft (ideally from `$report-type-splitter`'s child skills), but analysis content, a dashboard output, or other project-related files are equally valid when a report doesn't exist yet or isn't needed
- prioritized recommendations or action items (ideally from `$action-matrix-generator-skill`)
- structure mode preference: timeline narrative, conclusion-first (Minto), or RQ-first
- audience and occasion (steering committee, kickoff readout, phase handoff, etc.)
- target output layer: one-pager copy, intro summary slide outline, or executive-summary section draft

If the user does not name a structure mode, default to timeline narrative — see [Workflow §2](#2-choose-the-structure-mode).
If the user does not name a target output layer, ask which one is needed rather than guessing, since the three layers differ in length and rendering.
If the source material itself isn't already in the conversation and its file location isn't known or is ambiguous, **ask the user to send or point to it** rather than guessing a plausible-looking path, searching speculatively across the project for something that might match, or proceeding from memory/assumption. This applies even if a similarly-named or similarly-scoped file was used in an earlier session — confirm it's the right one rather than assuming.

## Workflow

### 1. Confirm compression readiness

Locate the source material first. If it isn't already provided in the conversation and its location isn't known or is ambiguous, **stop and ask the user to send it or point to its location** — do not guess a file path, run a speculative broad search for something that might be the right file, or draft from memory/assumption of what the report probably says. A wrong or fabricated source is worse than a short delay to ask.

Once the source is confirmed, identify what kind of material is being compressed — a finished/stable report draft, a dashboard output, or analysis content/project files directly — and note it for the hand-off (§7). No single source type is required; match the workflow to whatever is actually available.

If the user's real need turns out to be the full report itself (not a compressed summary), point to `$report-type-splitter` instead of improvising report content here — but do not require a report to exist before this skill can run.

Check that the source material is stable enough to compress regardless of type:
- claims are traceable back to the source report, dashboard, analysis output, or project files
- numbers and dates are not being invented to fill narrative gaps
- recommendations, if included, come from an actual prioritization pass rather than being improvised here

If the source is still raw or unverified (contradictory coding, unresolved analysis, draft notes with unchecked claims), stop short of polishing an executive narrative and surface the gap first. This is a stability check, not a format check — analysis content that is internally consistent and evidenced is compressible even without ever becoming a formatted report.

### 2. Choose the structure mode

Default to **timeline narrative** (background → method progression → what was found at each step) unless the user asks for something else. This mirrors the team's actual precedent rather than a generic best practice.
Always mention that **conclusion-first (Minto)** and **RQ-first** are available alternatives, even when timeline narrative is used — do not silently pick one and hide the option.

Use the signals below to recommend a mode when the user is undecided:
- source material already reads as a step-by-step process (desk research → fieldwork → synthesis) → timeline narrative
- audience needs the answer before the method (steering committee with limited time) → conclusion-first
- source material is already organized by research question, or into named theme/finding clusters, or the study had 3-5 named RQs → RQ-first

If the user explicitly requests timeline narrative but the source is a single-round study with no real phase progression (one method pass, one synthesis step), still honor the request, but say so plainly in the hand-off (§7) rather than padding the timeline with thin or empty phases to make it look multi-step. Name which alternate mode would have fit the source better.

Read [references/one-pager-patterns.md](references/one-pager-patterns.md) for the section skeleton of each mode and the native evidence behind them.

### 3. Extract the compression material

From the source, pull out:
- the handful of headline claims (not every finding — the ones an executive audience needs)
- the minimum evidence each claim needs to stay credible (one stat, one quote, or one comparison — not the full backing table)
- the process steps or RQs the claims map to, matching the chosen structure mode
- next-action or recommendation items, sourced from `$action-matrix-generator-skill` output when available; otherwise state that recommendations were not independently re-prioritized here

Do not carry over the source's full argument chain — an executive narrative compresses, it does not summarize paragraph-by-paragraph.

### 4. Build the narrative in the chosen mode

Follow the matching skeleton in [references/one-pager-patterns.md](references/one-pager-patterns.md).
Use claim-sentence headings (a complete assertion, not a topic label) consistently with how the team already writes report headings elsewhere.
Keep section count tight enough to still function as a "compressed" artifact — if the draft is growing into a full report body, that is a signal to hand off to `$report-type-splitter` instead of continuing here.

### 5. Attach the recommendation or next-action block

Place this near the end regardless of structure mode.
If `$action-matrix-generator-skill` output exists, use its prioritized items directly instead of re-deriving priority here.
If no prioritized action list exists, either state that the recommendation block reflects only the source material's stated next steps, or ask whether to run `$action-matrix-generator-skill` first.

### 6. Render the target output layer

Draft in markdown first, then convert to the final deliverable — do not stop at markdown and call it done.

- **one-pager copy**: markdown draft → **docx is the required final deliverable** (this is a Word-first team; a markdown draft alone is not the finished artifact)
- **intro summary slide outline**: slide-by-slide breakdown (title, key visual/data point, one supporting line) as markdown, then a slide deck (pptx) when the environment can produce one; state clearly if only the markdown outline could be produced
- **executive-summary section draft**: markdown draft → **docx**, written to also slot into a larger interim/final report docx

When generating the docx, match native's actual convention rather than inventing custom branding: use plain built-in Word styles (`Heading 1`/`Heading 2`/`Heading 3` for section headings, `Normal` for body text, `Table Grid` for any tables, `List Bullet`/`List Number` for lists). Native's own artifacts (e.g. the PAYAI quick-summary docx) use these default theme styles with no custom fonts or brand colors — do not add color schemes or custom fonts that the team's real documents do not use. Use `python-docx` for generation, matching the pattern documented in [references/one-pager-patterns.md](references/one-pager-patterns.md) §5.

Keep the underlying content model (claims, evidence, structure mode) stable across renderers — the renderer is the last step, not a redesign.

### 7. Hand off with caveats

Return:
- what kind of material was compressed (finished report, dashboard output, or analysis/project files directly) so the reader knows what the summary is grounded in
- which structure mode was used and why
- which claims came with direct evidence versus which were compressed from a longer argument
- whether the recommendation block came from `$action-matrix-generator-skill` or from the source material's own next-steps language
- an explicit note that native precedent for this artifact type is still thin (two structurally different examples observed so far — see references) — do not present the chosen mode as a fixed team standard

Point to `$report-type-splitter` when the user's real need turns out to be the full report body itself (either because no summary-worthy material exists yet, or because the request has grown past a compressed layer) — not as a mandatory first step before this skill can run.

## Guardrails

- Do not treat "one-pager" as requiring exactly one physical page or one slide.
- Do not invent timeline steps, dates, or metrics that are not in the source material.
- Do not silently default to timeline narrative without naming conclusion-first and RQ-first as available options.
- Do not re-derive recommendation priority from scratch when `$action-matrix-generator-skill` output already exists.
- Do not expand this into a full report body — that boundary belongs to `$report-type-splitter`.
- Do not present the current structure-mode skeletons as a fixed, validated team standard; the native evidence base is still two examples showing two different modes, not a converged convention.
- Do not treat a markdown draft as the finished deliverable for the one-pager copy or executive-summary section layers — generate the docx.
- Do not invent custom fonts, brand colors, or styling that native's real documents do not use. Default to plain built-in Word styles unless the user supplies an actual team template to match.
- Do not require a finished report to exist before this skill can run — analysis content or project-related files are valid sources on their own. Do state clearly which kind of material was actually compressed.
- Do not guess the source report's location or search speculatively when it isn't known — ask the user to send it or point to it. Do not substitute a similarly-named file from a different or earlier session without confirming it's the intended source.

## Expected use cases

Use this skill for prompts such as:
- turn this finished interim report into an executive one-pager
- draft the executive-summary section for this completed final report
- summarize this report for a steering committee readout
- write an executive summary directly from this analysis output or these project files — no formatted report exists yet
