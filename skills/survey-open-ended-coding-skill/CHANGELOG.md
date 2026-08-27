# Changelog — survey-open-ended-coding-skill

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다. 목적: AI 에이전트와 대화하며 스킬을 반복 수정할 때, ①무엇을 왜 바꿨는지 ②그 변경이 어느 validation_runs 세션에서 검증됐는지를 다음 세션(사람이든 다른 에이전트든)이 바로 이어받을 수 있게 하는 것.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 (2차) — canonical 스크립트 실제 재실행 검증, 버그 3건 발견·수정

- 계기: "다음 검증" 요청으로 promoted-but-untested 스킬(#19/#38/#43) 순서 중 #38을 실제 실행. 이전 항목(소급 승격)에서는 파일만 복사하고 실행하지 않았었음.
- 발견·수정한 버그 3건(전부 "복사만 하고 안 돌려봤으면 몰랐을" 문제):
  1. 스크립트 파일 위치 기준 상대경로로 옛 ad-hoc 폴더를 가리키던 하드코딩 — CLI 인자(`cleaned_dataset_csv`/`column_ledger_csv`/`out_dir`)로 교체.
  2. `survey-data-preprocessing`의 canonical 스크립트가 만들지 않는 `question_family_summary.csv`에 의존 — `column_ledger.csv`에서 직접 question_map을 만들도록 변경(불필요한 스킬 간 파일 의존 제거).
  3. **스크립트가 실행할 때마다 자기 자신의 `04_validation_notes.md`를 "2026-08-18" 하드코딩 문자열로 덮어쓰고 있었음** — 재실행할 때마다 사람이 남긴 노트가 날짜까지 포함해서 조용히 사라지는 구조. 노트 자동생성 코드를 제거하고, 다른 스킬들과 동일하게 세션에서 직접 `04_validation_notes.md`를 작성하는 방식으로 통일.
- 검증: `validation_runs/survey-data-preprocessing/2026-08-19_26.GP.UXQ/`(오늘 만든 #17 canonical 출력)를 입력으로 재실행 — **#17→#38 파이프라인이 실제로 연결됨**을 증명. 추출 응답 67건×8필드 = 536개 값 전부 2026-08-18 원본과 일치.
- 남은 일: 코드북 키워드는 UXQ 프로젝트 전용 — 다른 프로젝트 재사용 시 키워드셋 재작성 필요.

## 2026-08-19 — 기존 validation_runs 스크립트를 canonical로 소급 승격(retroactive)

- 계기: 사용자가 "나머지 데이터분석/대시보드 스킬에도 소급 적용해줘" 요청.
- 변경: `scripts/build_open_ended_workbook.py` 신규 추가. 원본은 `validation_runs/survey-open-ended-coding-skill/2026-08-18_26.GP.UXQ/`(1차 workbook 생성 검증)에서 그대로 복사함 — 코드 자체는 수정하지 않았다.
- 검증: 오늘은 코드를 재실행하지 않았다(파일 복사만 수행).
- 남은 일: 마스터 로그에 이미 기록된 한계 — 이번 검증은 전용 장문 문항이 아니라 `UXQ survey2`의 기타 답변(개방형 응답 67건) 기반이었다. 실제 장문 개방형 설문 문항이 있는 프로젝트로 재검증하면 스크립트의 일반화 여부를 더 확실히 알 수 있다.
