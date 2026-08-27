# Changelog — coding-sheet-generator

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다. 목적: AI 에이전트와 대화하며 스킬을 반복 수정할 때, ①무엇을 왜 바꿨는지 ②그 변경이 어느 validation_runs 세션에서 검증됐는지를 다음 세션(사람이든 다른 에이전트든)이 바로 이어받을 수 있게 하는 것.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 (2차) — 실제 재실행 검증, 버그 2건 발견·수정 + Node→Python 전면 포팅

- 계기: "#43부터 이어서 진행해줘" 요청으로 promoted-but-untested 스크립트를 실제 실행.
- 발견·수정 1: `extract_guide_structure.py`의 Q45/Q47 항목 리스트가 항상 비어있던 원인 확정 — `normalize()`가 개행문자를 먼저 지운 뒤 `parse_numbered_items()`에 넘겨서, 줄바꿈 기준 파싱이 원천적으로 실패하고 있었음. raw 셀 값을 먼저 파싱하도록 수정. native 원본 가이드로 재실행해 Q45 11개 항목·Q47 10개 SUS 항목이 실제로 채워짐을 확인.
- 확인(버그 아님): "인지와 유용 문항 범위 불일치"(guide 7개 vs downstream 9개)는 실제로 가이드의 `activity_type` 컬럼 기준으로 재확인한 결과 **guide-first 7개 추출이 맞음** — Q14/Q27은 activity_type이 다르고 질문 구조도 다름. downstream workbook의 확장은 사람의 별도 스코프 결정이지 추출 버그가 아님.
- 발견·수정 2 (환경 문제): `build_coding_workbook.mjs`가 쓰는 `@oai/artifact-tool` 패키지가 이 환경(전역 npm 포함 전체)에 **존재하지 않음**을 확인 — 2026-08-18 노트의 "non-zero exit" 미스터리의 실제 원인으로 추정(아마 Claude.ai Artifacts 등 다른 실행 환경에서 만들어진 스크립트). `scripts/build_coding_workbook.py`를 openpyxl로 신규 작성해 동일한 8시트·수식·드롭다운 구조를 이 환경에서 실행 가능하게 포팅.
- 발견·수정 3 (포팅 중 발견한 진짜 계산 버그): SUS 점수 공식의 `*2.5` 배수가 5점 척도용 상수인데 이 워크북은 1~7점 10문항 척도를 씀 — 중립(전부 4점) 응답이 50이 아니라 75로, 최고 응답이 100이 아니라 150으로 계산되던 버그. 올바른 배수(`100/60 = 5/3`)로 수정하고 중립/최고/최저 케이스 + 랜덤 5건을 교과서적 SUS 계산과 대조해 정확히 일치함을 확인.
- 검증: native 원본 인터뷰 가이드로 전체 파이프라인(가이드 xlsx → JSON → 워크북) 실행 완료. 8개 시트 차원·수식·드롭다운을 원본 로직과 1:1 대조. **단, 실제 수식 재계산(recalc)은 수행하지 못함** — `xlsx` 스킬의 `recalc.py`가 디스크에 존재를 확인했으나 이 세션의 Bash에서는 "파일 없음"으로 실행 불가(스킬 자체 실행 컨텍스트에 샌드박스된 것으로 추정, Word 렌더링 때와 동일한 제약). 수식 정확성은 수동/논리 검증(SUS 버그 발견 포함)으로 대체함.
- 남은 일: 실제 LibreOffice/Excel 환경에서 `recalc.py` 재실행해 수식이 에러 없이 계산되는지 최종 확인 필요. PNG 렌더는 openpyxl에 대응 기능이 없어 미구현.

## 2026-08-19 — 기존 validation_runs 스크립트를 canonical로 소급 승격(retroactive), 알려진 버그를 그대로 이관

- 계기: 사용자가 "나머지 데이터분석/대시보드 스킬에도 소급 적용해줘" 요청.
- 변경:
  - `scripts/extract_guide_structure.py`(Python, 가이드 구조 추출)와 `scripts/build_coding_workbook.mjs`(Node.js, 실제 워크북 생성)를 신규 추가. 원본은 `validation_runs/coding-sheet-generator/2026-08-18_24.ST.GBI/`(GBI 2차 protocol 1차 workbook scaffold 검증)에서 그대로 복사함 — 코드 자체는 수정하지 않았다.
  - 이 스킬은 파이프라인이 Python(추출)→Node.js(생성) 두 언어로 나뉘어 있다는 점을 그대로 유지했다(임의로 통일하지 않음).
- 검증: 오늘은 코드를 재실행하지 않았다(파일 복사만 수행).
- 남은 일(고치지 않고 그대로 이관한 기존 이슈):
  - `04_validation_notes.md`에 이미 기록된 버그: **bundled exporter가 `.xlsx`와 render 파일을 정상적으로 남긴 뒤에도 non-zero exit를 반환**함 — 원인 미상, 다음 세션에서 재현·수정 필요.
  - Q45/Q47 item list가 downstream workbook에서 header fallback을 쓰는 문제(마스터 로그 기록) — 아직 미해결.
