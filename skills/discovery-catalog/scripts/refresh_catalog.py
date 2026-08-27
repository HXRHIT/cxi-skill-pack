from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from datetime import date
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "UX_Research_AI_아이디어_로그.md").exists() and (candidate / ".agents").exists():
            return candidate
    raise FileNotFoundError("Could not locate UXR-Template repo root")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_sync_report(repo_root: Path) -> dict[str, Any]:
    generated_root = repo_root / "website" / "data" / "generated"
    overlay_path = repo_root / "website" / "data" / "curated" / "catalog_overlay.json"
    skills_root = repo_root / ".agents" / "skills"

    ideas_payload = load_json(generated_root / "ideas.json")
    skills_payload = load_json(generated_root / "skills.json")
    counts_payload = load_json(generated_root / "counts.json")
    overlay = load_json(overlay_path)

    idea_items = ideas_payload.get("items", [])
    skill_items = skills_payload.get("items", [])
    generated_skill_ids = {item.get("skillName") for item in skill_items if item.get("skillName")}
    actual_skill_ids = {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    } if skills_root.exists() else set()
    skill_fingerprints = {}
    for skill_id in sorted(actual_skill_ids):
        skill_md = skills_root / skill_id / "SKILL.md"
        digest = hashlib.sha256(skill_md.read_bytes()).hexdigest()[:16]
        skill_fingerprints[skill_id] = {
            "sourcePath": str(skill_md),
            "sha256_16": digest,
        }

    warnings: list[str] = []
    if generated_skill_ids != actual_skill_ids:
        missing_in_generated = sorted(actual_skill_ids - generated_skill_ids)
        missing_on_disk = sorted(generated_skill_ids - actual_skill_ids)
        if missing_in_generated:
            warnings.append(f"skills missing in generated snapshot: {', '.join(missing_in_generated)}")
        if missing_on_disk:
            warnings.append(f"generated skills missing on disk: {', '.join(missing_on_disk)}")

    for idx, pair in enumerate(overlay.get("templatePairs", []) if isinstance(overlay, dict) else [], start=1):
        for skill_id in pair.get("currentSkills", []) or []:
            if skill_id not in actual_skill_ids:
                warnings.append(f"templatePairs[{idx}].currentSkills references missing skill: {skill_id}")

    counts = counts_payload.get("counts", {}) if isinstance(counts_payload, dict) else {}
    if counts.get("ideaCards") is not None and counts.get("ideaCards") != len(idea_items):
        warnings.append("counts.ideaCards does not match generated ideas item count")
    if counts.get("installCards") is not None and counts.get("installCards") != len(skill_items):
        warnings.append("counts.installCards does not match generated skills item count")

    return {
        "_meta": {
            "status": "catalog sync report",
            "generatedAt": date.today().isoformat(),
            "generatedBy": ".agents/skills/discovery-catalog/scripts/refresh_catalog.py",
        },
        "counts": {
            "ideas": len(idea_items),
            "skillsGenerated": len(skill_items),
            "skillsOnDisk": len(actual_skill_ids),
            "templatePairs": len(overlay.get("templatePairs", []) if isinstance(overlay, dict) else []),
            "warnings": len(warnings),
        },
        "warnings": warnings,
        "skillFingerprints": skill_fingerprints,
        "sourceFiles": {
            "ideas": str(generated_root / "ideas.json"),
            "skills": str(generated_root / "skills.json"),
            "counts": str(generated_root / "counts.json"),
            "overlay": str(overlay_path),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Template Atlas generated data and write a compact sync report.")
    parser.add_argument("--repo-root", type=Path, default=None, help="UXR-Template repo root. Defaults to auto-detection.")
    parser.add_argument("--skip-refresh", action="store_true", help="Only write the sync report; do not run the existing website generator.")
    parser.add_argument("--report-path", type=Path, default=None, help="Output report path. Defaults to website/data/generated/catalog_sync_report.json.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else find_repo_root(Path.cwd().resolve())
    generator = repo_root / "website" / "scripts" / "build_catalog_generated_data.py"

    if not args.skip_refresh:
        if not generator.exists():
            raise FileNotFoundError(f"Missing existing catalog generator: {generator}")
        runpy.run_path(str(generator), run_name="__main__")

    report = build_sync_report(repo_root)
    report_path = args.report_path or repo_root / "website" / "data" / "generated" / "catalog_sync_report.json"
    write_json(report_path, report)

    print(f"report={report_path}")
    print(f"ideas={report['counts']['ideas']}")
    print(f"skills={report['counts']['skillsOnDisk']}")
    print(f"warnings={report['counts']['warnings']}")


if __name__ == "__main__":
    main()
