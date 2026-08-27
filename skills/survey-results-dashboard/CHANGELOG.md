# Changelog — survey-results-dashboard

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다. 목적: AI 에이전트와 대화하며 스킬을 반복 수정할 때, ①무엇을 왜 바꿨는지 ②그 변경이 어느 validation_runs 세션에서 검증됐는지를 다음 세션(사람이든 다른 에이전트든)이 바로 이어받을 수 있게 하는 것.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 — 기존 validation_runs 스크립트를 canonical로 소급 승격(retroactive)

- 계기: 사용자가 "나머지 데이터분석/대시보드 스킬에도 소급 적용해줘" 요청 — survey-interim-report-writer·interview-results-dashboard에 먼저 적용한 scripts/+CHANGELOG 패턴을 이 스킬에도 적용.
- 변경:
  - `scripts/build_full_dashboard.py`, `scripts/build_interactive_dashboard.py`, `scripts/build_dashboard_report_bridge.py`를 신규 추가. 원본은 `validation_runs/survey-results-dashboard/2026-08-18_26.GP.UXQ_full-validation/`(2차 full validation, 26.GP.UXQ 프로젝트)에서 그대로 복사함 — 코드 자체는 수정하지 않았다.
  - 1차 검증(`validation_runs/survey-results-dashboard/2026-08-18_26.GP.UXQ/build_dashboard.py`)은 2차 full-validation 버전으로 대체된 것으로 보고 승격하지 않음. 다만 이 판단은 **코드 diff를 직접 비교하지 않고 마스터 로그의 "2차 full validation 완료" 서술만 근거로 내린 추정**이다 — 실제로 1차 스크립트에만 있는 기능이 2차에서 유실됐을 가능성을 배제하지 않았다.
- 검증: 오늘은 코드를 재실행하지 않았다(파일 복사만 수행) — 다음에 이 스킬을 실제로 쓸 때 `scripts/`의 3개 파일이 정상 동작하는지 재확인 필요.
- 남은 일:
  - 1차 `build_dashboard.py`와 2차 3개 파일의 실제 diff 비교(기능 유실 여부 확인).
  - PPTX/PDF 렌더링 실물 검증은 아직 없음(마스터 로그의 "부분 결핍" 항목 — #19 차트형 커스텀 대시보드 실물).
