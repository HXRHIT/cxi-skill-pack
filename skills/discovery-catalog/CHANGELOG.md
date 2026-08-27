# Changelog — discovery-catalog

이 파일은 스킬의 동작 스키마(Skill.md)와 재사용 실행 코드(scripts/) 변경 이력을 관리한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다.
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/`에 변경이 생기면 항상 기록한다.

---

## 2026-08-27 — cxi-skill-pack 배포 repo 구조 반영

- 계기: 팀 배포용 GitHub repo `https://github.com/HXRHIT/cxi-skill-pack`가 생성되어 UXR-Template의 스킬 산출물을 배포 repo 구조로 정리해야 함
- 변경:
  - `build_distribution_bundle.py` 기본 package name을 `cxi-skill-pack`으로 전환
  - 배포 산출물에 root `README.md`, `docs/` 설치/운영 문서, `update_cxi_skills.bat`를 생성하도록 보강
  - 기존 배포 repo에 재생성할 수 있도록 `.git`은 보존하고 생성 산출물만 교체하는 `--clean` 옵션 추가
  - `distribution-architecture.md`, `agent-adapter-install-guide.md`의 repo명, 경로, 업데이트 명령을 `cxi-skill-pack` 기준으로 변경
- 검증: 이번 작업 후 catalog refresh와 배포 repo export를 수행 예정
- 남은 일: 1차 배포 스킬 묶음 확정 후 release note와 tag 운영 규칙을 추가할 수 있음

## 2026-08-27 — git repo 기반 업데이트 운영 가이드 추가

- 계기: UXR skill 공유폴더를 git repo로 두고 팀원이 `git pull`로 최신화하면 매번 zip을 다시 받을 필요가 없는지에 대한 운영 설명을 install guide에 반영
- 변경:
  - `references/agent-adapter-install-guide.md`에 git clone/git pull 기반 권장 운영 섹션 추가
  - zip 배포는 초기 테스트용 또는 git 사용이 어려운 팀원용 보조 방식으로 정리
  - agent가 repo를 직접 참조하는 방식과 복사 설치 후 adapter 재실행 방식의 차이를 명시
- 검증: 문서 변경. 스킬 reference 변경 규칙에 따라 catalog refresh 수행 예정
- 남은 일: 실제 팀 repo URL과 agent별 표준 설치 위치가 확정되면 예시 경로를 실경로로 교체

## 2026-08-27 — 설치 adapter 한글 가이드 추가

- 계기: 팀원이 Claude, ChatGPT, Codex, MCP에서 UXR skill pack을 어떻게 설치·연결하는지 한글로 쉽게 볼 수 있는 가이드가 필요함
- 변경:
  - `references/agent-adapter-install-guide.md` 신규 추가
  - `SKILL.md`와 `distribution-architecture.md`에서 한글 설치 가이드로 연결
  - `build_distribution_bundle.py`가 생성하는 adapter README, slash-command 안내문, ChatGPT project instructions 문구를 한글화
- 검증: 미실행. 다음 catalog refresh 시 최신 skill fingerprint와 generated metadata에 반영 필요
- 남은 일: 실제 agent별 설치 smoke test를 이어서 수행할 수 있음

## 2026-08-27 — MCP 실행 가이드 추가

- 계기: 팀원이 UXR skill pack을 MCP로 어떻게 호출하고 실행하면 되는지 쉽게 설명하는 별도 Markdown 가이드가 필요함
- 변경:
  - `references/mcp-execution-guide.md` 신규 추가
  - `resolve`/`execute` 2도구 구조, `/스킬명` 직접 호출, 자연어 라우팅, 위험 작업 dry-run 기준, 예시 payload를 쉬운 문체로 정리
  - `SKILL.md`에서 MCP 실행 가이드로 연결
- 검증: 이 항목 작성 후 quick validation과 catalog refresh를 수행할 예정
- 남은 일: 실제 MCP 서버 구현체가 생기면 도구명/설정 경로를 프로젝트 환경에 맞춰 보강

## 2026-08-27 — 팀 배포용 UXR skill pack 구조 추가

- 계기: UXR-Template의 스킬/코드를 팀원이 내려받아 Claude, ChatGPT, Codex 등 다양한 AI agent에서 `/스킬명` 또는 자연어 질의 기반으로 호출할 수 있게 하고 싶다는 요청 대응
- 변경:
  - `references/distribution-architecture.md` 신규 추가: canonical skill registry, manifest, agent adapter, natural-language resolver 구조 정의
  - `scripts/build_distribution_bundle.py` 신규 추가: `.agents/skills/*`를 portable `uxr-skill-pack` 폴더로 복사하고 `manifest.json`, slash command adapter, `runtime/resolve_skill.py`를 생성
  - skill folder fingerprint, Korean routing keywords, `runtime/check_updates.py`, `update_uxr_skills.bat` 추가
  - `SKILL.md`에 팀 배포 패키징 모드와 실행 명령 추가
- 검증:
  - `python -m py_compile .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py`
  - `python -X utf8 C:/Users/hanati/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/discovery-catalog`
  - `python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --zip --output-dir dist/uxr-skill-pack_test_v2`
  - zip 내부 `manifest.json`, `runtime/resolve_skill.py`, `runtime/check_updates.py`, `/app-review-analysis-pipeline` slash adapter 존재 확인
  - `/app-review-analysis-pipeline`, `앱 리뷰 분석해줘`, `전사본 개인정보 익명화해줘` resolver smoke test 통과
  - 설치본/원격본 시뮬레이션에서 `app-review-analysis-pipeline` 변경 감지 → `--apply` 후 변경 없음 상태 확인
- 남은 일: agent별 실제 설치 방식(Codex/Claude/ChatGPT/MCP)의 세부 adapter 파일을 더 정교화해야 함

## 2026-08-27 — 스킬 변경 후 자동 catalog refresh 규칙 추가

- 계기: 다른 스킬을 업데이트하면 #33 discovery catalog도 자동으로 최신 상태가 되도록 해야 한다는 요청 대응
- 변경:
  - `AGENTS.md`에 `.agents/skills/*` 변경 후 `discovery-catalog/scripts/refresh_catalog.py` 실행 규칙 추가
  - `SKILL.md`와 `references/catalog-maintenance.md`에 같은 자동 refresh 운영 규칙 반영
  - 기존 website generator의 hard-coded 날짜를 `date.today()`로 변경
  - `catalog_sync_report.json`에 skill별 `SKILL.md` fingerprint를 기록하도록 `refresh_catalog.py` 보강
- 검증:
  - `python -m py_compile .agents/skills/discovery-catalog/scripts/refresh_catalog.py website/scripts/build_catalog_generated_data.py`
  - `python -X utf8 C:/Users/hanati/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/discovery-catalog`
  - `python .agents/skills/discovery-catalog/scripts/refresh_catalog.py`
  - 생성 결과: ideas 47건, skills 22건, template pairs 13건, sync warnings 0건
- 남은 일: generated snapshot과 overlay drift 경고를 더 정교화할 수 있음

## 2026-08-27 — #33 discovery-catalog 스킬 초안 작성

- 계기: 여러 AI agent와 MCP-like 호출면에서 같은 UXR 스킬을 일관되게 찾고, 다른 agent가 먼저 작업한 파일을 중복 수정하지 않도록 운영 진입점이 필요함
- 변경:
  - `.agents/skills/discovery-catalog/SKILL.md` 신규 작성
  - MCP-style `resolve`/`execute` 라우팅 계약을 `references/mcp-routing-contract.md`로 분리
  - 기존 `website/scripts/build_catalog_generated_data.py`를 복제하지 않고 감싸는 `scripts/refresh_catalog.py` 추가
  - generated base + curated overlay + render layer 유지보수 규칙을 `references/catalog-maintenance.md`로 분리
- 검증: 미실행. 이번 턴은 시작 범위로 스킬 파일과 wrapper 초안만 작성했으며, 사용자가 요청하면 quick validation과 실제 catalog refresh를 별도 수행한다.
- 남은 일: master log의 #33 상태를 D로 이동하고, `website/data/generated/catalog_sync_report.json` 생성 테스트 및 website fallback 축소 범위를 결정해야 한다.
