---
name: persona-generator-skill
description: "Generate evidence-based persona workbooks by turning synthesized UXR findings into structured persona profiles with core demographics, About, Goals, Frustrations, and optional extended trait fields. Use when Codex needs to create a persona artifact from analyzed survey, interview, app-review, or mixed-method research outputs, especially in the team's workbook format."
---

# Persona Generator Skill

## Overview

Use this skill to turn analyzed research evidence into a persona workbook that matches the team's observed persona structure.
Keep the generation workflow in this file.
Read [references/persona-patterns.md](references/persona-patterns.md) when you need the default sheet schema, naming rules, or narrative-field pattern.

Prefer synthesized evidence rather than raw transcripts or raw survey rows.
If the project is still at coding or descriptive-stat stage, finish that work first before generating personas.

## Inputs

Gather these inputs when available:
- synthesized user segments or archetypes
- supporting evidence from survey, interview, app review, or mixed-method analysis
- key goals, pain points, and behavioral traits by segment
- optional scenario or journey context
- optional English alias or bilingual naming preference
- optional project-specific trait fields such as risk tolerance or decision style

If the available evidence only supports participant summaries rather than stable archetypes, stop short of persona generation and surface that limitation.

## Workflow

### 1. Confirm persona readiness

Check that the inputs are persona-ready:
- segment logic exists or can be defended
- multiple signals point to the same archetype
- goals and frustrations are grounded in observed behavior
- the team is not asking for one persona per participant

Do not convert thin anecdotes into confident personas.

### 2. Define the persona set before writing profiles

Decide how many archetypes the evidence actually supports.
Use stable group labels first, then name individual persona rows within those groups if the workbook format calls for multiple exemplars.

When bilingual naming helps, keep the Korean group label and the English alias aligned rather than inventing separate concepts.

### 3. Build the core workbook sheet

Read [references/persona-patterns.md](references/persona-patterns.md).
Use the `01. Userdoc` style sheet as the default output backbone.
For each persona row, fill:
- group label or user type
- short description
- fictional identity fields
- About summary
- Goals bullets
- Frustrations bullets

Keep the profile concrete enough that a product or research teammate could recognize the segment behavior immediately.

### 4. Add the extended trait sheet when the project needs it

If the project needs deeper profiling, add the second-sheet pattern from [references/persona-patterns.md](references/persona-patterns.md).
Use it for scenario, English alias, income or propensity fields, risk tolerance, decision style, and other structured traits.

Do not invent a second sheet when the project has no evidence for those fields.

### 5. Write narrative fields from evidence, not vibes

Write `About`, `Goals`, and `Frustrations` from the actual research pattern:
- `About` should sound like a compact background narrative, not a slogan
- `Goals` should be action-oriented and specific
- `Frustrations` should describe concrete blockers in the product or task context

Prefer concrete scenario wording over abstract adjectives.

### 6. Hand off with evidence caveats

Return:
- the persona workbook structure
- any fields that were inferred versus directly grounded
- cautions about thin evidence or missing demographic confidence
- the recommended next step for journey mapping, reporting, or review

Point downstream to `$journey-map-generator-skill` when the user wants journey stages and touchpoints rather than profile generation alone.

## Guardrails

- Do not use real participant names or identifying details as persona identities.
- Do not create one persona per participant unless the user explicitly wants case profiles rather than archetypes.
- Do not fill demographic or financial traits when the evidence does not support them.
- Do not write generic goals or frustrations that could fit any product.
- Do not separate Korean and English labels into different concepts.
- Do not skip the evidence caveat when the persona count is a judgment call.

## Expected use cases

Use this skill for prompts such as:
- build a persona workbook from these synthesized findings
- turn these interview and survey insights into personas
- create a team-style xlsx persona artifact from this segment analysis
- generate persona rows with goals, frustrations, and extended trait fields