from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: mcp. Install with `pip install mcp`, then run this server again."
    ) from exc


PACK_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PACK_ROOT / "manifest.json"
mcp = FastMCP("cxi-skill-pack")


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def normalize_skill_key(value: str) -> str:
    return value.strip().lower().removeprefix("/").replace("_", "-")


def find_skill(skill_id: str) -> dict[str, Any] | None:
    wanted = normalize_skill_key(skill_id)
    for skill in load_manifest().get("skills", []):
        aliases = [skill.get("id", ""), skill.get("shortName", ""), *skill.get("aliases", []), *skill.get("commands", [])]
        if wanted in {normalize_skill_key(alias) for alias in aliases if alias}:
            return skill
    return None


@mcp.tool()
def resolve_skill(query: str, skill_id: str | None = None) -> dict[str, Any]:
    """Resolve a natural-language UXR request or canonical skill_id to a skill."""
    manifest = load_manifest()
    if skill_id:
        skill = find_skill(skill_id)
        if skill:
            return {
                "resolved_skill_id": skill_id,
                "candidates": [skill],
                "reason": "skill_id matched a canonical CXI skill ID or short alias.",
                "required_inputs": ["user request", "skill-specific inputs"],
                "estimated_outputs": ["see resolved SKILL.md"],
                "risk_level": "medium" if skill.get("hasScripts") else "low",
                "next": "execute",
            }
    result = subprocess.run(
        [sys.executable, str(PACK_ROOT / "runtime" / "resolve_skill.py"), query, "--manifest", str(MANIFEST_PATH)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


@mcp.tool()
def read_skill(skill_id: str) -> dict[str, Any]:
    """Read a canonical skill entrypoint."""
    skill = find_skill(skill_id)
    if not skill:
        return {"status": "not_found", "skill_id": skill_id}
    path = PACK_ROOT / skill["entrypoint"]
    return {
        "status": "ok",
        "skill_id": skill_id,
        "path": str(path),
        "content": path.read_text(encoding="utf-8"),
    }


@mcp.tool()
def execute_skill(skill_id: str, query: str, inputs: dict[str, Any] | None = None, dry_run: bool = True) -> dict[str, Any]:
    """Prepare skill execution. Defaults to dry_run for safety."""
    skill = find_skill(skill_id)
    if not skill:
        return {"status": "not_found", "skill_id": skill_id}
    skill_path = PACK_ROOT / skill["entrypoint"]
    return {
        "status": "dry_run" if dry_run else "needs_runner",
        "skill_id": skill_id,
        "query": query,
        "inputs": inputs or {},
        "skill_path": str(skill_path),
        "next": "Load SKILL.md, confirm required inputs and safety, then call the skill-specific runner. This starter does not auto-mutate files.",
    }


if __name__ == "__main__":
    mcp.run()
