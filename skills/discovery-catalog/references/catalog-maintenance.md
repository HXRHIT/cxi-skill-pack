# Catalog maintenance guide

Use this reference when the user asks to refresh, repair, or extend the Template Atlas / discovery catalog.

## Existing architecture

- `UX_Research_AI_아이디어_로그.md`: idea number, stage, readiness, validation, feedback status
- `ideas/*.md`: detailed idea documentation
- `.agents/skills/*/SKILL.md`: installed or authored skill entrypoints
- `website/data/generated/*.json`: machine-generated base metadata
- `website/data/curated/catalog_overlay.json`: human-curated highlights, display copy, and template-skill pair summaries
- `website/app.js`: render and fallback layer

The intended pattern is generated base + curated overlay + render layer. Do not make `website/app.js` the new source of truth.

## Refresh routine

1. Define the target scope before editing.
2. If only counts or generated base metadata changed, run or update `scripts/refresh_catalog.py`.
3. If short Korean card copy, highlight reasons, or template-skill pair summaries changed, edit `website/data/curated/catalog_overlay.json`.
4. If the UI behavior changed, edit `website/app.js` only after the data layer contract is clear.
5. Update the relevant idea file and skill `CHANGELOG.md` when behavior changes.

## Automatic update rule for skill changes

When any agent changes `.agents/skills/*/SKILL.md`, `.agents/skills/*/references/`, `.agents/skills/*/scripts/`, or `.agents/skills/*/CHANGELOG.md`, the agent should run:

```bash
python .agents/skills/discovery-catalog/scripts/refresh_catalog.py
```

This refreshes `website/data/generated/ideas.json`, `website/data/generated/skills.json`, `website/data/generated/counts.json`, and writes `website/data/generated/catalog_sync_report.json`.

Do not run competing refreshes in parallel. If another agent is actively changing generated catalog files, wait for that work to settle or ask the user to choose an order.

## Drift checks

Check for these warnings when maintaining the catalog:

- idea count differs from master log rows
- install card count differs from `.agents/skills/*/SKILL.md`
- `currentSkills` in overlay references a missing skill directory
- `readyNowHighlights` references a non-ready idea
- `decisionHighlights` references a ready or ended idea
- an idea moved to ready/skill-written status but remains in `futureSkills`
- a generated title/status contradicts a curated short label

## Multi-agent coordination

- Avoid editing files another agent has just changed or claimed.
- Keep work units separate by folder where possible: one agent owns a skill folder, another owns website rendering, another owns an idea document.
- If the same file must be touched by multiple agents, ask the user to choose an order rather than merging blindly.
- Generated files can be refreshed by one agent after source edits settle; avoid multiple agents regenerating snapshots at the same time.

## What to preserve

- Canonical skill IDs must remain directory names.
- Curated Korean copy should not be overwritten by generated descriptions.
- Historical idea files should not be deleted when ideas are merged or ended.
- Generated JSON should remain reproducible from repo sources.
