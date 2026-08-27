# Workbook patterns for survey-open-ended-coding-skill

## 1. Default workbook output

Use a workbook-first output model.
Default artifact:
- `open_ended_coding_workbook.xlsx`

Minimal default sheet set:
- `coding_overview`
- `responses_coded`
- `codebook`
- `question_code_summary`
- `representative_quotes`
- `outliers_review`

If the project has several open-ended questions, keep this sheet logic stable and add a question field rather than inventing a new sheet taxonomy unless the volume makes one combined coded sheet unusable.

## 2. Response-level core columns

Keep these seven core columns in the coded response sheet:
- `row_id`
- `question`
- `respondent_id`
- `segment`
- `response_text`
- `codes`
- `coder_note`

If one of these fields does not exist in the source, keep the column and leave it blank rather than silently dropping the slot.

## 3. Codebook rule

When drafting a codebook:
- start with roughly 8 to 15 codes
- define each code in one line
- keep labels concrete and non-overlapping
- add an optional parent theme only when it helps roll-up

A practical codebook sheet usually includes:
- `code`
- `definition`
- `include_when`
- `exclude_when`
- `parent_theme`
- `count`

If the codebook is AI-suggested rather than team-approved, mark it as draft in the overview sheet.

## 4. Coding rule

Apply 1 to 3 codes per response by default.
Store multiple codes in a stable delimiter pattern such as comma-separated values.

Use `coder_note` for:
- ambiguity
- edge-case interpretation
- reason for leaving a response uncoded
- reminder for human review

Do not split one short response into multiple artificial records just to make coding easier.

## 5. Summary pattern

The summary sheet should show, at minimum:
- `question`
- `code`
- `count`
- `percent`
- `rank`
- `insight_note`

If segment cuts are included, keep them in additional columns or a clearly labeled companion region.
Do not blur per-response counts with per-respondent percentages when the source structure makes those different.

## 6. Representative quote rule

For each code, keep up to two quotes that clearly express the theme.
A practical quote sheet usually includes:
- `question`
- `code`
- `quote`
- `respondent_id`
- `selection_reason`

Prefer quotes that are vivid, specific, and easy to reuse in a synthesis document.

## 7. Outlier and review rule

Use the outlier or review sheet for:
- surprising answers
- uncoded responses
- contradictory responses
- extremely low-frequency but potentially high-signal themes

A practical sheet usually includes:
- `row_id`
- `question`
- `response_text`
- `issue_type`
- `review_note`

## 8. Boundary with related skills

Use `$survey-basic-stats-analysis` instead when the task is mainly numeric summary or Likert analysis.
Use `$survey-analysis-verification` when the question is whether a completed survey readout is correct.
Use `$qual-thematic-coding-skill` when the task needs interview-style thematic synthesis, affinity clustering, or cross-interview storytelling rather than workbook-first survey coding.
