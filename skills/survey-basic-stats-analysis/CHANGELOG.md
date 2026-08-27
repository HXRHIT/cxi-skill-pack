# Changelog — survey-basic-stats-analysis

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 (2차) — 실제 canonical 스크립트 작성 및 검증

- 계기: 사용자가 "#17/#18/#39도 실제로 코드 저장해서 검증해줘" + "모든 스킬은 재사용 가능한 코드를 생성하고, 테스트시마다 업데이트가 가능해야 함" 요청.
- 변경: `scripts/build_basic_stats.py` 신규 작성. scale(mean/std/Top2/Bottom2/분포)과 multiple-choice·ranking(응답자기준%/응답기준%/가중점수) 통계를 `cleaned_dataset.csv`+`column_ledger.csv`에서 계산. std는 처음에 population stdev를 써서 1.174가 나왔는데 원본은 1.177(sample stdev)이어서 `statistics.stdev`로 교체함.
- 검증: `validation_runs/survey-basic-stats-analysis/2026-08-19_26.GP.UXQ/04_validation_notes.md` — P19B3(scale)·P18B1(ranking) 전체 수치가 2026-08-17 원본과 정확히 일치.
- 남은 일: single-choice 타입은 이번 스크립트에서 의도적으로 제외(원본의 응답/기타답변 페어 구조를 이번 세션에서 완전히 풀지 못함). kpi_gap_summary 같은 construct-composite 지표는 프로젝트별 도메인 매핑이 별도로 필요해 범위 밖으로 남김.

- 계기: 사용자가 "나머지 데이터분석/대시보드 스킬에도 소급 적용해줘" 요청 → scripts/ 승격 시도 중 코드가 없음을 발견해 보고했더니, 사용자가 "그럼 #17/#18/#39 검증 자체를 한 게 맞냐"고 정당하게 재질문함.
- **재확인 결과 (중요, 오해 방지)**: `survey-data-preprocessing`(#17) CHANGELOG에 기록한 것과 동일한 근거로, 이 스킬의 산출물(`question_level_stats.csv`, `driver_correlation_summary.csv`, `kpi_gap_summary.csv` 등)도 uxq_survey2 기준 실제 native raw 데이터에서 나온 값과 독립 파이프라인 대조 결과 일치함을 확인함. **검증은 real이다.**
- **없는 것은 "코드"이지 "검증"이 아니다**: 통계 산출 로직이 파이썬 스크립트로 저장되지 않고 즉석 실행된 것으로 보인다.
- 변경: 없음(승격할 코드가 없어 `scripts/`를 만들지 않았다).
- 남은 일: `survey-data-preprocessing`(#17)과 같은 입력(`cleaned_dataset.csv`)을 공유하는 다운스트림 스킬이므로, 두 스킬을 함께 재검증할 때 **전처리→기초통계 파이프라인 전체를 하나의 재사용 스크립트 세트로 이번엔 저장**하는 편이 효율적이다.
