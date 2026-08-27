# CXI skill pack release policy

이 문서는 `cxi-template`에서 만든 스킬을 `cxi-skill-pack`으로 1차 배포할 때 적용하는 최소 기준과 후보 선정 규칙이다.

## 기본 원칙

- AI는 catalog 갱신, 최소 기준 검사, 배포 후보 추천까지 자동 수행한다.
- 공식 배포 확정은 사람이 승인한다.
- `cxi-template/.agents/skills/*`가 원본이고, `cxi-skill-pack/skills/*`는 배포 산출물이다.
- 배포 repo에서 직접 스킬 내용을 수정하지 않는다.
- 민감정보, 원천데이터, 프로젝트별 산출물은 skill pack에 넣지 않는다.

## 최소 기준

스킬이 1차 배포 후보가 되려면 최소한 아래를 만족해야 한다.

- `SKILL.md`가 있어야 한다.
- `SKILL.md` frontmatter에 `name`과 `description`이 있어야 한다.
- description은 어떤 요청에서 호출되는지 이해할 수 있을 만큼 충분히 구체적이어야 한다.
- 본문에는 입력, 동작 순서, 출력, 안전 경계가 드러나야 한다.
- `CHANGELOG.md`가 있어야 한다.
- 참조한 local markdown link는 깨지면 안 된다.
- `references/` 또는 `scripts/`를 언급했다면 실제 파일이 있어야 한다.
- placeholder, TODO, 임시 설명이 남아 있으면 보류 또는 검토 대상으로 둔다.
- 이메일, 전화번호, 주민등록번호처럼 보이는 값이 있으면 사람이 확인하기 전까지 보류한다.
- native 원천데이터 경로나 내부 자료 원문이 들어간 경우 배포 전 확인한다.

## 배포 lane

`audit_skill_readiness.py`는 각 스킬을 아래 세 단계로 나눈다.

- `A_READY`: 최소 기준을 통과했고 1차 배포 후보로 추천 가능
- `B_REVIEW`: 실행 가능성은 있으나 문서, 검증, 설명 보강 후 배포 권장
- `C_HOLD`: 깨진 링크, 필수 메타데이터 누락, 민감정보 의심 등으로 보류

`select_release_candidates.py`는 audit 결과를 바탕으로 아래 묶음을 만든다.

- `recommendedRelease`: 1차 공식 배포 추천
- `pilotOnly`: 내부 파일럿 사용 추천
- `hold`: 배포 보류

## 1차 배포 우선순위

첫 배포는 팀원이 바로 체감할 수 있고, 위험이 낮거나 통제가 쉬운 스킬부터 포함한다.

- catalog/routing 계열
- 템플릿 위생 검사
- 질문지 QA
- 앱 리뷰 분석
- 전사본 검증/익명화
- 설문 전처리/기초통계/검증/대시보드
- 정성 코딩 및 인터뷰 대시보드

보고서 작성, 페르소나, 후속조치 추적처럼 산출물 해석 책임이 큰 스킬은 pilot lane에서 먼저 운영할 수 있다.

## 실행 명령

```bash
python .agents/skills/discovery-catalog/scripts/refresh_catalog.py
python .agents/skills/discovery-catalog/scripts/audit_skill_readiness.py
python .agents/skills/discovery-catalog/scripts/select_release_candidates.py --version v0.1
python .agents/skills/discovery-catalog/scripts/build_distribution_bundle.py --output-dir C:\Users\hanati\Documents\GitHub\cxi-skill-pack --clean
```

## 승인 기준

공식 배포 전 사람이 확인할 것:

- `website/data/generated/skill_readiness_audit.md`
- `website/data/generated/release_candidates_v0.1.md`
- `cxi-skill-pack/README.md`
- `cxi-skill-pack/manifest.json`

승인 후 `cxi-skill-pack` repo에 commit/push한다.
