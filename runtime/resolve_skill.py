from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", "-")).strip()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def score_skill(query: str, skill: dict) -> int:
    q = normalize(query)
    skill_id = normalize(skill.get("id", ""))
    description = normalize(skill.get("description", ""))
    if q == "/" + skill_id or q == skill_id:
        return 100
    score = 0
    for keyword in skill.get("keywords", []):
        normalized_keyword = normalize(keyword)
        if normalized_keyword and normalized_keyword in q:
            score += 20
    for token in re.split(r"[^0-9a-zA-Z가-힣-]+", q):
        if not token:
            continue
        if token in skill_id:
            score += 8
        if token in description:
            score += 3
    return score


def resolve(query: str, manifest: dict, limit: int = 3) -> dict:
    scored = [
        {**skill, "score": score_skill(query, skill)}
        for skill in manifest.get("skills", [])
    ]
    scored = sorted(scored, key=lambda item: item["score"], reverse=True)
    candidates = [item for item in scored if item["score"] > 0][:limit]
    if not candidates:
        return {
            "resolved_skill_id": None,
            "candidates": [],
            "reason": "No matching UXR skill was found.",
            "required_inputs": [],
            "estimated_outputs": [],
            "risk_level": "low",
            "next": "not_available",
        }
    if len(candidates) == 1 or candidates[0]["score"] >= candidates[1]["score"] + 8:
        top = candidates[0]
        return {
            "resolved_skill_id": top["id"],
            "candidates": candidates[:1],
            "reason": f"Best match by canonical ID/description score: {top['score']}",
            "required_inputs": ["user request", "source files or parameters required by the resolved SKILL.md"],
            "estimated_outputs": ["see resolved SKILL.md"],
            "risk_level": "medium" if top.get("hasScripts") else "low",
            "next": "execute",
        }
    return {
        "resolved_skill_id": None,
        "candidates": candidates,
        "reason": "Multiple plausible skills matched the request.",
        "required_inputs": ["choose one canonical skill_id"],
        "estimated_outputs": ["depends on selected skill"],
        "risk_level": "medium",
        "next": "ask_user",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve a natural-language UXR request to a canonical skill ID.")
    parser.add_argument("query")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "manifest.json")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(resolve(args.query, load_manifest(args.manifest), args.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
