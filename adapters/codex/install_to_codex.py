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


def main() -> None:
    parser = argparse.ArgumentParser(description="Install UXR skill pack into Codex personal skills.")
    parser.add_argument("--target", type=Path, default=None, help="Target skills directory. Defaults to %CODEX_HOME%/skills or ~/.codex/skills.")
    args = parser.parse_args()

    root = pack_root()
    target = (args.target or default_codex_skills_dir()).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    target.mkdir(parents=True, exist_ok=True)

    installed = []
    for skill in manifest.get("skills", []):
        skill_id = skill["id"]
        source = root / "skills" / skill_id
        destination = target / skill_id
        shutil.copytree(source, destination, dirs_exist_ok=True)
        installed.append(skill_id)

    print(json.dumps({
        "status": "installed",
        "adapter": "codex",
        "target": str(target),
        "skills": installed,
        "next": "Start a new Codex task or refresh the app so the copied skills can be discovered."
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
