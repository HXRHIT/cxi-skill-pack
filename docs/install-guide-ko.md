# CXI Skill Pack 설치 어댑터 한글 가이드

이 문서는 팀원이 `cxi-skill-pack`을 받아서 Claude, ChatGPT, Codex, MCP에서 어떻게 연결하면 되는지 쉽게 설명한다.

핵심은 하나다.

스킬 원본은 `skills/` 폴더에 한 번만 있고, 각 AI agent는 자기 방식에 맞는 adapter로 그 스킬을 읽는다.

## 먼저 할 일

권장 방식은 `git repo`로 받는 것이다.

1. 팀 공용 CXI skill pack repo를 `git clone`한다.
2. repo 안에 `manifest.json` 또는 `.agents/skills/`가 있는지 확인한다.
3. 본인이 쓰는 AI agent에 맞는 adapter를 실행하거나 설정한다.
4. 이후 업데이트는 새 zip 다운로드가 아니라 `git pull`로 한다.

예시:

```bash
git clone https://github.com/HXRHIT/cxi-skill-pack.git C:\CXI\cxi-skill-pack
cd C:\CXI\cxi-skill-pack
git pull
```

zip도 사용할 수 있지만, zip은 초기 테스트용 또는 git을 쓰기 어려운 팀원용으로 보는 편이 좋다.

zip을 쓰는 경우:

1. 팀 공유 위치에서 `cxi-skill-pack_*.zip`을 받는다.
2. 원하는 폴더에 압축을 푼다.
3. 압축을 푼 폴더 안에 `manifest.json`이 있는지 확인한다.
4. 본인이 쓰는 AI agent에 맞는 adapter를 실행하거나 설정한다.

폴더 예시:

```text
C:\CXI\cxi-skill-pack
```

## 권장 운영: git repo를 공유 원본으로 쓰기

팀에서 계속 개선되는 스킬을 쓰려면 `cxi-skill-pack.zip`을 매번 다시 받는 방식보다 git repo 방식이 좋다.

권장 구조:

```text
팀 공용 git repo = 최신 배포본
각 사용자 PC = git clone 받은 로컬 사본
업데이트 = git pull
AI agent = 로컬 repo의 manifest/SKILL.md 참조
```

이렇게 하면 스킬 내용이 바뀔 때마다 새 파일을 다시 다운로드하지 않아도 된다.

팀원은 보통 아래만 하면 된다.

```bash
cd C:\CXI\cxi-skill-pack
git pull
```

단, AI agent가 스킬을 “복사해서 설치”하는 방식이면 `git pull`만으로는 agent 내부 설치 폴더까지 자동 갱신되지 않을 수 있다.

이 경우에는 둘 중 하나를 선택한다.

1. agent가 git repo 경로를 직접 바라보게 한다.
2. `git pull` 후 설치 adapter를 한 번 더 실행한다.

추천은 1번이다.

복사본을 줄여야 “어디가 최신인지” 헷갈리지 않는다.

다만 Codex처럼 개인 skill 폴더에 복사해 쓰는 방식이 편한 경우에는 아래 흐름을 쓴다.

```bash
cd C:\CXI\cxi-skill-pack
git pull
adapters\codex\install_to_codex.bat
```

## 폴더 구조

```text
cxi-skill-pack/
├─ manifest.json
├─ update_cxi_skills.bat
├─ README.md
├─ docs/
├─ skills/
├─ adapters/
│  ├─ codex/
│  ├─ claude/
│  ├─ chatgpt/
│  └─ mcp/
└─ runtime/
```

각 폴더의 의미:

- `manifest.json`: 어떤 스킬이 있는지 적힌 목록
- `skills/`: 실제 스킬 설명과 실행 코드
- `adapters/`: AI agent별 설치 도구
- `runtime/`: 자연어 요청을 스킬로 연결하는 공통 실행 도구
- `docs/`: 설치 가이드와 MCP 실행 가이드
- `update_cxi_skills.bat`: 나중에 스킬을 업데이트할 때 쓰는 도구

## Codex에서 쓰기

Codex는 스킬 폴더를 개인 skill 위치로 복사해서 쓰는 방식이 가장 단순하다.

압축을 푼 폴더에서 실행:

```bat
adapters\codex\install_to_codex.bat
```

이 명령은 `skills/` 안의 스킬들을 Codex 개인 스킬 폴더로 복사한다.

기본 복사 위치:

- `CODEX_HOME`이 있으면 `%CODEX_HOME%\skills`
- 없으면 `~\.codex\skills`

다른 위치에 설치하고 싶으면:

```bat
adapters\codex\install_to_codex.bat --target C:\원하는\skills\폴더
```

설치 후:

1. Codex를 새로 열거나 새 task를 시작한다.
2. 사용자가 `/app-review`처럼 짧은 스킬명을 직접 말하거나, “앱 리뷰 분석해줘”처럼 자연어로 요청한다.
3. Codex가 해당 `SKILL.md`를 읽고 작업한다.

## Claude 계열 agent에서 쓰기

Claude Code처럼 custom slash command 폴더를 지원하는 agent라면 command 파일을 만들어 연결한다.

압축을 푼 폴더에서 실행:

```bat
adapters\claude\install_slash_commands.bat
```

기본 생성 위치:

```text
~\.claude\commands\uxr
```

다른 위치에 만들고 싶으면:

```bat
adapters\claude\install_slash_commands.bat --commands-dir C:\원하는\commands\uxr
```

생성되는 command 파일은 실제 스킬 내용을 복사하지 않는다.

대신 clone 또는 압축 해제한 `cxi-skill-pack/skills/{skill_id}/SKILL.md`를 읽으라고 안내한다.

예시 사용:

```text
/uxr:app-review 하나1Q 앱 리뷰 분석해줘
```

실제 slash command 표기 방식은 사용하는 Claude 계열 도구의 규칙에 따라 조금 다를 수 있다.

## ChatGPT 계열 agent에서 쓰기

ChatGPT 계열은 로컬 slash command 설치 방식이 agent마다 다를 수 있다.

그래서 먼저 project/custom GPT에 넣을 안내문을 생성한다.

압축을 푼 폴더에서 실행:

```bat
adapters\chatgpt\generate_project_instructions.bat
```

생성 위치:

```text
adapters\chatgpt\generated\CHATGPT_PROJECT_INSTRUCTIONS.md
```

사용 방법:

1. 생성된 `CHATGPT_PROJECT_INSTRUCTIONS.md` 내용을 연다.
2. ChatGPT Project 또는 Custom GPT instructions에 붙인다.
3. `cxi-skill-pack` 폴더를 ChatGPT가 직접 읽을 수 없다면 MCP 서버를 함께 연결한다.
4. 사용자는 `/스킬명` 또는 자연어로 요청한다.

중요:

ChatGPT가 로컬 파일을 직접 읽을 수 없는 환경에서는, 안내문만으로 실제 코드를 실행할 수 없다. 이 경우 MCP adapter를 같이 쓰는 편이 좋다.

## MCP로 연결해서 쓰기

MCP는 여러 AI agent가 같은 skill pack을 호출하게 해주는 공통 리모컨이다.

MCP starter 서버 위치:

```text
adapters\mcp\uxr_mcp_server.py
```

필요 패키지 설치:

```bash
pip install mcp
```

서버 실행:

```bash
python adapters/mcp/uxr_mcp_server.py
```

MCP 설정 예시는 여기에 있다:

```text
adapters\mcp\mcp_config.example.json
```

MCP starter가 제공하는 도구:

- `resolve_skill`: 사용자 요청에 맞는 스킬 찾기
- `read_skill`: 특정 스킬의 `SKILL.md` 읽기
- `execute_skill`: 실행 준비. 기본값은 안전을 위해 `dry_run`

처음에는 `execute_skill`이 바로 파일을 고치지 않는다.

먼저 “어떤 스킬을 어떤 입력으로 실행할지”를 반환하고, 팀에서 자주 쓰는 스킬부터 실제 runner를 붙이면 된다.

## 자연어 요청은 어떻게 연결되나

사용자가 이렇게 말할 수 있다.

```text
앱 리뷰 분석해서 대시보드 만들어줘
```

agent 또는 MCP는 내부적으로 이렇게 실행한다.

```bash
python runtime/resolve_skill.py "앱 리뷰 분석해서 대시보드 만들어줘" --manifest manifest.json
```

예상 결과:

```json
{
  "resolved_skill_id": "app-review-analysis-pipeline",
  "command": "/app-review",
  "next": "execute"
}
```

즉 사용자가 스킬 이름을 몰라도 된다.

## 직접 스킬명을 아는 경우

스킬명을 아는 사람은 바로 이렇게 요청하면 된다.

```text
/app-review 하나1Q 앱 리뷰 분석해줘
```

팀원이 직접 입력할 때는 짧은 명령을 우선 사용한다. 내부 canonical skill ID는 `skills/` 폴더명과 같고, 로그와 리포트에는 함께 남긴다.

예시:

- `/app-review` → `app-review-analysis-pipeline`
- `/transcript-pii` → `transcript-anonymizer-skill`
- `/survey-stats` → `survey-basic-stats-analysis`
- `research-qa-skill`

## 업데이트 방법

처음 설치 후에는 매번 새 zip을 다시 받을 필요가 없다.

가장 쉬운 방식은 git repo를 최신화하는 것이다.

```bash
cd C:\CXI\cxi-skill-pack
git pull
```

agent가 이 repo를 직접 바라보면 여기서 끝이다.

agent가 별도 폴더로 복사 설치되어 있다면, `git pull` 후 해당 adapter를 다시 실행한다.

Codex 예시:

```bat
adapters\codex\install_to_codex.bat
```

이전 설치 때문에 긴 스킬명과 짧은 스킬명이 같이 보이면 아래처럼 legacy 폴더를 정리한다.

```bat
adapters\codex\install_to_codex.bat --remove-legacy
```

자세한 내용은 `docs/codex-duplicate-skill-cleanup-guide.md`를 참고한다.

zip 기반 업데이트도 가능하다.

최신 pack 폴더가 공유 드라이브나 repo clone 위치에 있다면:

```bat
update_cxi_skills.bat C:\공유폴더\latest-cxi-skill-pack
```

또는:

```bash
python runtime/check_updates.py --remote-pack C:/공유폴더/latest-cxi-skill-pack --apply
```

이 명령은 바뀐 스킬만 비교해서 업데이트한다.

삭제된 스킬은 자동 삭제하지 않고 보고만 한다. 실수로 팀원 환경에서 파일이 사라지는 것을 막기 위해서다.

## 실행 전에 꼭 확인할 것

바로 실행하지 말고 사용자 확인이 필요한 경우:

- 원본 파일을 수정해야 할 때
- 개인정보/참여자 데이터가 포함된 파일을 다룰 때
- 외부 API나 유료 서비스를 호출할 때
- 어떤 스킬을 써야 할지 후보가 여러 개일 때
- 파일 삭제, 이동, 덮어쓰기가 포함될 때
- 다른 AI agent가 같은 파일을 작업 중일 수 있을 때

이런 경우에는 먼저 `dry_run`으로 보여준다.

## 팀원에게 안내할 가장 짧은 버전

1. `cxi-skill-pack` git repo를 `clone`한다.
2. 본인 agent에 맞는 adapter를 실행한다.
3. 업데이트할 때는 `git pull`을 한다.
4. agent가 복사 설치 방식이면 adapter를 한 번 더 실행한다.
5. 스킬명을 알면 짧은 `/스킬명`으로 부른다.
6. 스킬명을 모르면 그냥 자연어로 말한다.
7. 민감하거나 위험한 작업은 실행 전에 확인한다.

## 운영자가 배포할 때 할 일

cxi-template repo에서:

```bash
python .agents/skills/discovery-catalog/scripts/refresh_catalog.py
python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --output-dir C:\Users\hanati\Documents\GitHub\cxi-skill-pack --clean
```

운영 방식은 두 가지다.

권장 방식:

1. `cxi-skill-pack` repo에 변경사항을 반영한다.
2. 팀원은 각자 `git pull`로 최신화한다.

보조 방식:

1. 생성된 `dist/cxi-skill-pack_*.zip`을 팀에 공유한다.
2. git을 쓰기 어려운 팀원은 zip을 내려받아 압축을 푼다.

스킬이 바뀌면:

1. 스킬 원본을 수정한다.
2. `refresh_catalog.py`를 실행한다.
3. git repo에 변경사항을 반영한다.
4. 팀원은 `git pull`로 갱신한다.
5. zip 배포가 필요할 때만 새 bundle을 만든다.
6. zip 설치 팀원은 `update_cxi_skills.bat` 또는 `runtime/check_updates.py --apply`로 갱신한다.
