# Changelog — survey-interim-report-writer

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다. 목적: AI 에이전트와 대화하며 스킬을 반복 수정할 때, ①무엇을 왜 바꿨는지 ②그 변경이 어느 validation_runs 세션에서 검증됐는지를 다음 세션(사람이든 다른 에이전트든)이 바로 이어받을 수 있게 하는 것.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` (어떤 대화/요청에서 시작됐는지) + `- 변경:` (무엇을 바꿨는지, 파일 단위) + `- 검증:` (어느 validation_runs 세션에서 확인했는지) + `- 남은 일:` (있다면)
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이며, **`scripts/`가 canonical**이다 — 다음 프로젝트에 이 스킬을 쓸 때는 validation_runs의 옛 사본이 아니라 여기서 복사해서 시작한다.

---

## 2026-08-19 — 하우스 스타일 보정 코드를 스킬 canonical script로 승격

- 계기: 사용자가 "survey/interview 보고서 하우스 스타일 보정" 작업을 요청, native 실제 보고서(26.GP.UXQ) 형식과 비교해 초안을 재구성함.
- 변경:
  - `scripts/build_report_docx.py`를 이번 세션에서 개선한 버전으로 신규 추가(기존에는 `validation_runs/2026-08-18_26.GP.UXQ_dashboard-handoff/`에만 존재했음).
  - 제목 파싱 로직을 "버전+제목 한 줄" 결합 형식에서, native 실제 문서처럼 "버전 문단 / 제목 Heading1 / 날짜조직 문단" 3줄 분리 형식으로 변경(`extract_title_block`, `VERSION_LABEL_PATTERN` 추가). 기존 결합 형식도 하위호환으로 계속 지원.
  - 챕터 heading level을 native와 동일하게 정렬(챕터=Heading 1, 하위섹션=Heading 2로 매핑).
  - 표 앞에 `표 N. 제목` 캡션을 붙이는 패턴을 도입.
- 검증: `validation_runs/survey-interim-report-writer/2026-08-18_26.GP.UXQ_dashboard-handoff/` — native 원본을 템플릿으로 02_docx_draft.docx·03_appended_latest.docx 재생성 확인.
- 남은 일: docx 시각 렌더(PDF 변환)는 이 환경에서 Word COM이 멈추는 문제로 미확인 상태(HTML preview로만 대체 확인). `build_report_from_dashboard_data.py`(데이터 기반 markdown 생성 로직)는 아직 canonical화 안 됨 — 프로젝트마다 데이터 스키마가 달라 재사용성 검토 필요.
