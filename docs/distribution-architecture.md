# CXI skill distribution architecture

This reference defines how to package cxi-template skills so teammates can use one deployment repo, `cxi-skill-pack`, from different AI agents.

For the Korean teammate-facing installation guide, see [agent-adapter-install-guide.md](agent-adapter-install-guide.md).

## Design principle

Do not make separate source-of-truth copies for Claude, ChatGPT, Codex, and MCP. Keep one canonical package and generate thin adapters.

The stable core is:

- canonical skill ID: `.agents/skills/{skill_id}`
- short command name: `shortName` in `manifest.json`
- entrypoint: `SKILL.md`
- reusable code: `scripts/`
- optional guidance: `references/`
- catalog metadata: `manifest.json`

Agent-specific behavior should live in adapters, not in duplicated skill content.

## Target package shape

```text
cxi-skill-pack/
├─ manifest.json
├─ update_cxi_skills.bat
├─ README.md
├─ docs/
├─ skills/
│  └─ {skill_id}/
│     ├─ SKILL.md
│     ├─ references/
│     ├─ scripts/
│     └─ CHANGELOG.md
├─ adapters/
│  ├─ README.md
│  └─ slash-commands/
│     ├─ {shortName}.md
└─ runtime/
   ├─ resolve_skill.py
   └─ check_updates.py
```

## Invocation model

There are two supported invocation paths.

### Direct command

If the agent supports custom slash commands, map the short command first:

- `/{shortName}` → resolve to canonical `skill_id`, then read `skills/{skill_id}/SKILL.md`
- `/{skill_id}` → legacy fallback for compatibility through resolver metadata, not a duplicated slash-command file
- then follow the skill instructions
- then run skill scripts only when the user request requires execution

Do not rename canonical skill folders only to make commands shorter. Short aliases are user-facing entrypoints; canonical `skill_id` stays in logs, manifest, reports, and file paths.

### Natural-language routing

If the user says a natural request such as "앱 리뷰 분석해줘" or "전사본 익명화해줘", run the resolver first.

Resolver inputs:

- query
- optional artifact type
- optional stage
- optional goal

Resolver output:

- resolved skill ID
- reason
- required inputs
- estimated outputs
- risk level
- next action

The resolver may be a local script, an MCP tool, or a system prompt wrapper, but it must use the same `manifest.json`.

## Distribution workflow

1. Update or add skills under `.agents/skills/`.
2. Run `python .agents/skills/discovery-catalog/scripts/refresh_catalog.py`.
3. Build or export the package with `python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --output-dir <local-cxi-skill-pack-repo> --clean`.
4. Review the changed distribution repo and publish it.
5. Teammates clone or pull `https://github.com/HXRHIT/cxi-skill-pack`, then point their agent adapter at `manifest.json`.

## Update workflow

After the first install, teammates should not need to manually download a new package every time a skill changes. The package manifest includes a fingerprint for each skill folder, and `runtime/check_updates.py` can compare an installed pack with the latest unpacked pack.

For a local or shared-drive MVP:

```bash
python runtime/check_updates.py --remote-pack <latest-unpacked-cxi-skill-pack-folder>
```

To apply changed/new skills:

```bash
python runtime/check_updates.py --remote-pack <latest-unpacked-cxi-skill-pack-folder> --apply
```

Windows users can run:

```bat
update_cxi_skills.bat <latest-unpacked-cxi-skill-pack-folder>
```

This copies new/changed skill folders and the latest manifest into the installed pack. Removed skills are reported but not deleted automatically, to avoid surprising destructive updates.

## Agent adapter expectations

Each adapter should do only three things:

- expose slash-command style entrypoints when supported
- tell the agent to load the relevant `SKILL.md` before acting
- call `runtime/resolve_skill.py` or an equivalent MCP resolver for natural-language requests

Adapter examples:

- Codex: place or reference the skill folders where Codex can discover them, and use the manifest for routing.
- Claude-like agents: convert the short-name files in `adapters/slash-commands/*.md` into that agent's custom-command format when available.
- ChatGPT-like agents: use the pack as project knowledge or a mounted skill directory, and rely on the resolver manifest for canonical IDs.
- MCP: expose `resolve` and `execute` tools using the schema in `mcp-routing-contract.md`.

## Safety boundary

The package should not contain native project source data. It may contain reusable skill code, instructions, public templates, and generated metadata.

Execution adapters should ask before:

- writing to source project folders
- modifying internal source data
- anonymizing or transforming real participant data
- calling paid or external APIs
- running a skill when multiple candidates are plausible

## Versioning

Use a package version or timestamp and include:

- `generatedAt`
- source repo name
- skill count
- skill IDs
- skill fingerprints
- sync report summary
- optional zip filename

For team usage, treat `manifest.json` as the package contract, `cxi-skill-pack` as the deployment repo, and `.agents/skills/*` in cxi-template as the source.
