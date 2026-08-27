# Workbook patterns for interview-quant-coding-skill

## 1. Default workbook output

Use a workbook-first output model.
Default artifact:
- `coding-workbook.xlsx`

Common workbook pattern:
- one sheet per coded question or construct
- one insight or ranking sheet
- optional participant scoring sheet

## 2. Question-level matrix rule

For each target question:
- rows usually represent participants or response records
- columns represent fixed tags or attributes
- cell values use true or false, or 1 and 0 if the workflow requires numeric coding

Keep the coding rubric stable within one question.
Do not redefine tag meaning mid-workbook.

## 3. Tag-list rule

Use a fixed tag list when the project needs comparison across participants or variants.
Common sources:
- adjective lists
- predefined UX attributes
- approved coding rubric from the research team

If tags are AI-suggested, treat them as draft until reviewed.

## 4. Frequency and ranking pattern

After matrix coding, calculate:
- tag frequency
- rank order
- optional per-variant comparison

Include a short insight note near the ranking output.
The note should explain what the ranking suggests, not re-summarize every row.

## 5. Scoring pattern

When the project uses participant scoring:
- combine selected coded fields according to an explicit rule
- keep the component fields visible
- output the final score and derived label

Possible derived outputs include:
- interest score
- engagement type
- persona or behavior label

Do not invent scoring weights without a documented basis.

## 6. Boundary with qual-thematic-coding-skill

Use `$qual-thematic-coding-skill` instead when the task needs:
- open theme discovery
- workarounds and surprise capture
- cross-interview synthesis by confidence
- affinity clustering

Use this skill when the task needs:
- fixed tags
- question-by-question matrices
- frequency ranking
- rule-based scoring

## 7. Review and ambiguity rule

When evidence for a tag is weak or mixed:
- leave a review marker
- keep the raw quote or response reference available
- avoid confident binary coding without support

## 8. Minimal workbook sheet set

A practical default sheet set is:
- `Q##_matrix`
- `Q##_insight`
- `participant_scores` when scoring exists

If multiple questions are coded, repeat the matrix and insight pair per question.