---
name: qual-thematic-coding-skill
description: "Analyze interview transcripts through qualitative thematic coding by extracting core themes, pain points, workarounds, emotional moments, and surprises; structuring them into the team Context-Content-Group schema; then synthesizing patterns across interviews and clustering them into affinity groups. Use when Codex needs to turn one or more interview transcripts into thematic coding files, cross-interview synthesis, or an affinity mapping report before dashboarding or executive reporting."
---

# Qual Thematic Coding Skill

## Overview

Use this skill for qualitative interview analysis, not fixed-tag quantitative coding.
Keep the main workflow in this file.
Read [references/coding-patterns.md](references/coding-patterns.md) when you need the five-category lens, the team schema, cross-interview confidence rules, or the default file outputs.

If the user needs true or false tag matrices, ranking counts, or scoring, route that work to `$interview-quant-coding-skill` instead of forcing it into this workflow.

## Inputs

Gather these inputs when available:
- one or more interview transcripts
- research topic or study goal
- participant context or segment notes
- optional interview question guide
- optional project hypotheses or focus themes

If transcript quality is poor, recommend transcript cleanup before deep coding.
If identifying details remain, recommend anonymization before sharing outputs widely.

## Workflow

### 1. Code each interview individually

Read [references/coding-patterns.md](references/coding-patterns.md).
For each participant transcript, extract evidence through the five-category lens.
Use the team schema:
- Context for direct quote or grounded excerpt
- Content for interpreted meaning
- Group for the higher-order theme label

Produce one participant-level coding file per transcript.
Do not jump straight to cross-interview synthesis before preserving the individual evidence.

### 2. Preserve the five-category lens

At minimum look for:
- key themes
- pain points
- workarounds
- emotional moments
- surprises

Do not let the more obvious categories crowd out workarounds or surprising findings.
Those are often the highest-value discovery signals.

### 3. Synthesize across interviews

Merge the participant-level outputs and look for cross-interview structure.
Use the confidence-oriented synthesis rules from [references/coding-patterns.md](references/coding-patterns.md).
Every synthesized pattern should stay tied to relevant participant language, not just analyst paraphrase.
Surface:
- consistent patterns
- contradictions
- spectrum findings
- outlier insights
- confidence assessment

Order the synthesis by confidence, not just by raw mention count.

If the project has a formal RQ (research question) list (e.g. an `rq-list` file under `02_establish__*`), cross-check the finished synthesis against it once coding is done — this workflow is intentionally bottom-up (evidence first, not RQ-down), so RQ coverage should be verified as a closing step, not assumed. Note explicitly which RQs are fully covered, partially covered, or a genuine gap that no amount of re-reading the same transcripts can close (e.g. a comparison the recruiting design never captured). Do not quietly skip this check just because the bottom-up synthesis already "feels" complete.
For each pattern, include one or more directly relevant user quotes alongside the interpretation.
Those quotes should be verbatim from the source evidence whenever possible.
Do not replace user language with cleaned paraphrase, summary wording, or ellipsis-shortened fragments unless the source itself is truncated.
Prefix each quote with the question number, question source, and participant metadata.
At minimum include:
- question number from the interview guide or protocol when identifiable
- which interview question or protocol section the quote came from
- PID
- age band and gender
- any researcher-requested segment traits such as involvement level

### 4. Run affinity clustering

Group quotes, observations, and interpreted insights into natural clusters.
Aim for a manageable set of clusters rather than a flat list.
Rank them by both volume and significance.
Also identify outliers and note relationships between clusters when the sequence or causality matters.

### 5. Hand off the evidence pack

Return the default markdown evidence set:
- participant-level thematic coding files
- one cross-interview synthesis file
- one affinity mapping report

If the user explicitly needs spreadsheet packaging, treat that as an optional export layer rather than the core output.

## Guardrails

- Do not collapse qualitative coding into a binary tag matrix inside this skill.
- Do not paraphrase every quote into generic summaries; preserve grounded evidence.
- Do not treat frequency alone as confidence.
- Do not skip contradictory or outlier findings because they are inconvenient.
- Do not mix affinity clustering with formal scoring rules that belong in `$interview-quant-coding-skill`.

## Expected use cases

Use this skill for prompts such as:
- analyze these interview transcripts for major themes and pain points
- make participant-by-participant qualitative coding files and a cross-interview synthesis
- cluster these interview findings into affinity groups
- turn this transcript set into evidence-backed qualitative insights
