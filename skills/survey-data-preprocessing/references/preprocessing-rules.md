# Preprocessing rules for survey-data-preprocessing

## 1. Default output bundle

Produce these artifacts together:
- cleaned dataset
- codebook or variable ledger
- short review notes or drift notes

Do not treat the cleaned dataset as complete if the codebook still needs review.

## 2. Question type system

Use a compact type system based on the team patterns:
- meta
- single
- scale7
- multi_binary
- multi_rank
- open

Classify each question or derived variable into one of these types before documenting transformations.

## 3. Variable ledger schema

Use this default schema for the companion codebook or ledger:
- variable_name
- question_id
- question_type
- scale
- missing_handling
- outlier_flag
- normality_flag
- derived_variable
- source_columns
- description
- preprocessing_decision
- needs_review

Add extra columns only when the project needs them.
Keep the base fields stable across runs.

## 4. Missing-value rule

The default team convention is blank cell equals no response or not applicable.
Only introduce coded missing values when a downstream analysis environment requires them.
If you recode missing values, document:
- original state
- new code
- reason for recoding

## 5. Wide-format rule

Treat wide-format exports as normal rather than malformed.
Common patterns include:
- one column for single-choice
- one column per option for multi-select
- one column per rank slot for ranking

Validate group completeness before transforming them.
Prefer preserving the original analytic shape unless a later step explicitly needs long format.

## 6. Schema drift checks

When multiple exports or waves exist, compare:
- column count
- missing or added questions
- renamed columns
- changed answer-slot counts

If drift exists, summarize it before merging files.
Do not hide drift inside a silent cleanup step.

## 7. Duplicate path merge rule

If the same logical question appears in split collection paths such as PathA and PathB:
- confirm they represent the same concept
- merge them at the respondent level using the most complete valid value
- document the merge rule in preprocessing_decision
- flag the variable for review if the merge required judgment

## 8. Review gate rule

Carry a `needs_review` field or equivalent review marker in the codebook.
Use it to distinguish:
- draft metadata that still needs human inspection
- reviewed metadata that can unlock downstream analysis

If any high-impact variable still needs review, keep the whole output in draft status.

## 9. PID join rule

When prescreener data and main research responses must be joined:
- preserve a stable PID as the primary key
- record the exact join key used
- report unmatched or duplicate IDs
- avoid joining on soft profile fields when a stronger PID should exist