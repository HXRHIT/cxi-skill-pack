# Report patterns for survey-interim-report-writer

## 1. Default section order

Use this section order unless the user gives a stronger house template:
- `study_overview`
- `key_findings`
- `competitive_position`
- `satisfaction_recommendation_retention`
- `missing_features_or_pain_points`
- `driver_or_correlation_takeaways`
- `next_interview_plan`
- optional `appendix_note`

Keep the report as a survey-source document.
Do not fold interview or heuristic evidence into the main narrative unless the task has already become a final integrated report.

## 2. Headline rule

Write section headlines as complete claim sentences rather than noun fragments.
Prefer a structure like:
- target or topic
- observed evaluation or tension
- implication when it matters

If the title sounds like a dashboard label, strengthen it into a report claim.

## 3. Evidence block rule

For each major claim, keep these elements close together:
- the metric or observed result
- the base or denominator
- the comparison target when one exists
- the implication for the product or research follow-up

Do not leave a polished claim floating without its supporting base or comparison.

## 4. Table rule

Survey interim reports are table-heavy.
Prefer real data tables, ranked lists, and structured comparison tables over decorative quote or photo boxes.

If a section starts to behave like a dashboard card grid, pull it back toward report prose plus anchored tables.

## 5. Next interview bridge rule

Treat `next_interview_plan` as a required bridge when the survey findings naturally open unresolved questions.
Use this section to state:
- what the survey already clarified
- what still needs qualitative explanation
- which user groups or situations should be probed next

Do not invent a full interview guide here.
Frame it as the handoff from survey evidence to the next qualitative phase.

## 6. Append-latest rule

When an existing interim document is present:
- append the new version block instead of overwriting the previous one
- preserve prior versions for traceability
- mark the appended block as the latest version
- match any visible versioning convention already present in the file when possible

If no version convention exists, add a simple dated version marker and a latest-version note.

## 7. Output ladder rule

Use this output order by default:
1. improve the markdown draft until the logic and tone are stable
2. convert that draft into a docx draft
3. append it into the working interim document if update mode is in scope

Do not jump straight to docx while the structure is still weak.

## 8. Boundary with nearby skills

Use `$survey-basic-stats-analysis` when the missing work is still descriptive statistics.
Use `$survey-analysis-verification` when the key question is whether a finding is numerically correct.
Use `$survey-results-dashboard` when the user wants a lighter visualization or workbench surface.
Use `$report-type-splitter` when the task is actually about choosing among survey interim, interview interim, heuristic interim, and final integrated report families.
