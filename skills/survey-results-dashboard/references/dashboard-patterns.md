# Dashboard patterns for survey-results-dashboard

## 1. Default output split

Use a dual-output model by default:
- researcher workbench
- stakeholder report

If the user wants only one, state which side was omitted.
Do not assume the same screen density works for both audiences.

## 2. Researcher workbench modules

A practical workbench usually includes:
- `study_overview`
- `sample_profile`
- `question_navigator`
- `question_detail`
- `segment_compare`
- `qa_flags`
- optional `rq_rh_tracker`

This view keeps denominator visibility, QA notes, and drill-down paths available.

## 3. Stakeholder report modules

A practical report view usually includes:
- headline summary
- study overview
- respondent profile snapshot
- key insight cards
- question-by-question result blocks
- optional appendix or method note

Keep this layer lighter than the workbench.
Use interpretation only where the evidence has already been reviewed.

## 4. Question block rule

Each repeated question block should usually include:
- question ID or short label
- question text or display title
- base_n
- main metric view
- segment cross-tab or comparison view
- highlight note
- low-base or significance caveat

Keep the claim, the supporting chart or table, and the caveat in one visible region.

## 5. AI insight three-layer rule

When using generated narrative, label the layers explicitly:
- `[Data]` for numbers and direct descriptive statements
- `[AI Interpretation]` for tentative pattern reading
- `[Needs Judgment]` for claims that require human review or business context

If the dashboard omits these labels, do not inject model-written narrative.

## 6. Low-base and significance rule

Use a low-base warning when a segment or subgroup falls below the accepted floor.
In the observed internal pattern, `base_n < 30` is a hard caution line.

Do not say a segment is meaningfully higher or lower unless an actual comparison rule or statistical test supports that statement.

## 7. Renderer selection rule

Prefer an interactive app such as Streamlit when:
- the dashboard is for researchers
- repeated filtering matters
- the user will inspect many question or segment cuts

Prefer static HTML or document-style views when:
- the audience mainly needs a readout
- the interaction model is shallow
- sharing simplicity matters more than exploration

Keep the information architecture stable across both renderers.

## 8. Brand token reminder

When the project expects Hana brand styling, reuse the observed palette consistently.
Known examples include:
- `#003087` for navy
- `#E8003D` for red

Treat brand tokens as presentation polish, not as the main logic of the dashboard.

## 9. Boundary with nearby skills

Use `$survey-basic-stats-analysis` first when the task is still about computing stats.
Use `$survey-analysis-verification` when the question is whether reported findings are correct.
Use `$report-type-splitter` when the user is really asking for an interim or final report artifact rather than a dashboard surface.
Use `$survey-open-ended-coding-skill` when the missing layer is open-ended coding rather than visualization.