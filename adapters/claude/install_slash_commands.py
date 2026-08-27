from __future__ import annotations

import argparse
import json
from pathlib import Path


def pack_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_commands_dir() -> Path:
    return Path.home() / ".claude" / "commands" / "uxr"


def command_body(pack: Path, skill: dict, command_name: str) -> str:
    skill_id = skill["id"]
    return f"""설치된 CXI skill pack에서 `{command_name}` 명령으로 canonical `{skill_id}` 스킬을 사용한다.

스킬 진입점:
`{pack / "skills" / skill_id / "SKILL.md"}`

짧은 권장 명령: `{skill.get("command", "/" + command_name)}`
Canonical ID: `{skill_id}`

작업 전 순서:

1. 위 `SKILL.md`를 끝까지 읽는다.
2. 요청에 필요한 경우에만 reference를 추가로 읽는다.
3. 로그와 산출물에는 canonical skill ID `{skill_id}`를 사용한다.
4. 사용자 요청이 애매하거나 위험하면 실행 전에 확인한다.

사용자 요청:
$ARGUMENTS
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Install UXR slash-command adapters for Claude-like agents.")
    parser.add_argument("--commands-dir", type=Path, default=None, help="Target command directory. Defaults to ~/.claude/commands/uxr.")
    args = parser.parse_args()

    root = pack_root()
    commands_dir = (args.commands_dir or default_commands_dir()).resolve()
    commands_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))

    written = []
    for skill in manifest.get("skills", []):
        command_name = skill.get("shortName") or skill["id"]
        path = commands_dir / f"{command_name}.md"
        path.write_text(command_body(root, skill, command_name), encoding="utf-8")
        written.append(str(path))

    print(json.dumps({
        "status": "installed",
        "adapter": "claude-like-slash-commands",
        "commands_dir": str(commands_dir),
        "commands": written,
        "next": "Restart or refresh the Claude-like agent, then invoke commands by the files created in the target commands directory."
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
