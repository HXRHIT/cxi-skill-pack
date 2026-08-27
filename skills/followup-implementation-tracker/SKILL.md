---
name: followup-implementation-tracker
description: "Track research follow-up and implementation review cycles: read final, survey, and interview reports to extract improvement proposals with source anchors, build a fixed-status review workbook the researcher fills in, and produce companion review summaries. Use when Codex needs to manage post-research follow-up on design or product changes, especially to build a review checklist from reports, send proposal feedback, review whether recommendations were implemented, or summarize what changed after research."
---

# Followup Implementation Tracker

## Overview

Use this skill to manage the post-research follow-up cycle between sending improvement proposals and reviewing whether they were actually implemented.
Keep the core workflow in this file.
Read [references/tracker-patterns.md](references/tracker-patterns.md) when you need the default artifact bundle, proposal-ID rule, outbound memo pattern, implementation-review workbook pattern, or summary-report structure.

This skill runs standalone from reports. Prefer upstream inputs from `$action-matrix-generator-skill` when proposal IDs or priorities already exist, but never require them.
If the requested artifact is really an organization-facing project evaluation deck rather than an implementation follow-up cycle, route that work to `$report-type-splitter` instead.

## Inputs

Primary input:
- research reports to mine for proposals: final report, survey report, interview report, insight report, executive summary

Gather these inputs when available:
- proposal list or action matrix, as an alternative source rather than a prerequisite
- updated design screens, specs, release notes, or product changes to review
- optional prior review-round workbook
- optional category scheme already used by the team
- optional evidence links back to research findings, screens, or source artifacts
- optional deadlines or review-round dates

If the source material only shows that ideas were discussed, but not whether they were implemented, keep the output in review status rather than claiming resolution.

## Workflow

### 1. Decide which point in the cycle the task is in

Classify the request before producing artifacts:
- outbound feedback round
- implementation review round
- end-to-end follow-up cycle across both

Use the scope rule in [references/tracker-patterns.md](references/tracker-patterns.md).
Default scope includes:
- sending structured feedback on updated designs
- reviewing whether prior proposals were implemented

Default scope excludes:
- organization-facing project evaluation decks
- zero-precedent artifacts such as `action-checklist` or `followup-meeting` unless the user explicitly wants to introduce a new convention

### 2. Extract proposals from the reports

When no proposal list is supplied, mine the reports directly. Use the extraction pattern in [references/tracker-patterns.md](references/tracker-patterns.md).

- Read every supplied report. Proposals routinely span more than one report, so never assume a single source document.
- For each proposal capture `source_document`, `source_locator`, and a verbatim `source_excerpt`. Anchor at sentence or section level, not whole-document level.
- Do not invent proposals the reports do not state. If something is implied but unwritten, leave it out and say so in the handoff.
- Carry the report type into `evidence_type` so the reviewer knows whether the proposal came from survey, interview, heuristic, or desk research.

These source columns are the point of this step. Team follow-up workbooks historically carried no field linking a proposal back to the finding that produced it, which left the tracker untraceable upstream.

### 3. Register or normalize proposal IDs

Read [references/tracker-patterns.md](references/tracker-patterns.md).
If the proposals already have stable IDs, keep them.
If not, assign stable IDs before drafting or reviewing anything.

Keep each proposal traceable through:
- proposal ID
- category
- proposal text
- optional screen or pattern reference
- optional source-finding reference

Do not let the follow-up cycle depend on plain-language proposal text alone.
Never join review rounds on proposal text. Rounds join on `proposal_id` only, because proposal wording gets lightly edited between rounds and a one-character change silently breaks the history.

### 4. Build the outbound feedback artifact when the task is pre-implementation

When the task is to send feedback on updated designs:
- group feedback using the observed three-level hierarchy
- keep issue titles actionable and self-contained
- anchor comments to screen or pattern identifiers when possible
- preserve the link to the originating proposal ID

Use this stage to make later implementation review possible.
A feedback memo without stable proposal anchors creates avoidable ambiguity downstream.

### 5. Build the implementation review workbook when the task is post-implementation

Use the workbook pattern in [references/tracker-patterns.md](references/tracker-patterns.md).

The status vocabulary is fixed to exactly these four values, written into the workbook verbatim:
- `반영완료`
- `부분반영`
- `미반영`
- `Unclear`

`Unclear` stays in Latin script. That is the team's own notation and it is preserved deliberately, so rounds need no label mapping. English snake_case may serve as an internal identifier in code but must never reach the delivered file. Ship the `분류` code-definition sheet next to the review sheet and enforce the four values with data validation.

Keep `Unclear` separate from `미반영`. In the observed team round 18 of 26 items were `Unclear`, and 12 of those later resolved to `반영완료`. Collapsing the two would have manufactured a "not implemented, then implemented" story that never happened.

Do not overwrite prior round judgments. Carry history forward as **two separate columns per prior round**:
- `{round}_판정` for the prior verdict
- `{round}_비고` for the prior note

Both are required. A single merged history column is what actually broke time-series comparison in the observed case: the later round copied all 26 prior notes but carried across zero prior verdicts, so the earlier judgments were lost while the column still looked populated.

The workbook is what the researcher fills in. Leave `반영 여부` empty unless the judgment rule in step 7 permits a drafted verdict.

### 6. Generate the companion summary report

After the workbook is updated, produce a concise summary that explains:
- what was reflected
- what remains unimplemented
- what still needs confirmation
- what constraints limited judgment

Use category groupings from the workbook when they are stable enough.
Treat the workbook as the traceable evidence layer and the summary as the readable decision layer.

### 7. Apply the judgment-authority rule

Who fills in `반영 여부` depends on whether the reviewer supplied evidence to judge against.

- **No evidence supplied**: do not draft a verdict. Leave `반영 여부` empty for the researcher, and fill `검토 포인트` and `확인 방법` so they know what to look at.
- **Evidence supplied**, such as screen captures, UX specs, design documents, or release notes: draft a verdict, set `판정 출처` to `AI초안-사람확정`, and cite the file and location used. The researcher confirms it.
- **Never assign `미반영` on your own.** It carries organizational weight and appeared once in 26 observed items. When evidence does not settle the question the answer is `Unclear`.
- **When judging from screen captures, state which screen elements you actually read.** Multimodal reading of app screenshots proved unreliable enough that the team used it as their model-selection criterion. Anything you could not read goes to `Unclear` rather than to a guess.

When the available artifact is a plan, mockup, or partial release note:
- mark uncertain items as `Unclear`
- fill `확인 불가 사유` with what specifically blocked the judgment
- say what evidence would resolve them
- avoid promoting intent into confirmed implementation

The skill is most useful when it preserves the difference between "not done" and "cannot verify yet."

Open each new round by queueing the prior round's `Unclear` items first, and flag anything `Unclear` for two consecutive rounds.

### 8. Hand off with next-step guidance

Return:
- which cycle stage was handled
- the updated workbook or tracker structure
- the summary of reflected and unresolved items
- any missing links back to proposal IDs or research evidence
- the recommended next step for another review round, report writing, or artifact cleanup

Point downstream to `$template-hygiene-checker` when the follow-up materials expose placeholder leakage or sensitive-name cleanup issues.

## Guardrails

- Do not treat project-evaluation decks as if they were implementation trackers.
- Do not collapse `Unclear` into `미반영`.
- Do not translate, abbreviate, or extend the four fixed status values.
- Do not merge a prior round's verdict and note into one history column.
- Do not join review rounds on proposal text instead of `proposal_id`.
- Do not fill in `반영 여부` when no evidence was supplied to judge against.
- Do not assign `미반영` from a drafted judgment.
- Do not overwrite prior round judgments without preserving history.
- Do not issue follow-up claims that cannot be traced to a proposal ID or concrete artifact.
- Do not assume a design intention note proves implementation.
- Do not invent `action-checklist` or `followup-meeting` artifacts by default when the team has no precedent yet.

## Expected use cases

Use this skill for prompts such as:
- read these reports and build a review checklist of improvement proposals
- track whether these UX recommendations were implemented
- build a follow-up workbook from this proposal list and updated design
- create an outbound feedback memo and later implementation review structure
- here are the updated screens and the UX spec, check these proposals against them
- summarize what changed after this research round and what still needs action