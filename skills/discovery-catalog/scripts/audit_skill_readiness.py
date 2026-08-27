from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", re.M)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(
    r"\b(TODO|TBD|FIXME|lorem ipsum|placeholder)\b|작성\s*필요|미작성|추후\s*작성|임시\s*내용",
    re.I,
)
SENSITIVE_HINT_RE = re.compile(
    r"(\b\d{6}-\d{7}\b|\b01[016789]-?\d{3,4}-?\d{4}\b|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
)
SOURCE_DATA_HINTS = ("native/", "02_standardized_assets", "내 드라이브", "원천데이터", "참여자명", "주민등록")


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "UX_Research_AI_아이디어_로그.md").exists() and (candidate / ".agents" / "skills").exists():
            return candidate
    raise FileNotFoundError("Could not locate cxi-template repo root")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for key, value in FIELD_RE.findall(match.group(1)):
        fields[key] = value.strip().strip('"').strip("'")
    return fields


def local_markdown_links(skill_dir: Path, text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("#") or target.startswith("mailto:"):
            continue
        clean_target = target.split("#", 1)[0].strip()
        if not clean_target:
            continue
        links.append(
            {
                "target": target,
                "exists": str((skill_dir / clean_target).exists()).lower(),
            }
        )
    return links


def list_script_files(skill_dir: Path) -> list[str]:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return []
    allowed_suffixes = {".py", ".js", ".mjs", ".ts", ".sh", ".bat", ".ps1"}
    return sorted(
        str(path.relative_to(skill_dir)).replace("\\", "/")
        for path in scripts_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed_suffixes
    )


def latest_changelog_has_validation(changelog_text: str) -> bool:
    latest_match = re.search(r"\n##\s+\d{4}-\d{2}-\d{2}.*?(?=\n##\s+\d{4}-\d{2}-\d{2}|\Z)", changelog_text, re.S)
    latest = latest_match.group(0) if latest_match else changelog_text
    if "검증" not in latest:
        return False
    weak_terms = ("미실행", "예정", "수행 예정", "not run", "pending")
    return not any(term in latest.lower() for term in weak_terms)


def audit_skill(skill_dir: Path) -> dict[str, Any]:
    skill_id = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    changelog = skill_dir / "CHANGELOG.md"
    result: dict[str, Any] = {
        "id": skill_id,
        "score": 100,
        "minimumPass": True,
        "releaseTier": "A_READY",
        "blockers": [],
        "warnings": [],
        "checks": {},
        "scripts": [],
    }

    if not skill_md.exists():
        result["blockers"].append("SKILL.md missing")
        result["score"] = 0
        result["minimumPass"] = False
        result["releaseTier"] = "C_HOLD"
        return result

    text = skill_md.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    description = frontmatter.get("description", "")
    body = FRONTMATTER_RE.sub("", text, count=1).strip()
    scripts = list_script_files(skill_dir)
    result["scripts"] = scripts

    checks = result["checks"]
    checks["hasName"] = bool(frontmatter.get("name"))
    checks["hasDescription"] = bool(description)
    checks["descriptionLength"] = len(description)
    checks["bodyLength"] = len(body)
    checks["hasChangelog"] = changelog.exists()
    checks["hasReferencesDir"] = (skill_dir / "references").exists()
    checks["hasScriptsDir"] = (skill_dir / "scripts").exists()
    checks["scriptCount"] = len(scripts)

    if not checks["hasName"]:
        result["blockers"].append("frontmatter name missing")
    if not checks["hasDescription"]:
        result["blockers"].append("frontmatter description missing")
    elif len(description) < 50:
        result["warnings"].append("description is short; clarify trigger and output boundary")
        result["score"] -= 8

    if len(body) < 600:
        result["warnings"].append("SKILL.md body is short; add operating steps, inputs, outputs, and safety boundary")
        result["score"] -= 12

    if not changelog.exists():
        result["warnings"].append("CHANGELOG.md missing")
        result["score"] -= 10
        checks["latestChangelogHasValidation"] = False
    else:
        changelog_text = changelog.read_text(encoding="utf-8")
        has_validation = latest_changelog_has_validation(changelog_text)
        checks["latestChangelogHasValidation"] = has_validation
        if not has_validation:
            result["warnings"].append("latest CHANGELOG entry has no completed validation evidence")
            result["score"] -= 8

    links = local_markdown_links(skill_dir, text)
    broken_links = [item["target"] for item in links if item["exists"] != "true"]
    checks["localLinkCount"] = len(links)
    checks["brokenLocalLinks"] = broken_links
    if broken_links:
        result["blockers"].append(f"broken local markdown links: {', '.join(broken_links)}")
        result["score"] -= 20

    if PLACEHOLDER_RE.search(text):
        result["warnings"].append("placeholder or TODO-like text remains")
        result["score"] -= 10

    if SENSITIVE_HINT_RE.search(text):
        result["warnings"].append("possible email, phone, or resident-id-like value found in SKILL.md")
        result["score"] -= 15

    if any(hint in text for hint in SOURCE_DATA_HINTS):
        result["warnings"].append("source-data path or sensitive-data hint appears; confirm no raw project data is embedded")
        result["score"] -= 6

    if checks["hasScriptsDir"] and not scripts:
        result["warnings"].append("scripts directory exists but no executable script files were found")
        result["score"] -= 5

    result["score"] = max(0, min(100, int(result["score"])))
    if result["blockers"]:
        result["minimumPass"] = False
        result["releaseTier"] = "C_HOLD"
    elif result["score"] >= 85:
        result["releaseTier"] = "A_READY"
    elif result["score"] >= 70:
        result["releaseTier"] = "B_REVIEW"
    else:
        result["minimumPass"] = False
        result["releaseTier"] = "C_HOLD"

    return result


def build_audit(repo_root: Path) -> dict[str, Any]:
    skills_root = repo_root / ".agents" / "skills"
    skills = [
        audit_skill(path)
        for path in sorted(skills_root.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir()
    ]
    summary = {
        "total": len(skills),
        "minimumPass": sum(1 for item in skills if item["minimumPass"]),
        "ready": sum(1 for item in skills if item["releaseTier"] == "A_READY"),
        "review": sum(1 for item in skills if item["releaseTier"] == "B_REVIEW"),
        "hold": sum(1 for item in skills if item["releaseTier"] == "C_HOLD"),
        "blockers": sum(len(item["blockers"]) for item in skills),
        "warnings": sum(len(item["warnings"]) for item in skills),
    }
    return {
        "schemaVersion": "0.1.0",
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "repoRoot": str(repo_root),
        "summary": summary,
        "skills": skills,
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    lines = [
        "# Skill readiness audit",
        "",
        f"- generatedAt: `{audit['generatedAt']}`",
        f"- total skills: `{audit['summary']['total']}`",
        f"- minimum pass: `{audit['summary']['minimumPass']}`",
        f"- ready: `{audit['summary']['ready']}`",
        f"- review: `{audit['summary']['review']}`",
        f"- hold: `{audit['summary']['hold']}`",
        f"- blockers: `{audit['summary']['blockers']}`",
        f"- warnings: `{audit['summary']['warnings']}`",
        "",
        "| skill_id | tier | pass | score | blockers | warnings |",
        "|---|---:|---:|---:|---|---|",
    ]
    for skill in audit["skills"]:
        blockers = "<br>".join(skill["blockers"]) if skill["blockers"] else "-"
        warnings = "<br>".join(skill["warnings"]) if skill["warnings"] else "-"
        lines.append(
            f"| `{skill['id']}` | {skill['releaseTier']} | {skill['minimumPass']} | {skill['score']} | {blockers} | {warnings} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit UXR skills against minimum release-readiness criteria.")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else find_repo_root(Path.cwd().resolve())
    generated_root = repo_root / "website" / "data" / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)
    output_json = args.output_json or generated_root / "skill_readiness_audit.json"
    output_md = args.output_md or generated_root / "skill_readiness_audit.md"

    audit = build_audit(repo_root)
    output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(audit, output_md)

    print(f"skills={audit['summary']['total']}")
    print(f"minimum_pass={audit['summary']['minimumPass']}")
    print(f"ready={audit['summary']['ready']}")
    print(f"review={audit['summary']['review']}")
    print(f"hold={audit['summary']['hold']}")
    print(f"blockers={audit['summary']['blockers']}")
    print(f"warnings={audit['summary']['warnings']}")
    print(f"json={output_json}")
    print(f"markdown={output_md}")


if __name__ == "__main__":
    main()
