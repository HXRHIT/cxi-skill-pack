# Changelog — survey-data-preprocessing

이 파일은 스킬의 **동작(SKILL.md/references)과 재사용 코드(scripts/)가 실제로 어떻게 바뀌어왔는지**를 세션 단위로 기록한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/` 아래 코드가 바뀌면 반드시 이 파일에도 기록한다. **`scripts/`가 canonical**이며, validation_runs 안의 프로젝트별 사본은 실행 스냅샷일 뿐이다.

---

## 2026-08-19 (2차) — 실제 canonical 스크립트 작성 및 byte-perfect 검증

- 계기: 사용자가 "#17/#18/#39도 실제로 코드 저장해서 검증해줘" + "모든 스킬은 재사용 가능한 코드를 생성하고, 테스트시마다 업데이트가 가능해야 함" 요청.
- 변경: `scripts/build_cleaned_dataset.py` 신규 작성(이전 항목의 "코드 없음" 상태를 해소). native의 실제 raw xlsx를 직접 열어 헤더 구조(3행 헤더: 문항코드/문항텍스트/옵션라벨, forward-fill)를 역공학으로 파악해 구현. 개발 중 발견한 구조적 함정 2건(후행 시스템 컬럼의 forward-fill 오귀속, "기타 답변" 동반 컬럼의 명명 규칙)을 코드 주석과 검증 노트에 남김.
- 검증: `validation_runs/survey-data-preprocessing/2026-08-19_26.GP.UXQ/04_validation_notes.md` — 2026-08-17 원본 산출물과 `cleaned_dataset.csv` 242개 컬럼 헤더 전부, 67,760개 데이터 셀 전부(숫자 포맷 차이 제외) byte 단위 일치 확인. `dataset_profile.json`의 family 분류(37개, 타입별 2/21/3/11)·group_candidates(성별/연령대/중복판단)도 완전 일치.
- 남은 일: 이 스크립트의 헤더 파싱 가정은 UXQ 1개 프로젝트에서만 검증됨 — 다른 프로젝트(DIGIWM/IBUJA 등) 재사용 전 헤더 구조를 직접 확인할 것.

## 2026-08-19 — 소급 적용 점검: 검증 자체는 real, 다만 재사용 코드가 저장되지 않음

- 계기: 사용자가 "나머지 데이터분석/대시보드 스킬에도 소급 적용해줘" 요청 → scripts/ 승격을 시도했으나 코드가 없어서 "재사용 가능한 스크립트가 없다"고 보고했더니, 사용자가 "그럼 #17/#18/#39 검증 자체를 한 게 맞냐"고 정당하게 재질문함.
- **재확인 결과 (중요, 오해 방지)**: 검증은 실제로 제대로 수행됐다. `validation_runs/2026-08-17_survey-analysis-line/uxq_survey2/cleaned_dataset.csv`를 직접 열어 대조한 결과, 성별 172/108·연령대 112/74/57/30/7 분포가 완전히 별개 파이프라인(`survey-results-dashboard`용 `01_dashboard_data.json`)에서도 독립적으로 동일하게 나타남 — 우연이 아니라 실제 native raw 파일(`03_execute__survey-response__설문2_raw.xlsx`, 경로 확인함)을 읽어 처리했다는 증거. DIGIWM(200행)·IBUJA(403행)도 `dataset_profile.json`의 `raw_path`가 실제 native 파일을 정확히 가리키고 행 수가 README 요약과 일치함을 확인.
- **없는 것은 "코드"이지 "검증"이 아니다**: 이 세션에서는 전처리 로직을 파이썬 스크립트 파일로 저장하지 않고 즉석(ad-hoc)으로 실행해 결과만 남긴 것으로 보인다. 즉 산출물(csv/json/md)은 신뢰할 수 있지만, 그 산출물을 만든 절차를 재실행할 저장된 코드가 없다는 뜻이다.
- 변경: 없음(승격할 코드가 없어 `scripts/`를 만들지 않았다).
- 남은 일: 다음에 이 스킬을 실제로 실행할 때는 로직 자체는 이미 검증됐으니 그대로 재사용하되(`01_preprocessing_profile.md`의 PASS/WARN 기준 등 문서화된 규칙 참고), **이번에는 처리 코드를 파일로 저장하고 `scripts/`에 canonical로 등록**하는 것을 첫 번째 할 일로 삼을 것.
