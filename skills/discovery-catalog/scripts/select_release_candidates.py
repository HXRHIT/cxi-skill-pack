from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


CORE_PRIORITY = {
    "discovery-catalog": 100,
    "app-review-analysis-pipeline": 96,
    "template-hygiene-checker": 94,
    "research-qa-skill": 92,
    "transcript-verification-enhancer": 91,
    "transcript-anonymizer-skill": 90,
    "survey-data-preprocessing": 88,
    "survey-basic-stats-analysis": 87,
    "survey-analysis-verification": 86,
    "survey-results-dashboard": 84,
    "survey-open-ended-coding-skill": 82,
    "qual-thematic-coding-skill": 80,
    "interview-results-dashboard": 78,
}


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "UX_Research_AI_아이디어_로그.md").exists() and (candidate / ".agents" / "skills").exists():
            return candidate
    raise FileNotFoundError("Could not locate cxi-template repo root")


def load_audit(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Audit file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def release_score(skill: dict[str, Any]) -> int:
    priority = CORE_PRIORITY.get(skill["id"], 60)
    readiness = int(skill.get("score", 0))
    blocker_penalty = len(skill.get("blockers", [])) * 30
    warning_penalty = min(20, len(skill.get("warnings", [])) * 3)
    return max(0, min(100, round(priority * 0.55 + readiness * 0.45 - blocker_penalty - warning_penalty)))


def classify(skill: dict[str, Any]) -> str:
    score = release_score(skill)
    if skill.get("blockers"):
        return "hold"
    if skill.get("minimumPass") and score >= 78:
        return "release"
    if skill.get("minimumPass") or score >= 65:
        return "pilot"
    return "hold"


def reason_for(skill: dict[str, Any], lane: str) -> str:
    if lane == "release":
        return "minimum criteria passed and the skill is high-priority for the first team distribution."
    if lane == "pilot":
        return "usable candidate, but it needs either more validation evidence, clearer documentation, or lower-priority rollout."
    blockers = skill.get("blockers", [])
    if blockers:
        return f"blocked by minimum criteria: {', '.join(blockers)}"
    return "below first-release threshold."


def build_release_plan(audit: dict[str, Any], version: str) -> dict[str, Any]:
    lanes = {"release": [], "pilot": [], "hold": []}
    for skill in audit.get("skills", []):
        lane = classify(skill)
        entry = {
            "id": skill["id"],
            "releaseScore": release_score(skill),
            "readinessScore": skill.get("score", 0),
            "readinessTier": skill.get("releaseTier"),
            "minimumPass": skill.get("minimumPass"),
            "blockers": skill.get("blockers", []),
            "warnings": skill.get("warnings", []),
            "reason": reason_for(skill, lane),
        }
        lanes[lane].append(entry)

    for lane_items in lanes.values():
        lane_items.sort(key=lambda item: (-item["releaseScore"], item["id"]))

    return {
        "schemaVersion": "0.1.0",
        "version": version,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "policy": "AI recommends the release bundle; a human owner approves the official release.",
        "summary": {
            "release": len(lanes["release"]),
            "pilot": len(lanes["pilot"]),
            "hold": len(lanes["hold"]),
            "sourceAuditGeneratedAt": audit.get("generatedAt"),
        },
        "recommendedRelease": lanes["release"],
        "pilotOnly": lanes["pilot"],
        "hold": lanes["hold"],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    lines = [
        f"# Release candidates {plan['version']}",
        "",
        f"- generatedAt: `{plan['generatedAt']}`",
        f"- release: `{plan['summary']['release']}`",
        f"- pilot: `{plan['summary']['pilot']}`",
        f"- hold: `{plan['summary']['hold']}`",
        "- decision: AI recommendation only. Human approval is required before official release.",
        "",
        "## Recommended first release",
        "",
        "| skill_id | release score | readiness | reason |",
        "|---|---:|---:|---|",
    ]
    for item in plan["recommendedRelease"]:
        lines.append(f"| `{item['id']}` | {item['releaseScore']} | {item['readinessScore']} | {item['reason']} |")

    lines.extend(["", "## Pilot only", "", "| skill_id | release score | readiness | reason |", "|---|---:|---:|---|"])
    for item in plan["pilotOnly"]:
        lines.append(f"| `{item['id']}` | {item['releaseScore']} | {item['readinessScore']} | {item['reason']} |")

    lines.extend(["", "## Hold", "", "| skill_id | release score | readiness | reason |", "|---|---:|---:|---|"])
    for item in plan["hold"]:
        lines.append(f"| `{item['id']}` | {item['releaseScore']} | {item['readinessScore']} | {item['reason']} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Select first-release candidates from a skill readiness audit.")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--audit-json", type=Path, default=None)
    parser.add_argument("--version", default="v0.1")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else find_repo_root(Path.cwd().resolve())
    generated_root = repo_root / "website" / "data" / "generated"
    audit_json = args.audit_json or generated_root / "skill_readiness_audit.json"
    output_json = args.output_json or generated_root / f"release_candidates_{args.version}.json"
    output_md = args.output_md or generated_root / f"release_candidates_{args.version}.md"

    plan = build_release_plan(load_audit(audit_json), args.version)
    output_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, output_md)

    print(f"version={plan['version']}")
    print(f"release={plan['summary']['release']}")
    print(f"pilot={plan['summary']['pilot']}")
    print(f"hold={plan['summary']['hold']}")
    print(f"json={output_json}")
    print(f"markdown={output_md}")


if __name__ == "__main__":
    main()
