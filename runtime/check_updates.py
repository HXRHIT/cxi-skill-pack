from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def skill_map(manifest: dict) -> dict:
    return {skill["id"]: skill for skill in manifest.get("skills", []) if skill.get("id")}


def compare(local_manifest: dict, remote_manifest: dict) -> dict:
    local = skill_map(local_manifest)
    remote = skill_map(remote_manifest)
    new = sorted(set(remote) - set(local))
    removed = sorted(set(local) - set(remote))
    changed = sorted(
        skill_id for skill_id in set(local) & set(remote)
        if local[skill_id].get("fingerprint") != remote[skill_id].get("fingerprint")
    )
    return {
        "new": new,
        "changed": changed,
        "removed": removed,
        "hasUpdates": bool(new or changed or removed),
    }


def copy_changed_skills(installed_root: Path, remote_root: Path, diff: dict) -> None:
    for skill_id in [*diff["new"], *diff["changed"]]:
        source = remote_root / "skills" / skill_id
        target = installed_root / "skills" / skill_id
        if not source.exists():
            raise FileNotFoundError(f"Remote skill is missing: {source}")
        shutil.copytree(source, target, dirs_exist_ok=True)
    shutil.copy2(remote_root / "manifest.json", installed_root / "manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check or apply updates between two CXI skill packs.")
    parser.add_argument("--installed-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--remote-pack", type=Path, required=True, help="Path to the latest unpacked cxi-skill-pack folder.")
    parser.add_argument("--apply", action="store_true", help="Copy new/changed skills and manifest from remote-pack into installed-root.")
    args = parser.parse_args()

    installed_root = args.installed_root.resolve()
    remote_root = args.remote_pack.resolve()
    local_manifest = load_manifest(installed_root / "manifest.json")
    remote_manifest = load_manifest(remote_root / "manifest.json")
    diff = compare(local_manifest, remote_manifest)

    if args.apply and diff["hasUpdates"]:
        copy_changed_skills(installed_root, remote_root, diff)
        diff["applied"] = True
    else:
        diff["applied"] = False

    print(json.dumps(diff, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
