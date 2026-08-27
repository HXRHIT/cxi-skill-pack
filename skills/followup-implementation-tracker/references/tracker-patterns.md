# Tracker patterns for followup-implementation-tracker

## 1. Scope split rule

Observed follow-up artifacts separate into three types:
- outbound design feedback
- implementation review
- project evaluation

Default skill scope includes the first two as one feedback-to-review cycle.
Default skill scope excludes project evaluation, which belongs with report-generation work rather than implementation tracking.

Also exclude `action-checklist` and `followup-meeting` from the default artifact bundle unless the user explicitly wants to introduce a new convention, because the team has no current precedent for them.

## 2. Default artifact bundle

A practical default bundle is:
- `followup_tracking_workbook.xlsx`
- `implementation_review_summary.md`
- optional `design_feedback_memo.md` when the task includes the outbound round

When the workbook is built by mining reports, it is the reviewer's worksheet before it is an archive. Its job is to put everything needed to judge an item on the same row, so the researcher can fill in a verdict without reopening the source report.

Keep the workbook as the evidence layer.
Use the summary artifact as the human-readable decision layer.

## 3. Proposal ID rule

Use a stable proposal identifier for every follow-up item.
Prefer IDs inherited from upstream action or recommendation artifacts.
If none exist, create a simple stable ID pattern such as:
- `FUP-001`
- `FUP-002`

Each tracked row should be able to carry:
- `proposal_id`
- `category`
- `proposal_text`
- `screen_or_pattern_ref`
- `source_finding_ref`

Rounds join on `proposal_id` and never on `proposal_text`. In the observed workbook all 26 proposal strings happened to match across two rounds, so a text join worked by luck. Wording gets lightly edited between rounds, and one edited character silently drops a row out of its own history.

## 4. Outbound feedback memo pattern

Observed outbound feedback follows a three-level structure:
- category axis
- issue statement
- screen or pattern anchor plus rationale

Useful writing rules:
- make the issue title self-contained
- keep the recommendation actionable
- point to a specific screen or pattern when possible
- preserve the proposal ID so the same item can be reviewed later

## 5. Implementation review workbook pattern

Use a fixed status vocabulary sheet and a review-round sheet structure.
A practical workbook includes:
- `status_codes`
- `review_YYYYMMDD`
- optional earlier review-round sheets

A practical review sheet contains, in order:

| # | Column | Filled by | Note |
|---|---|---|---|
| 1 | `proposal_id` | skill | join key |
| 2 | `category` | skill | promoted from report structure |
| 3 | `ux_proposal` | skill | |
| 4 | `source_document` | skill | which report it came from |
| 5 | `source_locator` | skill | page, section, or heading |
| 6 | `source_excerpt` | skill | verbatim sentence from the report |
| 7 | `evidence_type` | skill | survey / interview / heuristic / desk |
| 8 | `검토 포인트` | skill | what to look at in order to judge this |
| 9 | `확인 방법` | skill | app screen / plan doc / UX spec / needs live data |
| 10 | `반영 여부` | **researcher** | the four fixed values, data-validated |
| 11 | `반영사항` | researcher or drafted | |
| 12 | `확인 불가 사유` | researcher | required when the value is `Unclear` |
| 13 | `{round}_판정` | skill | prior round verdict, one column per prior round |
| 14 | `{round}_비고` | skill | prior round note, kept separate from the verdict |
| 15 | `판정자` | skill or researcher | |
| 16 | `판정일` | skill or researcher | |
| 17 | `판정 출처` | skill | `사람직접` or `AI초안-사람확정` |

Columns 4 to 7 are what make the tracker traceable upstream; the team's own workbooks had no equivalent. Columns 8 and 9 are what make it a review worksheet rather than a list.

Ship two companion sheets: `분류` for the four code definitions, and a source sheet listing the input reports with page counts and extraction date.

Separate the code definitions from the review data.
Do not mix freeform notes into the status code table.
Never merge columns 13 and 14 into one history column.

## 6. Fixed status vocabulary

Researcher decision, 2026-08-27. Use these four values verbatim in the delivered workbook:
- `반영완료` — reflected, with sufficient evidence
- `부분반영` — some but not all of the proposal is reflected, or it was accepted in a different form
- `미반영` — enough evidence exists to judge that it was not reflected
- `Unclear` — available artifacts do not allow a confident judgment

`Unclear` stays in Latin script by decision, matching the team's own code sheet, so no label mapping is needed between rounds. English snake_case may be used as an internal identifier in code but must never appear in the delivered file.

`Unclear` is closer to a pending state than to a verdict. In the observed rounds it held 18 of 26 items in round one, and 15 of those resolved in round two: 12 to `반영완료`, 2 to `부분반영`, 1 to `미반영`. Treat leftover `Unclear` items as the next round's first queue.

`미반영` is rare and consequential: it appeared once in 26 items. Prefer `Unclear` whenever the evidence does not settle the question.

## 7. History preservation rule

Observed team practice preserves earlier judgments instead of overwriting them, but the observed implementation failed at it.

The later round carried a single history column. It copied the prior round's note for all 26 rows and carried across **zero** prior verdicts, so every earlier judgment was lost while the column still looked populated. The prior round also used a different vocabulary, which is the failure usually blamed, but fixing the vocabulary alone would not have saved a single verdict.

The layout is therefore fixed, not open:
- `{round}_판정` carries the prior verdict
- `{round}_비고` carries the prior note
- both columns are required, one pair per prior round
- separate review-round sheets may be kept as well, but they do not substitute for the paired columns

Time-series judgment must remain visible as data, not as prose in a note field.

## 8. Summary report pattern

A practical companion summary usually follows this order:
- review background
- overall result
- major reflected items grouped by category
- unimplemented or still-unconfirmed items
- conclusion
- optional attached detail table

Keep the summary aligned with workbook categories so the reader can trace major claims back to the tracker.

## 9. Evidence and limitation rule

When artifacts are incomplete, say so directly.
Common limitation patterns include:
- feature requires live data or an environment not available for review
- updated artifact shows intent but not actual implemented behavior
- supporting material is too partial to confirm the proposal outcome

Use these situations to justify `unclear`, not to guess.

## 10. Report extraction pattern

Reports are a first-class input. The skill reads them and produces the proposal rows itself.

Procedure:
1. Accept every report supplied: final report, survey report, interview report, insight report, executive summary.
2. Chunk by page or section and extract statements that read as improvement proposals or improvement directions.
3. For each proposal, record the source document, the locator, and a verbatim excerpt. Anchor at sentence or section level.
4. Deduplicate proposals that appear in more than one report, keeping every source anchor rather than dropping to one.
5. Group into categories using the reports' own structure before inventing a scheme.

Feasibility check, 2026-08-27: 26 proposals from one team's follow-up workbook were matched back against that project's three reports, 117 pages total. Plain token overlap at page granularity anchored 21 of 26 above 0.5, with 3 exact matches, and every remaining item anchored above 0.33. The proposals had been lifted almost verbatim from report sentences. Two observations follow:
- an LLM reading the same reports can anchor at sentence level rather than page level
- **proposals spanned two different reports**, 18 from the interview report and 8 from the survey report, so never assume a single source document

Do not manufacture proposals the reports do not state. An unwritten but implied improvement is a gap to report in the handoff, not a row to add.

## 11. Judgment authority

Who fills the status column depends on evidence, not on confidence.

| Situation | Who judges | Recorded as |
|---|---|---|
| No evidence supplied | researcher | status left empty; `검토 포인트` and `확인 방법` filled by the skill |
| Screen captures, UX specs, design docs, or release notes supplied | skill drafts, researcher confirms | `판정 출처` = `AI초안-사람확정`, plus the file and location used |
| Evidence supplied but inconclusive | skill | `Unclear` with `확인 불가 사유` |

Hard limits:
- a drafted judgment never assigns `미반영`
- judgments read from screen captures must state which screen elements were actually read, and anything unread goes to `Unclear`
- a drafted judgment is never written into the same field as a confirmed one without `판정 출처` distinguishing them

The team's own multimodal comparison selected a model on whether it read app screenshots correctly, recording that one model missed images and another disclosed misses only when asked directly. Screenshot reading is the weakest link in the chain, so it declares its limits rather than smoothing them over.

## 12. Boundary with nearby skills

Use `$action-matrix-generator-skill` when the user is still prioritizing what to do.
Use this skill when the proposals already exist and the task is to send or review follow-up.
Use `$report-type-splitter` when the deliverable is really an interim or organization-facing report.
Use `$template-hygiene-checker` when the follow-up artifacts expose placeholder leakage or sensitive-author-name cleanup issues.