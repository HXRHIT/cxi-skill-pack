# Analysis patterns for survey-basic-stats-analysis

## 1. Default output bundle

Produce these artifacts as the default bundle:
- analysis-readiness note or gate result
- question-level stats workbook or table set
- hypothesis tracker tied to the active RQ or RH set
- short analyst notes with caveats or blockers

If the user only wants a quick answer, summarize the same structure in markdown instead of pretending the workbook never existed.

## 2. Question-level sheet pattern

The team pattern is one question or question family per sheet or section.
Use stable columns so different question sheets are easy to compare.

Common base fields:
- answer option or response bucket
- count
- percentage
- respondent_based_percentage when needed
- response_based_percentage when needed
- segment columns when cross-tabs are included

## 3. Metric rules by question type

### single

Default metrics:
- count
- percentage

### multi_binary or multi-select

Default metrics:
- count
- response-based percentage
- respondent-based percentage

Keep both percentage definitions visible.
Do not collapse them into one unlabeled percentage.

### scale5

Default metrics:
- mean
- standard deviation
- top2
- bottom2

If helpful, also include mode or median, but keep the core four stable.

### scale7

If project metadata defines the metric, follow it.
Otherwise default to:
- mean
- standard deviation
- top2
- bottom2

Record the exact cut points used, for example `6+7` and `1+2`.
If a legacy workbook uses a different threshold, preserve that decision instead of silently normalizing it.

### open

Do only light structural handling here:
- non-empty response count
- missing response count

Route deeper text analysis to a separate open-ended coding workflow.

## 4. Hypothesis tracker schema

Use this default schema when the active RQ or RH context exists:
- RH_number
- RH
- analysis_idea
- analysis_method
- statistical_test_or_basis
- result_summary
- p_value
- decision
- insight
- report_include

If a field is not applicable, leave it clearly empty rather than inventing evidence.
If neither RQ nor RH context is available yet, block final stats generation and record the missing context instead of filling this table with placeholders.

## 5. Decision vocabulary

Use stable decision labels such as:
- supported
- rejected
- inconclusive
- descriptive_only

Prefer `descriptive_only` when no real test was run.
Do not force a binary supported or rejected label when the design does not justify it.

## 6. Segment comparison rule

Before comparing segments, confirm:
- the segment variable is trustworthy
- cell counts are not obviously too thin
- the question type matches the comparison method
- the segment cut still answers a real RQ or RH rather than becoming exploratory noise

When significance is tested, state the method and p-value.
When only descriptive comparison is available, say that explicitly.

## 7. Analysis metric override rule

If the dataset or companion metadata already declares an `Analysis_Metric` or equivalent field:
- follow the declared metric list
- use project-specific thresholds if they are documented
- document any places where the data prevented the requested analysis

## 8. What not to overbuild

Automatic survey tools already cover many charts and simple cross-tabs.
This skill adds the most value when it provides:
- a hard gate that prevents stats without question-map and RQ/RH context
- stable question-by-question stats outputs
- RH-level traceability
- consistent interpretation fields across questions
- analyst-ready text that can move into reporting
