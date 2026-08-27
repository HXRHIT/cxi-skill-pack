from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


def pack_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_codex_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def ensure_under(root: Path, target: Path) -> None:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    if resolved_target == resolved_root or resolved_root not in resolved_target.parents:
        raise ValueError(f"Refusing to modify path outside target skills dir: {target}")


def write_alias_wrapper(root: Path, target: Path, skill: dict) -> str:
    skill_id = skill["id"]
    short_name = skill.get("shortName") or skill_id
    destination = target / short_name
    destination.mkdir(parents=True, exist_ok=True)
    canonical_skill = root / "skills" / skill_id / "SKILL.md"
    description = f"Short CXI alias for {skill_id}. {skill.get('description', '')}".strip()
    wrapper = f"""---
name: {short_name}
description: {json.dumps(description, ensure_ascii=False)}
---

# {short_name}

This is a short Codex alias for canonical CXI skill `{skill_id}`.

Before doing any task:

1. Read the canonical skill entrypoint completely: `{canonical_skill}`
2. Follow that `SKILL.md` exactly.
3. Use canonical skill ID `{skill_id}` in logs and generated metadata.
4. If the request is risky or ambiguous, ask before executing.
"""
    (destination / "SKILL.md").write_text(wrapper, encoding="utf-8")
    return short_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Install CXI skill pack into Codex personal skills.")
    parser.add_argument("--target", type=Path, default=None, help="Target skills directory. Defaults to %%CODEX_HOME%%/skills or ~/.codex/skills.")
    parser.add_argument("--mode", choices=["alias", "copy"], default="alias", help="alias installs short wrapper skills. copy installs full canonical skill folders.")
    parser.add_argument("--remove-legacy", action="store_true", help="Remove old long canonical skill folders from the target when mode=alias.")
    args = parser.parse_args()

    root = pack_root()
    target = (args.target or default_codex_skills_dir()).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    target.mkdir(parents=True, exist_ok=True)

    installed = []
    legacy_present = []
    for skill in manifest.get("skills", []):
        skill_id = skill["id"]
        source = root / "skills" / skill_id
        if args.mode == "copy":
            destination = target / skill_id
            shutil.copytree(source, destination, dirs_exist_ok=True)
            installed.append(skill_id)
        else:
            installed.append(write_alias_wrapper(root, target, skill))
            legacy_destination = target / skill_id
            if legacy_destination.exists() and skill_id != (skill.get("shortName") or skill_id):
                if args.remove_legacy:
                    ensure_under(target, legacy_destination)
                    shutil.rmtree(legacy_destination)
                else:
                    legacy_present.append(skill_id)

    print(json.dumps({
        "status": "installed",
        "adapter": "codex",
        "mode": args.mode,
        "target": str(target),
        "skills": installed,
        "legacySkillDirsStillPresent": legacy_present,
        "next": "Start a new Codex task or refresh the app. Use short commands such as /app-review, /survey-stats, and /transcript-pii."
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
