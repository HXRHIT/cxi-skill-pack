# UXR 스킬을 MCP로 실행하는 쉬운 가이드

이 문서는 팀원이 Claude, ChatGPT, Codex 같은 AI agent에서 cxi-template 스킬을 MCP로 호출할 때의 기본 사용법을 설명한다.

핵심은 간단하다.

MCP는 AI agent와 UXR 스킬팩 사이의 리모컨이다.

사용자는 자연어로 요청하고, MCP는 어떤 스킬을 쓸지 찾은 뒤, 필요한 경우 해당 스킬의 코드를 실행한다.

## 한 줄 요약

MCP에는 최소한 도구 2개만 있으면 된다.

- `uxr.resolve_skill`: 사용자 요청을 보고 어떤 스킬을 쓸지 찾는다.
- `uxr.execute_skill`: 확정된 스킬을 실제로 실행한다.

처음부터 바로 실행하지 말고, 보통은 `resolve`를 먼저 한다.

## 전체 흐름

1. 팀원이 `uxr-skill-pack`을 설치하거나 공유 폴더에 둔다.
2. MCP 서버가 `uxr-skill-pack/manifest.json` 위치를 알고 있어야 한다.
3. 사용자가 AI agent에게 “앱 리뷰 분석해줘”처럼 요청한다.
4. AI agent 또는 MCP가 `uxr.resolve_skill`을 호출한다.
5. 결과가 1개로 확정되면 `resolved_skill_id`를 확인한다.
6. 입력값이 충분하고 위험한 작업이 아니면 `uxr.execute_skill`을 호출한다.
7. 파일 쓰기, 외부 API, 개인정보 처리, 모호한 후보가 있으면 사용자에게 먼저 확인한다.

## 직접 호출 방식

사용자가 스킬명을 정확히 알고 있으면 `/스킬명`으로 호출한다.

예시:

```text
/app-review-analysis-pipeline 하나1Q 앱 리뷰를 2026-03-01부터 2026-08-27까지 분석해줘
```

MCP 요청 예시:

```json
{
  "action": "resolve",
  "skill_id": "app-review-analysis-pipeline",
  "query": "하나1Q 앱 리뷰를 2026-03-01부터 2026-08-27까지 분석해줘"
}
```

기대 결과:

```json
{
  "resolved_skill_id": "app-review-analysis-pipeline",
  "reason": "skill_id가 canonical ID와 일치합니다.",
  "required_inputs": ["app_name", "from_date", "to_date", "store app id"],
  "estimated_outputs": ["Excel", "CSV", "HTML dashboard"],
  "risk_level": "medium",
  "next": "execute"
}
```

## 자연어 호출 방식

사용자가 스킬명을 몰라도 된다.

예시:

```text
하나1Q 앱 리뷰 긁어서 좋은 점/나쁜 점이랑 평점 추세 대시보드로 보여줘
```

MCP 요청 예시:

```json
{
  "action": "resolve",
  "query": "하나1Q 앱 리뷰 긁어서 좋은 점/나쁜 점이랑 평점 추세 대시보드로 보여줘",
  "artifact_type": "app_review",
  "goal": "analyze"
}
```

기대 결과:

```json
{
  "resolved_skill_id": "app-review-analysis-pipeline",
  "reason": "앱 리뷰, 평점, 대시보드 요청이 app-review-analysis-pipeline과 가장 잘 맞습니다.",
  "required_inputs": ["앱 이름", "수집 기간", "스토어 앱 ID 또는 후보 확인"],
  "estimated_outputs": ["app_review_analysis_*.xlsx", "dashboard_*.html"],
  "risk_level": "medium",
  "next": "execute"
}
```

## MCP 도구 1: `uxr.resolve_skill`

이 도구는 실행하지 않고 “어떤 스킬이 맞는지”만 찾는다.

권장 입력:

```json
{
  "query": "사용자 요청 원문",
  "skill_id": "선택: 정확한 스킬 ID를 아는 경우",
  "stage": "선택: 01|02|03|04|05|06|PLATFORM|CROSS|UTIL",
  "artifact_type": "선택: interview|survey|transcript|template|recruiting|dashboard|report|app_review|unknown",
  "goal": "선택: prepare|collect|analyze|synthesize|verify|distribute|maintain",
  "inputs": {
    "project_code": "선택",
    "files": ["선택 파일 경로"]
  }
}
```

권장 출력:

```json
{
  "resolved_skill_id": "canonical skill id 또는 null",
  "candidates": [],
  "reason": "왜 이 스킬인지",
  "required_inputs": [],
  "estimated_outputs": [],
  "risk_level": "low|medium|high",
  "next": "execute|ask_user|dry_run|not_available"
}
```

## MCP 도구 2: `uxr.execute_skill`

이 도구는 확정된 스킬을 실행한다.

권장 입력:

```json
{
  "skill_id": "app-review-analysis-pipeline",
  "query": "사용자 요청 원문",
  "inputs": {
    "app_name": "하나1Q",
    "from_date": "2026-03-01",
    "to_date": "2026-08-27",
    "google_play_app_id": "com.hanabank.oqf",
    "app_store_app_id": "6743190232",
    "output_dir": "outputs/hana1q_app_review"
  },
  "runner": "prompt"
}
```

권장 출력:

```json
{
  "execution_id": "20260827-001",
  "skill_id": "app-review-analysis-pipeline",
  "status": "completed",
  "artifact_paths": [
    "outputs/hana1q_app_review/app_review_analysis_하나1Q.xlsx",
    "outputs/hana1q_app_review/dashboard_하나1Q.html"
  ],
  "log_path": "outputs/hana1q_app_review/run_log.json",
  "fallback": null
}
```

## MCP 서버가 내부에서 하는 일

`resolve`는 `manifest.json`을 읽고 가장 맞는 스킬을 고른다.

로컬 스킬팩을 쓰는 경우, MCP 서버는 아래처럼 resolver를 호출할 수 있다.

```bash
python runtime/resolve_skill.py "앱 리뷰 분석해줘" --manifest manifest.json
```

`execute`는 다음 순서로 동작한다.

1. `skills/{skill_id}/SKILL.md`를 읽는다.
2. 해당 스킬이 요구하는 reference나 script를 확인한다.
3. 입력값이 부족하면 사용자에게 묻는다.
4. 실행이 안전하면 script를 실행하거나 산출물을 만든다.
5. 결과 파일 경로와 로그를 반환한다.

## 바로 실행하면 안 되는 경우

아래 경우에는 `execute` 대신 `dry_run`이나 사용자 확인을 먼저 반환한다.

- 후보 스킬이 2개 이상으로 애매할 때
- 실제 프로젝트 원본 파일을 수정해야 할 때
- 개인정보 익명화처럼 되돌리기 어려운 처리가 있을 때
- 외부 API나 유료 서비스를 호출해야 할 때
- 다른 AI agent가 같은 파일을 작업 중일 수 있을 때
- 삭제, 이동, 덮어쓰기 같은 위험 작업이 포함될 때

## 예시 1: 앱 리뷰 분석

사용자 요청:

```text
하나1Q 앱 리뷰를 2026년 3월부터 8월까지 긁어서 대시보드로 보여줘
```

1차 호출:

```json
{
  "action": "resolve",
  "query": "하나1Q 앱 리뷰를 2026년 3월부터 8월까지 긁어서 대시보드로 보여줘",
  "artifact_type": "app_review",
  "goal": "analyze"
}
```

resolve 결과:

```json
{
  "resolved_skill_id": "app-review-analysis-pipeline",
  "risk_level": "medium",
  "next": "execute"
}
```

2차 호출:

```json
{
  "action": "execute",
  "skill_id": "app-review-analysis-pipeline",
  "inputs": {
    "app_name": "하나1Q",
    "from_date": "2026-03-01",
    "to_date": "2026-08-27",
    "google_play_app_id": "com.hanabank.oqf",
    "app_store_app_id": "6743190232"
  },
  "runner": "prompt"
}
```

## 예시 2: 전사본 익명화

사용자 요청:

```text
이 인터뷰 전사본에서 개인정보 마스킹해줘
```

1차 호출:

```json
{
  "action": "resolve",
  "query": "이 인터뷰 전사본에서 개인정보 마스킹해줘",
  "artifact_type": "transcript",
  "goal": "verify"
}
```

resolve 결과:

```json
{
  "resolved_skill_id": "transcript-anonymizer-skill",
  "risk_level": "high",
  "next": "dry_run"
}
```

이 경우에는 바로 원본을 바꾸면 안 된다.

먼저 탐지 리포트와 치환 계획을 보여주고, 사용자가 승인하면 사본에 적용한다.

## 팀원이 기억할 규칙

- 스킬명을 알면 `/스킬명`으로 시작한다.
- 스킬명을 모르면 그냥 자연어로 요청한다.
- MCP는 먼저 `resolve`로 맞는 스킬을 찾는다.
- 파일을 쓰거나 민감한 데이터를 다루면 실행 전에 사용자 확인을 받는다.
- 실행 결과는 항상 파일 경로와 로그 경로로 돌려준다.
- canonical skill ID는 `.agents/skills/{skill_id}` 폴더명과 같아야 한다.

## 운영자 체크리스트

- `uxr-skill-pack/manifest.json` 경로가 MCP 서버 설정에 들어가 있는가?
- `runtime/resolve_skill.py`가 실행되는가?
- `skills/{skill_id}/SKILL.md`를 MCP 서버가 읽을 수 있는가?
- script 실행이 필요한 스킬에서 Python/Node 의존성이 준비되어 있는가?
- `execute`가 원본 파일을 바로 수정하지 않도록 안전장치가 있는가?
- 업데이트 후 `runtime/check_updates.py` 또는 `update_uxr_skills.bat`로 최신화할 수 있는가?

## 최소 구현 예시

MCP 서버를 아주 단순하게 시작한다면 아래 정도면 된다.

```python
from pathlib import Path
import json
import subprocess

PACK_ROOT = Path("C:/path/to/uxr-skill-pack")
MANIFEST = PACK_ROOT / "manifest.json"


def resolve_skill(query: str) -> dict:
    result = subprocess.run(
        ["python", str(PACK_ROOT / "runtime" / "resolve_skill.py"), query, "--manifest", str(MANIFEST)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


def execute_skill(skill_id: str, inputs: dict) -> dict:
    skill_md = PACK_ROOT / "skills" / skill_id / "SKILL.md"
    if not skill_md.exists():
        return {"status": "failed", "reason": "Unknown skill_id"}
    return {
        "status": "dry_run",
        "skill_id": skill_id,
        "next": "Load SKILL.md, check required inputs, then run the skill-specific script with user approval.",
        "skill_path": str(skill_md),
        "inputs": inputs,
    }
```

처음에는 `execute_skill`을 바로 자동 실행으로 만들지 말고 `dry_run`으로 시작하는 편이 안전하다. 팀에서 자주 쓰는 스킬부터 하나씩 실제 실행 runner를 붙이면 된다.
