# Changelog — interview-results-dashboard

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다. 목적: AI 에이전트와 대화하며 스킬을 반복 수정할 때, ①무엇을 왜 바꿨는지 ②그 변경이 어느 validation_runs 세션에서 검증됐는지를 다음 세션(사람이든 다른 에이전트든)이 바로 이어받을 수 있게 하는 것.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 — Word COM 렌더 시도 중 발견한 인용 마커 버그 수정, 표 렌더링 추가

- 계기: 사용자가 interview docx 시각 렌더를 요청 → Word COM이 멈추는 문제 확인 후, 대안으로 HTML preview를 Playwright로 스크린샷하는 과정에서 렌더링 버그를 실제로 발견함.
- 변경:
  - `scripts/build_report_docx.py`를 신규 추가(기존에는 `validation_runs/2026-08-18_23.BK.S.233Q.GBIUX/`에만 존재).
  - 마크다운 파서에 `|` 표 파싱, `▍`(인용)·`—`(귀속) 두 줄 인용 블록, `<!-- 근거: ... -->` HTML 주석 스킵(문항 추적성은 유지하되 본문 비노출)을 새로 지원.
  - **버그 수정**: `add_quote_attribution()`과 HTML의 `render_quote_html()`/`quote_attr` 분기에서 `▍`/`—` 마커를 파싱 시 벗겨내고 렌더링 시 다시 안 붙이는 실수가 있었음 — docx와 HTML 양쪽에서 마커 없이 렌더되던 것을 수정.
  - 표지(Executive Summary 등)를 하드코딩 대신 markdown 기반으로 통일.
- 검증: `validation_runs/interview-results-dashboard/2026-08-18_23.BK.S.233Q.GBIUX/09_report_preview.html`을 로컬 HTTP 서버 + Playwright 스크린샷으로 실제 렌더 확인.
- 남은 일: docx → PDF 렌더는 이 환경에서 Word COM이 `doc_opened` 단계에서 멈추는 문제가 재현됨(원인 미상). LibreOffice(soffice) 등 대안 렌더러 설치 여부를 팀 차원에서 검토할 만함.
