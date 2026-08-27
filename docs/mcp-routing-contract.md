# MCP routing contract

This reference defines the stable request and response shape for MCP-like callers that need to resolve UXR research tasks to canonical skills.

## Request schema

- `action`: `resolve` or `execute`
- `query`: natural-language user request
- `skill_id`: optional canonical `.agents/skills/{skill_id}` directory name
- `stage`: optional `01|02|03|04|05|06|PLATFORM|CROSS|UTIL`
- `artifact_type`: optional `interview|survey|transcript|template|recruiting|dashboard|report|app_review|unknown`
- `goal`: optional `prepare|collect|analyze|synthesize|verify|distribute|maintain`
- `inputs`: optional object with file paths, app IDs, date ranges, output preferences, or project code
- `runner`: optional `auto|prompt`

## Resolve behavior

1. If `skill_id` exactly matches an installed skill directory, resolve to that skill.
2. Otherwise score candidate skills by canonical ID, frontmatter description, idea title, stage, artifact type, and goal.
3. Prefer skills with `SKILL.md` present over idea-only candidates.
4. Prefer validated skills over unverified skills when both are appropriate.
5. If the top result is ambiguous, return up to three candidates and ask the user to choose before execution.

## Resolve response

Return these fields:

- `resolved_skill_id`: canonical ID or `null`
- `candidates`: ranked list when ambiguous
- `reason`: one-sentence rationale
- `required_inputs`: minimum inputs needed before execution
- `estimated_outputs`: likely output artifacts
- `risk_level`: `low`, `medium`, or `high`
- `next`: `execute`, `ask_user`, `dry_run`, or `not_available`

## Execute behavior

- `execute` should only run when the target `skill_id` is canonical and installed.
- If `skill_id` is missing, run `resolve` first and stop.
- If execution would write files, delete files, call paid APIs, expose internal data, or overlap another agent's working scope, return `dry_run` or ask for explicit user approval.
- Preserve action logs with `execution_id`, `skill_id`, `project_code` when a runner exists.

## Risk hints

- `low`: read-only catalog lookup, skill recommendation, generated metadata summary
- `medium`: writing generated catalog JSON, creating a dashboard artifact, producing a report draft
- `high`: editing source templates, modifying internal data, applying anonymization, deleting/moving files, using external paid services

## Fallbacks

- If no installed skill matches, return the closest idea file and label it `idea_only`.
- If generated catalog files are stale or missing, suggest `scripts/refresh_catalog.py`.
- If the request is outside UXR scope, say so and do not force a skill match.
