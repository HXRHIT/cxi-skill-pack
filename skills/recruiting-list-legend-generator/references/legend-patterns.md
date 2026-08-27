# Legend patterns for recruiting-list-legend-generator

## 1. Observed stage-packaging rule

Recruiting artifacts often separate stages explicitly.
Observed patterns include:
- separate round-level files plus raw or final variants
- multi-sheet workbooks where source pool, selected participants, and follow-up recruiting live on different tabs
- single-sheet screener handoff files for external recruiting vendors

Default rule:
- keep stage separation explicit
- if multiple stages coexist, separate them by sheet or file when possible
- use a single status column only when the source workflow already depends on that structure

## 2. Guide-sheet content rule

A practical guide sheet should explain:
- file purpose
- current stage
- owner or updater
- major tabs and when to use them
- key columns and meanings
- status values or stage-specific transitions
- PID legend
- linkage to transcript, coding, or survey artifacts when relevant

## 3. PID rule

- use simple sequential PID values such as `P001`
- keep segment, round, cohort, or session grouping as separate columns or lookup fields
- align with `pid_map.csv` when present
- avoid opaque combined ids when a simpler PID plus metadata columns can do the job

## 4. Common column patterns

Common roster fields include:
- PID or user id
- age or age band
- gender
- session group or cohort
- availability or participation status
- interview status or scheduling status
- notes or follow-up comments

Common screener-handoff fields include:
- category or classification
- content or request detail
- note or exception field
- vendor-facing instructions

Selected-participant sheets often pull forward approved cases from a broader source pool with formulas or lookups.

## 5. Stage-specific structure rule

When a workbook contains multiple stages:
- keep source pool data distinct from selected-participant lists
- keep follow-up or post-study recruiting distinct from the initial pool
- document how rows move from one stage to the next

When a workbook contains only one stage:
- keep one primary data sheet
- add one guide sheet plus optional summary sheet

## 6. Boundary rule

- use this skill for usage sheets, PID legends, and stage explanations
- use `$transcript-anonymizer-skill` for replacing names or masking PII
- use discovery or template-hygiene work for broader catalog or governance problems
- use recruiting operations tools or human workflows for actual outreach and scheduling