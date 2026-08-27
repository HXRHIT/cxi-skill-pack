# Persona patterns for persona-generator-skill

## 1. Default workbook output

Use a workbook-first output model.
Default artifact:
- `persona_workbook.xlsx`

Default sheet set:
- `01. Userdoc`
- `02. Extended Profile`

If the project only supports the core sheet, omit the second sheet and say so explicitly.

## 2. Core sheet pattern: `01. Userdoc`

Observed backbone columns include:
- `Generated date`
- `#`
- `User Types`
- `Description`
- `Name`
- `Age`
- `Location`
- `Family status`
- `Work / Job Title`
- `About`
- `Goals`
- `Frustrations`

Treat this as the primary delivery format.

## 3. Extended sheet pattern: `02. Extended Profile`

Observed extensions include fields such as:
- `Scenario`
- `Group`
- `User Types_2`
- `Gender`
- `Income level`
- `Investment propensity`
- `Behavior / attitude / experience`
- `Investment strategy preference`
- `Risk tolerance level`
- `Decision-making process`

Only include fields the evidence can actually support.

## 4. Persona narrative rule

Use these writing patterns:
- `Description`: one-line segment summary
- `About`: compact background narrative, usually a few sentences
- `Goals`: three concise bullets when the evidence supports three
- `Frustrations`: three concrete blockers or pain points when the evidence supports three

Keep the wording specific to the domain and the observed product context.

## 5. Naming rule

Use fictional names only.
Do not reuse participant names, exact workplaces, or traceable personal details.

When bilingual labeling is useful:
- keep the Korean group label as the primary segment anchor
- keep the English alias as a compatible secondary label

## 6. Multi-row group rule

A single archetype can have more than one named row when the workbook format expects multiple exemplars inside one group.
If you do this, keep the shared group logic obvious and do not let the rows drift into unrelated concepts.

## 7. Evidence rule

A persona workbook should be generated from synthesized evidence, not from raw anecdotes alone.
Good supporting inputs include:
- thematic coding summaries
- survey segment findings
- mixed-method synthesis
- verified app-review themes

If the source only supports descriptive participant summaries, call them profiles or cases rather than stable personas.

## 8. Boundary with nearby skills

Use `$qual-thematic-coding-skill` or `$survey-open-ended-coding-skill` first when the evidence is still uncoded.
Use `$survey-results-dashboard` when the deliverable is a dashboard rather than a persona artifact.
Use `$journey-map-generator-skill` when the user wants stages, touchpoints, and emotional arcs instead of profile workbooks.