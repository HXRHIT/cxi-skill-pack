# Changelog — recruiting-list-legend-generator

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/`가 canonical이며, `validation_runs/` 안의 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-27 — 2차 forward 검증(HANAEZ·GBI) + `scripts/add_guide_sheet.py` canonical 신설

- 계기: 사용자 지시로 D 등급 미검증 스킬 순차 검증. 1차 검증(2026-08-18, 25.S.1QPLAY)이 남긴 액션 3건(① 가이드 시트 index 0 재배치 경로 확정 ② single-sheet handoff / raw-final split 패턴 forward validation ③ `#14`/`pid_map.csv` 규칙 합치 검증)을 닫는 것이 목표.
- 변경:
  - **`scripts/add_guide_sheet.py` 신설 (canonical)**. 1차 검증본 `build_recruiting_legend_workbook.mjs`는 `validation_runs/.../2026-08-18_25.S.1QPLAY/`에 그대로 남겨두고 **승격하지 않았다** — Codex 런타임의 `node_modules` 심볼릭 링크에 의존해 다른 환경에서 실행되지 않기 때문이다. 대신 openpyxl 기반 Python으로 다시 썼다. 설계 결정 2가지:
    - 가이드 **내용**은 스크립트가 판단하지 않는다. JSON spec으로 받는다(워크북 해석은 사람/모델, 렌더·시트순서·검증은 코드).
    - 실행마다 검증 JSON을 남긴다(`guide_is_first_sheet` / 원본 시트·행수 보존 / 수식 오류 수 / 수식 셀 수).
  - **SKILL.md §1** — 워크북 유형에 `sample-composition summary`와 `raw / final split` 2종 추가. 요약 시트가 하드코딩(수식 0개)일 수 있으니 경고하라는 규칙 포함.
  - **SKILL.md §2** — 가이드 시트가 index 0에 놓여야 함을 명시하고 `scripts/add_guide_sheet.py`를 지정. 스크리너 질문 본문의 위치를 3경우(헤더에 전문 있음 / 번호만 있음 / 없음)로 나눠 가이드 문구를 다르게 쓰도록 규정. (검증 F1 — 1차의 "질문 본문 없음" 한계는 1QPLAY 특유였고 일반 규칙이 아님을 확인)
  - **SKILL.md §4a 신설** — raw/final 분리형에서 둘의 관계(삭제·분할·재배열 / 행 집합 변화 여부 / 어느 파일을 읽어야 하는지)를 실측해 기술하도록 규정. (F3)
  - **SKILL.md §5** — risky field 예시 4종 추가: 하드코딩 집계 시트 · 산출식 없는 derived 컬럼 · 헤더 앞 공백/값 표기 불일치 · vendor 플랫폼 메타를 참여자 데이터로 오인. (F4)
  - **SKILL.md §5a 신설** — 팀의 폐기 표기(`//2차 사전설문에서 제외`)를 읽고 그대로 보존하라는 규칙. 컬럼이 왜 빠졌는지가 이 표기에만 남아 있다. (F2)
  - **SKILL.md §3** — PID 기본값(`P001`)을 적용하기 전에 프로젝트 실제 PID를 먼저 읽으라는 절 추가. 실측 3종(GBI `P19`~ 무패딩·**차수 넘어 연속** / 1QPLAY 식별자 3종 병존 / HANAEZ PID 없음+vendor ID 불연속)을 표로 명시하고, 차수 재번호 금지·vendor_id 보존·`#14`의 대괄호 표기(`[P001]`)와의 불일치를 명시. (F5)
- 검증: `validation_runs/recruiting-list-legend-generator/2026-08-27_forward_HANAEZ-GBI/` — 판정 **PASS**.
  - `25.S.HANAEZ` 유저스푼 공유용(단일시트 18행) → `guide_is_first_sheet: true`, 시트·행수 보존, 수식 오류 0.
  - `24.ST.GBI` 2차 리크루팅 명단(2시트) → `guide_is_first_sheet: true`, `리크루팅 명단_final` 9행·`요약` 7행 보존, **차트 2개(`chart1.xml`·`chart2.xml`)가 재배치 후에도 `요약` 시트에 정상 연결 유지**. openpyxl 재저장이 차트를 유실할 것으로 예상해 `--guide-only` 우회 경로를 넣어뒀으나 기본 경로로 충분했다.
  - 1차 액션 ①② 해소, ③은 **부적합 확인**(PID 표기가 스킬 간·실제 간 삼중 불일치) → 규칙으로 전환해 §3에 기록.
- 남은 일:
  - 시트 렌더 이미지 미생성 — 1차는 PNG를 남겼는데 이번엔 xlsx+JSON만. 시각 가독성 재확인 필요.
  - `24.S.BIZWEB` 3종 · `25.S.BIZMOB` 2종 · `26.S.PAYAI` 스크리닝 미적용.
  - GBI `금융 관심도`가 6문항 평균이라는 판단은 값 형태로 추정한 것 — 산출식 확정 필요.
  - `#14 transcript-anonymizer-skill`의 `[P001]` 표기와 이 스킬의 `P001` 표기 중 무엇을 표준으로 할지 미결(#14 검증 시 함께 정리).
  - `pid_map.csv` 실물이 native 어느 프로젝트에도 없음 — 만들 규칙인지 확인 필요.
