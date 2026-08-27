from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


KEYWORD_RULES: dict[str, list[str]] = {
    "app-review-analysis-pipeline": ["앱 리뷰", "리뷰 분석", "평점", "플레이스토어", "앱스토어", "play store", "app store"],
    "coding-sheet-generator": ["코딩 시트", "객관식 코딩", "리커트", "순위형", "워크북 scaffold"],
    "discovery-catalog": ["스킬 찾기", "스킬 추천", "카탈로그", "디스커버리", "skill routing", "mcp"],
    "executive-one-pager-skill": ["원페이저", "임원 요약", "executive summary", "1pager", "요약 슬라이드"],
    "followup-implementation-tracker": ["후속조치", "개선안 추적", "반영 여부", "implementation review"],
    "interview-interim-report-writer": ["인터뷰 중간보고서", "인터뷰 보고서", "정성 보고서"],
    "interview-quant-coding-skill": ["인터뷰 정량 코딩", "태깅 매트릭스", "빈도 코딩"],
    "interview-results-dashboard": ["인터뷰 대시보드", "인터뷰 결과", "quick summary"],
    "persona-generator-skill": ["페르소나", "persona"],
    "qual-thematic-coding-skill": ["정성 코딩", "테마 코딩", "어피니티", "인터뷰 분석"],
    "recruiting-list-legend-generator": ["리크루팅", "참여자 명단", "범례", "pid"],
    "research-plan-writer-skill": ["리서치 계획서", "연구계획", "rq", "rh", "프로토콜"],
    "research-qa-skill": ["질문지 qa", "편향 검증", "설문 검수", "인터뷰 가이드 검수"],
    "survey-analysis-verification": ["서베이 검증", "분석 검증", "가설 검증", "n수 확인"],
    "survey-basic-stats-analysis": ["기초통계", "설문 통계", "평균", "표준편차", "top box"],
    "survey-data-preprocessing": ["서베이 전처리", "설문 전처리", "cleaned dataset", "codebook"],
    "survey-interim-report-writer": ["서베이 중간보고서", "설문 보고서", "survey report"],
    "survey-open-ended-coding-skill": ["개방형 응답", "주관식 코딩", "오픈엔드", "codebook"],
    "survey-results-dashboard": ["서베이 대시보드", "설문 대시보드", "survey dashboard"],
    "transcript-anonymizer-skill": ["익명화", "개인정보", "pii", "전사본 마스킹"],
    "transcript-pipeline-skill": ["전사본 파이프라인", "전사 정리", "익명화까지"],
    "transcript-verification-enhancer": ["전사본 검증", "stt", "화자 분리", "오타 교정"],
}

PACKAGE_NAME = "cxi-skill-pack"
SOURCE_REPO_NAME = "UXR-Template"
PUBLIC_REPO_URL = "https://github.com/HXRHIT/cxi-skill-pack"
GENERATED_OUTPUT_NAMES = {
    "README.md",
    "manifest.json",
    "update_cxi_skills.bat",
    "update_uxr_skills.bat",
    "skills",
    "adapters",
    "runtime",
    "docs",
}


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "UX_Research_AI_아이디어_로그.md").exists() and (candidate / ".agents").exists():
            return candidate
    raise FileNotFoundError("Could not locate UXR-Template repo root")


def extract_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def extract_field(frontmatter: str, field: str) -> str:
    patterns = [
        rf"^{re.escape(field)}:\s*\"(.*)\"\s*$",
        rf"^{re.escape(field)}:\s*'(.*)'\s*$",
        rf"^{re.escape(field)}:\s*(.+?)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, frontmatter, re.M)
        if match:
            return match.group(1).strip()
    return ""


def should_package_file(path: Path) -> bool:
    ignored_parts = {"__pycache__", ".pytest_cache", ".mypy_cache"}
    if any(part in ignored_parts for part in path.parts):
        return False
    return not path.name.endswith(".pyc") and path.name not in {".DS_Store"}


def hash_skill_dir(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or not should_package_file(path):
            continue
        rel = path.relative_to(skill_dir).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def scan_skills(skills_root: Path) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(skills_root.iterdir(), key=lambda path: path.name.lower()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(text)
        skills.append(
            {
                "id": skill_dir.name,
                "name": extract_field(frontmatter, "name") or skill_dir.name,
                "description": extract_field(frontmatter, "description"),
                "entrypoint": f"skills/{skill_dir.name}/SKILL.md",
                "command": f"/{skill_dir.name}",
                "keywords": KEYWORD_RULES.get(skill_dir.name, []),
                "hasScripts": (skill_dir / "scripts").exists(),
                "hasReferences": (skill_dir / "references").exists(),
                "fingerprint": hash_skill_dir(skill_dir),
            }
        )
    return skills


def copy_skills(skills_root: Path, output_skills_root: Path) -> None:
    output_skills_root.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(skills_root.iterdir(), key=lambda path: path.name.lower()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue
        shutil.copytree(
            skill_dir,
            output_skills_root / skill_dir.name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache", ".DS_Store"),
        )


def ensure_safe_child(root: Path, target: Path) -> None:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    if resolved_target == resolved_root or resolved_root not in resolved_target.parents:
        raise ValueError(f"Refusing to modify a path outside the output root: {target}")


def prepare_output_root(output_root: Path, clean: bool) -> None:
    if not output_root.exists():
        output_root.mkdir(parents=True)
        return

    if not output_root.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {output_root}")

    existing = [path for path in output_root.iterdir() if path.name != ".git"]
    if not existing:
        return

    unknown = [path.name for path in existing if path.name not in GENERATED_OUTPUT_NAMES]
    if unknown:
        raise FileExistsError(
            f"Output directory has non-generated files: {', '.join(sorted(unknown))}. "
            "Use an empty deployment repo or move those files before exporting."
        )

    if not clean:
        raise FileExistsError(
            f"Output directory already contains generated files: {output_root}. "
            "Re-run with --clean to replace generated bundle contents while preserving .git."
        )

    for path in existing:
        ensure_safe_child(output_root, path)
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def write_adapter_files(output_root: Path, skills: list[dict[str, Any]]) -> None:
    adapters_root = output_root / "adapters"
    commands_root = adapters_root / "slash-commands"
    commands_root.mkdir(parents=True, exist_ok=True)
    (adapters_root / "codex").mkdir(parents=True, exist_ok=True)
    (adapters_root / "claude").mkdir(parents=True, exist_ok=True)
    (adapters_root / "chatgpt").mkdir(parents=True, exist_ok=True)
    (adapters_root / "mcp").mkdir(parents=True, exist_ok=True)

    readme = """# CXI Skill Pack 어댑터

이 폴더에는 AI agent별 설치/연결 도구가 들어 있다. 스킬 원본은 항상 `skills/{skill_id}/SKILL.md`이다.

agent가 custom slash command를 지원하면 아래처럼 직접 호출할 수 있다.

```text
/{skill_id}
```

자연어 요청은 `runtime/resolve_skill.py`로 먼저 어떤 스킬이 맞는지 찾은 뒤, resolved된 `SKILL.md`를 읽는다.

agent별 adapter 안에 스킬 내용을 복제하지 않는다. 스킬이 바뀌면 UXR-Template에서 package를 다시 만들고 cxi-skill-pack repo를 갱신한다.
"""
    (adapters_root / "README.md").write_text(readme, encoding="utf-8")

    for skill in skills:
        command_text = f"""# {skill['command']}

UXR 스킬 `{skill['id']}`를 사용한다.

작업 전 순서:

1. `skills/{skill['id']}/SKILL.md`를 끝까지 읽는다.
2. 현재 요청에 필요할 때만 reference 파일을 추가로 읽는다.
3. 실행이 필요하고 허용된 경우에만 `skills/{skill['id']}/scripts/` 안의 코드를 실행한다.
4. 요청이 애매하면 추측하지 말고 먼저 resolve한다.
"""
        (commands_root / f"{skill['id']}.md").write_text(command_text, encoding="utf-8")

    codex_installer = r'''
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
'''.lstrip()
    (adapters_root / "codex" / "install_to_codex.py").write_text(codex_installer, encoding="utf-8")
    (adapters_root / "codex" / "install_to_codex.bat").write_text(
        '@echo off\npython "%~dp0install_to_codex.py" %*\n',
        encoding="utf-8",
    )
    (adapters_root / "codex" / "README.md").write_text(
        """# Codex 어댑터

clone 또는 압축 해제한 `cxi-skill-pack` 폴더에서 실행한다.

```bat
adapters\\codex\\install_to_codex.bat
```

기본값은 모든 `skills/*` 폴더를 `%CODEX_HOME%\\skills` 또는 `~/.codex/skills`로 복사한다.

다른 위치에 설치하려면:

```bash
python adapters/codex/install_to_codex.py --target C:/path/to/skills
```
""",
        encoding="utf-8",
    )

    claude_installer = r'''
from __future__ import annotations

import argparse
import json
from pathlib import Path


def pack_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_commands_dir() -> Path:
    return Path.home() / ".claude" / "commands" / "uxr"


def command_body(pack: Path, skill: dict) -> str:
    skill_id = skill["id"]
    return f"""설치된 UXR skill pack에서 `{skill_id}` 스킬을 사용한다.

스킬 진입점:
`{pack / "skills" / skill_id / "SKILL.md"}`

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
        path = commands_dir / f"{skill['id']}.md"
        path.write_text(command_body(root, skill), encoding="utf-8")
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
'''.lstrip()
    (adapters_root / "claude" / "install_slash_commands.py").write_text(claude_installer, encoding="utf-8")
    (adapters_root / "claude" / "install_slash_commands.bat").write_text(
        '@echo off\npython "%~dp0install_slash_commands.py" %*\n',
        encoding="utf-8",
    )
    (adapters_root / "claude" / "README.md").write_text(
        """# Claude 계열 slash command 어댑터

clone 또는 압축 해제한 `cxi-skill-pack` 폴더에서 실행한다.

```bat
adapters\\claude\\install_slash_commands.bat
```

기본값은 command 파일을 `~/.claude/commands/uxr`에 만든다.

사용하는 agent의 command 위치가 다르면:

```bash
python adapters/claude/install_slash_commands.py --commands-dir C:/path/to/commands/uxr
```

생성된 command 파일은 이 skill pack의 `skills/{skill_id}/SKILL.md`를 읽도록 안내한다.
""",
        encoding="utf-8",
    )

    chatgpt_installer = r'''
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
'''.lstrip()
    (adapters_root / "chatgpt" / "generate_project_instructions.py").write_text(chatgpt_installer, encoding="utf-8")
    (adapters_root / "chatgpt" / "generate_project_instructions.bat").write_text(
        '@echo off\npython "%~dp0generate_project_instructions.py" %*\n',
        encoding="utf-8",
    )
    (adapters_root / "chatgpt" / "README.md").write_text(
        """# ChatGPT 계열 Project 어댑터

ChatGPT 계열 도구는 로컬 coding agent처럼 slash command 설치를 직접 지원하지 않을 수 있다.

먼저 실행:

```bat
adapters\\chatgpt\\generate_project_instructions.bat
```

생성된 `CHATGPT_PROJECT_INSTRUCTIONS.md`를 project/custom GPT instructions로 사용한다. 로컬 파일을 직접 읽을 수 없는 환경이라면 MCP 서버를 함께 연결한다.
""",
        encoding="utf-8",
    )

    mcp_server = r'''
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


def find_skill(skill_id: str) -> dict[str, Any] | None:
    for skill in load_manifest().get("skills", []):
        if skill.get("id") == skill_id:
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
                "reason": "skill_id matched a canonical UXR skill ID.",
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
'''.lstrip()
    (adapters_root / "mcp" / "uxr_mcp_server.py").write_text(mcp_server, encoding="utf-8")
    (adapters_root / "mcp" / "requirements.txt").write_text("mcp\n", encoding="utf-8")
    (adapters_root / "mcp" / "run_mcp_server.bat").write_text(
        '@echo off\npython "%~dp0uxr_mcp_server.py"\n',
        encoding="utf-8",
    )
    (adapters_root / "mcp" / "mcp_config.example.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                "cxi-skill-pack": {
                    "command": "python",
                    "args": ["adapters/mcp/uxr_mcp_server.py"],
                    "cwd": "<absolute-path-to-cxi-skill-pack>",
                    }
                }
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (adapters_root / "mcp" / "README.md").write_text(
        """# MCP 어댑터

이 starter는 도구 3개를 제공한다.

- `resolve_skill`
- `read_skill`
- `execute_skill`

필요 패키지 설치:

```bash
pip install mcp
```

실행:

```bash
python adapters/mcp/uxr_mcp_server.py
```

MCP server config를 받는 agent에서는 `mcp_config.example.json`을 시작점으로 사용한다.

기본값으로 `execute_skill`은 dry-run 모드다. 팀에서 안전 실행 규칙을 합의한 뒤 자주 쓰는 스킬부터 실제 runner를 붙인다.
""",
        encoding="utf-8",
    )


def write_runtime(output_root: Path) -> None:
    runtime_root = output_root / "runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    runtime = r'''
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
'''.lstrip()
    (runtime_root / "resolve_skill.py").write_text(runtime, encoding="utf-8")

    updater = r'''
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
'''.lstrip()
    (runtime_root / "check_updates.py").write_text(updater, encoding="utf-8")

    batch = """@echo off
setlocal
if "%~1"=="" (
  echo Usage: update_cxi_skills.bat ^<latest-unpacked-cxi-skill-pack-folder^>
  exit /b 1
)
python "%~dp0runtime\\check_updates.py" --remote-pack "%~1" --apply
"""
    (output_root / "update_cxi_skills.bat").write_text(batch, encoding="utf-8")


def write_docs(output_root: Path, repo_root: Path) -> None:
    docs_root = output_root / "docs"
    docs_root.mkdir(parents=True, exist_ok=True)
    source_docs = {
        "install-guide-ko.md": repo_root / ".agents" / "skills" / "discovery-catalog" / "references" / "agent-adapter-install-guide.md",
        "distribution-architecture.md": repo_root / ".agents" / "skills" / "discovery-catalog" / "references" / "distribution-architecture.md",
        "mcp-execution-guide-ko.md": repo_root / ".agents" / "skills" / "discovery-catalog" / "references" / "mcp-execution-guide.md",
        "mcp-routing-contract.md": repo_root / ".agents" / "skills" / "discovery-catalog" / "references" / "mcp-routing-contract.md",
    }
    for output_name, source_path in source_docs.items():
        if source_path.exists():
            shutil.copy2(source_path, docs_root / output_name)


def write_root_readme(output_root: Path, skills: list[dict[str, Any]]) -> None:
    skill_lines = "\n".join(f"- `{skill['id']}`: {skill.get('description', '')}" for skill in skills)
    readme = f"""# CXI Skill Pack

이 repo는 CXI/UXR 팀이 여러 AI agent에서 같은 UX 리서치 스킬을 사용하기 위한 배포용 skill pack이다.

원본 스킬 개발과 검증은 `{SOURCE_REPO_NAME}` repo에서 진행한다. 이 repo에서는 배포 산출물만 관리하며, 스킬 내용을 직접 수정하지 않는 것을 원칙으로 한다.

## 빠른 시작

```bash
git clone {PUBLIC_REPO_URL}.git C:\\CXI\\cxi-skill-pack
cd C:\\CXI\\cxi-skill-pack
```

Codex에 설치:

```bat
adapters\\codex\\install_to_codex.bat
```

Claude 계열 slash command 생성:

```bat
adapters\\claude\\install_slash_commands.bat
```

ChatGPT Project 안내문 생성:

```bat
adapters\\chatgpt\\generate_project_instructions.bat
```

MCP starter 실행:

```bash
pip install -r adapters/mcp/requirements.txt
python adapters/mcp/uxr_mcp_server.py
```

## 업데이트

```bash
cd C:\\CXI\\cxi-skill-pack
git pull
```

agent가 별도 폴더로 복사 설치되어 있다면 `git pull` 후 해당 adapter를 한 번 더 실행한다.

## 주요 파일

- `manifest.json`: 배포된 스킬 목록과 fingerprint
- `skills/`: 실제 스킬 진입점 `SKILL.md`와 재사용 코드
- `adapters/`: Codex, Claude, ChatGPT, MCP 연결 도구
- `runtime/`: 자연어 요청을 스킬로 연결하거나 업데이트를 비교하는 공통 도구
- `docs/install-guide-ko.md`: 팀원용 한글 설치 가이드

## 포함 스킬

{skill_lines}
"""
    (output_root / "README.md").write_text(readme, encoding="utf-8")


def write_manifest(output_root: Path, repo_root: Path, skills: list[dict[str, Any]], zip_name: str | None) -> None:
    manifest = {
        "schemaVersion": "0.1.0",
        "packageName": PACKAGE_NAME,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "sourceRepo": str(repo_root),
        "sourceRepoName": SOURCE_REPO_NAME,
        "publicRepo": PUBLIC_REPO_URL,
        "canonicalSkillRoot": "skills",
        "directCommandPattern": "/{skill_id}",
        "naturalLanguageResolver": "runtime/resolve_skill.py",
        "skillCount": len(skills),
        "skills": skills,
        "adapters": {
            "slashCommands": "adapters/slash-commands/{skill_id}.md",
            "codexInstall": "adapters/codex/install_to_codex.py",
            "claudeSlashInstall": "adapters/claude/install_slash_commands.py",
            "chatgptProjectInstructions": "adapters/chatgpt/generate_project_instructions.py",
            "mcpServer": "adapters/mcp/uxr_mcp_server.py",
            "mcpContract": "docs/mcp-routing-contract.md",
        },
        "artifact": {
            "zip": zip_name,
        },
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def zip_dir(source_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source_dir.parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a downloadable CXI skill distribution bundle.")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--zip", action="store_true", help="Also create a .zip next to the output folder.")
    parser.add_argument("--clean", action="store_true", help="Replace generated files in an existing output repo while preserving .git.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve() if args.repo_root else find_repo_root(Path.cwd().resolve())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = args.output_dir.resolve() if args.output_dir else repo_root / "dist" / f"{PACKAGE_NAME}_{timestamp}"

    skills_root = repo_root / ".agents" / "skills"
    skills = scan_skills(skills_root)
    prepare_output_root(output_root, clean=args.clean)
    output_root.mkdir(parents=True, exist_ok=True)
    copy_skills(skills_root, output_root / "skills")
    write_adapter_files(output_root, skills)
    write_runtime(output_root)
    write_docs(output_root, repo_root)
    write_root_readme(output_root, skills)

    zip_name = output_root.with_suffix(".zip").name if args.zip else None
    write_manifest(output_root, repo_root, skills, zip_name)

    if args.zip:
        zip_path = output_root.with_suffix(".zip")
        zip_dir(output_root, zip_path)

    print(f"bundle={output_root}")
    print(f"skills={len(skills)}")
    if zip_name:
        print(f"zip={output_root.with_suffix('.zip')}")


if __name__ == "__main__":
    main()
