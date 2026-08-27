# cxi-skill-pack v0.1 Release Notes

## 요약

`cxi-skill-pack` v0.1은 CXI/UXR 팀이 Claude, ChatGPT, Codex, MCP 계열 agent에서 같은 UX 리서치 스킬을 일관되게 호출하기 위한 첫 배포 버전입니다.

이번 버전의 핵심은 다음과 같습니다.

- `UXR-Template`에서 만든 canonical skill을 배포용 repo로 분리
- 팀원이 `git clone` 또는 `git pull`로 최신 스킬팩을 받을 수 있는 구조 제공
- Codex, Claude 계열 slash command, ChatGPT Project, MCP starter adapter 포함
- 자연어 요청을 canonical skill ID로 연결하는 `runtime/resolve_skill.py` 포함
- skill readiness audit와 v0.1 release candidate report 포함
- 공식 배포 추천 스킬 15개, 파일럿 스킬 8개 포함

## 설치

권장 설치 방식은 git clone입니다.

```bash
git clone https://github.com/HXRHIT/cxi-skill-pack.git C:\CXI\cxi-skill-pack
cd C:\CXI\cxi-skill-pack
```

Codex에 설치:

```bat
adapters\codex\install_to_codex.bat
```

Claude 계열 slash command 생성:

```bat
adapters\claude\install_slash_commands.bat
```

ChatGPT Project 안내문 생성:

```bat
adapters\chatgpt\generate_project_instructions.bat
```

MCP starter 실행:

```bash
pip install -r adapters/mcp/requirements.txt
python adapters/mcp/uxr_mcp_server.py
```

자세한 설치 방법은 `docs/install-guide-ko.md`를 참고하세요.

## 사용 방법

스킬명을 아는 경우 직접 호출합니다.

```text
/app-review-analysis-pipeline 하나1Q 앱 리뷰 분석해줘
```

스킬명을 모르는 경우 자연어로 요청하면 agent 또는 MCP가 `manifest.json`과 resolver를 기준으로 적절한 스킬을 찾습니다.

```text
앱 리뷰 분석해서 대시보드 만들어줘
```

## v0.1 공식 배포 추천 스킬

다음 15개 스킬은 v0.1에서 우선 배포 추천 대상으로 분류되었습니다.

- `app-review-analysis-pipeline`
- `transcript-verification-enhancer`
- `transcript-anonymizer-skill`
- `discovery-catalog`
- `survey-basic-stats-analysis`
- `survey-data-preprocessing`
- `survey-analysis-verification`
- `survey-results-dashboard`
- `survey-open-ended-coding-skill`
- `qual-thematic-coding-skill`
- `research-qa-skill`
- `interview-results-dashboard`
- `recruiting-list-legend-generator`
- `research-plan-writer-skill`
- `survey-interim-report-writer`

## v0.1 파일럿 스킬

다음 8개 스킬은 포함되어 있지만, 팀 내부 파일럿 또는 추가 검토 후 공식 사용을 권장합니다.

- `template-hygiene-checker`
- `coding-sheet-generator`
- `executive-one-pager-skill`
- `interview-quant-coding-skill`
- `persona-generator-skill`
- `transcript-pipeline-skill`
- `followup-implementation-tracker`
- `interview-interim-report-writer`

## 포함된 주요 구성

- `manifest.json`: 스킬 목록, entrypoint, command, fingerprint metadata
- `skills/`: 실제 `SKILL.md`, references, scripts
- `adapters/codex/`: Codex personal skills 설치 도구
- `adapters/claude/`: Claude 계열 slash command 생성 도구
- `adapters/chatgpt/`: ChatGPT Project instructions 생성 도구
- `adapters/mcp/`: MCP starter server
- `runtime/resolve_skill.py`: 자연어 요청을 skill ID로 resolve
- `runtime/check_updates.py`: 설치본과 최신 pack의 fingerprint 비교
- `docs/skill-readiness-audit.md`: 스킬 최소 기준 자동 점검 결과
- `docs/release-candidates-v0.1.md`: v0.1 배포 후보 추천 리포트
- `docs/release-policy.md`: 배포 기준과 승인 원칙

## 업데이트 방법

스킬팩을 git으로 받은 팀원은 아래 명령으로 최신화합니다.

```bash
cd C:\CXI\cxi-skill-pack
git pull
```

agent가 repo를 직접 바라보는 구조라면 여기서 끝입니다.

Codex처럼 별도 폴더로 복사 설치한 경우에는 `git pull` 후 adapter를 다시 실행합니다.

```bat
adapters\codex\install_to_codex.bat
```

## 안전 기준

다음 작업은 자동 실행하지 말고 먼저 사용자 확인 또는 dry-run을 권장합니다.

- 원본 파일을 수정하는 작업
- 개인정보 또는 참여자 데이터가 포함된 파일 처리
- 외부 API 또는 유료 서비스 호출
- 파일 삭제, 이동, 덮어쓰기
- 어떤 스킬을 써야 할지 후보가 여러 개인 경우
- 다른 AI agent가 같은 파일을 작업 중일 가능성이 있는 경우

## 알려진 한계

- MCP adapter는 starter 구현입니다. 기본 `execute_skill`은 안전을 위해 dry-run 중심으로 동작합니다.
- 일부 스킬은 파일럿 lane으로 분류되어 있으며, 실제 프로젝트 적용 후 threshold와 release lane을 조정할 수 있습니다.
- 스킬 원본 수정은 `UXR-Template`에서 진행하고, `cxi-skill-pack`에서는 직접 수정하지 않는 운영을 권장합니다.

## 운영자용 참고

`UXR-Template`에서 다음 명령으로 v0.1 리포트와 배포본을 다시 생성할 수 있습니다.

```bash
python .agents/skills/discovery-catalog/scripts/refresh_catalog.py
python .agents/skills/discovery-catalog/scripts/audit_skill_readiness.py
python .agents/skills/discovery-catalog/scripts/select_release_candidates.py --version v0.1
python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --output-dir C:\Users\hanati\Documents\GitHub\cxi-skill-pack --clean
```

공식 배포 전에는 `docs/skill-readiness-audit.md`와 `docs/release-candidates-v0.1.md`를 확인한 뒤 tag를 붙입니다.
