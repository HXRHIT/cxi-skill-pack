from __future__ import annotations

import argparse
import json
from pathlib import Path


def pack_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ChatGPT project instructions for the CXI skill pack.")
    parser.add_argument("--target-dir", type=Path, default=None, help="Where to write ChatGPT adapter files. Defaults to adapters/chatgpt/generated.")
    args = parser.parse_args()

    root = pack_root()
    target = (args.target_dir or (root / "adapters" / "chatgpt" / "generated")).resolve()
    target.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    skills = manifest.get("skills", [])

    lines = [
        "# ChatGPT 계열 agent용 CXI Skill Pack 안내문",
        "",
        "이 문서는 로컬 CXI skill pack을 ChatGPT Project 또는 Custom GPT에서 사용하기 위한 얇은 adapter 안내문이다.",
        "",
        f"Skill pack 위치: `{root}`",
        f"Manifest 위치: `{root / 'manifest.json'}`",
        "",
        "사용자가 UXR 작업을 요청하면:",
        "",
        "1. 사용자가 `/{skill_id}`를 쓰면 pack에서 해당 스킬의 `SKILL.md`를 읽는다.",
        "2. 사용자가 자연어로 요청하면 먼저 `manifest.json` 기준으로 적절한 스킬을 찾는다.",
        "3. 아래 canonical skill ID를 그대로 사용한다.",
        "4. 파일 쓰기, 민감정보 처리, 외부 API 호출, 애매한 요청 실행 전에는 사용자에게 확인한다.",
        "",
        "사용 가능한 스킬:",
    ]
    for skill in skills:
        lines.append(f"- `{skill['id']}`: {skill.get('description', '')}")

    (target / "CHATGPT_PROJECT_INSTRUCTIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (target / "manifest_summary.json").write_text(json.dumps({
        "manifest": str(root / "manifest.json"),
        "skillCount": len(skills),
        "commands": [skill["command"] for skill in skills],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "generated",
        "adapter": "chatgpt-like-project",
        "target": str(target),
        "files": [
            str(target / "CHATGPT_PROJECT_INSTRUCTIONS.md"),
            str(target / "manifest_summary.json")
        ],
        "next": "생성된 안내문을 ChatGPT Project 또는 Custom GPT instructions에 넣고, 위 경로의 skill pack을 사용할 수 있게 유지하세요."
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
