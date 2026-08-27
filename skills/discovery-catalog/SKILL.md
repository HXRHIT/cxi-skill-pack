---
name: discovery-catalog
description: Resolve, explain, and maintain the UXR team's template/skill catalog so agents and MCP-like callers can consistently find the right research skill without duplicating work.
---

# Discovery Catalog

Use this skill when the user asks to find, recommend, route, list, or maintain UXR templates/skills, especially when multiple AI agents or MCP-like tools need the same canonical skill IDs.

Do not use this skill to perform the downstream research work itself. Resolve the right skill first, then use that domain skill if the user asks to execute it.

## Core rules

- Treat `.agents/skills/{skill_id}/SKILL.md` directory names as canonical executable skill IDs.
- Treat `UX_Research_AI_아이디어_로그.md` as the idea/status SSOT and `ideas/*.md` as detail pages.
- Reuse the existing website metadata architecture: generated base data plus curated overlay. Do not create a second unrelated catalog.
- Before editing, name the exact file scope and avoid files another agent is already working on. If the needed file overlaps another agent's active scope, stop and ask the user before changing it.
- Prefer read-only resolution first. Only mutate generated data, overlay files, or website rendering when the user explicitly asks for a refresh, update, or implementation.

## Common modes

### Resolve a user request to a skill

Return a compact answer with:

- `resolved_skill_id`
- `reason`
- `required_inputs`
- `estimated_outputs`
- `risk_level`
- `next`

If the request maps to several skills, return at most three candidates and explain the difference. Use canonical IDs only for executable recommendations.

For MCP-style schema and scoring rules, read [references/mcp-routing-contract.md](references/mcp-routing-contract.md).

For a teammate-friendly step-by-step guide to actually calling skills through MCP, read [references/mcp-execution-guide.md](references/mcp-execution-guide.md).

### Refresh or maintain the catalog

Use the existing website data flow instead of rewriting the catalog:

- generated source: `website/data/generated/*.json`
- curated source: `website/data/curated/catalog_overlay.json`
- existing generator: `website/scripts/build_catalog_generated_data.py`
- skill wrapper: `scripts/refresh_catalog.py`

Whenever any `.agents/skills/*` skill entrypoint, reference, script, or changelog is updated, run `python .agents/skills/discovery-catalog/scripts/refresh_catalog.py` before finishing so #33 sees the latest skill inventory. If another agent is already refreshing `website/data/generated/`, pause and ask the user to sequence the work.

Read [references/catalog-maintenance.md](references/catalog-maintenance.md) before changing `website/`, generated JSON, or overlay data.

### Package skills for team distribution

When the user wants teammates to download the UXR skills and use them from Claude, ChatGPT, Codex, or MCP-like tools, use the shared distribution architecture instead of creating agent-specific forks.

Read [references/distribution-architecture.md](references/distribution-architecture.md), then build a package with:

```bash
python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --zip
```

The package contains copied canonical skill folders, a `manifest.json`, slash-command adapter prompts, and a local natural-language resolver. Treat this as a portable starter pack; each agent may still need a thin install step that points to the same manifest and skill folders.

For the Korean teammate-facing installation guide, read [references/agent-adapter-install-guide.md](references/agent-adapter-install-guide.md).

Use short user-facing commands from `manifest.json` such as `/app-review`, `/survey-stats`, and `/transcript-pii`. Keep long canonical skill IDs as internal stable IDs for file paths, logs, MCP responses, and generated reports.

### Audit readiness and select release candidates

When the user asks whether skills are ready for distribution or which skills should be included in the first release, use the release policy and generated reports instead of deciding from memory.

Read [references/release-policy.md](references/release-policy.md), then run:

```bash
python .agents/skills/discovery-catalog/scripts/audit_skill_readiness.py
python .agents/skills/discovery-catalog/scripts/select_release_candidates.py --version v0.1
```

Default outputs:

- `website/data/generated/skill_readiness_audit.json`
- `website/data/generated/skill_readiness_audit.md`
- `website/data/generated/release_candidates_v0.1.json`
- `website/data/generated/release_candidates_v0.1.md`

AI may recommend release lanes, but a human owner must approve the official release list before publishing to `cxi-skill-pack`.

### Validate this skill

Use the skill-creator validator:

```bash
python -X utf8 C:/Users/hanati/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/discovery-catalog
```

The `-X utf8` flag is recommended on Windows because this repo uses Korean UTF-8 Markdown and the validator may otherwise read files with the system codepage.

### Explain what exists

When the user asks "what should we work on next" or "what skills exist", summarize by workflow:

- planning and QA
- transcript processing
- interview analysis
- survey analysis
- dashboards and reports
- platform/catalog/automation

Call out unverified or decision-dependent skills separately so the team does not confuse prototypes with ready-to-run tools.

## Operating boundary

- Do not execute a downstream skill just because resolution found a match.
- Do not edit `website/app.js` unless the user asks to change the catalog UI/rendering.
- Do not replace curated Korean UI copy with generated English descriptions unless the user requests a full regeneration.
- Do not mark an idea as ready or validated unless the corresponding files and validation evidence actually exist.
