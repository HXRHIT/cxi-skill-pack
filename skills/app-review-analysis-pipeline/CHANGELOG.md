# Changelog — app-review-analysis-pipeline

이 파일은 스킬의 동작 스키마(Skill.md)와 재사용 실행 코드(scripts/) 변경 이력을 관리한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다.
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/`에 변경이 생기면 항상 기록한다.

---

## 2026-08-27 — 대시보드 v4 중복 지표 제거와 추세/테마 드릴다운 보강

- 계기: 리뷰 수와 의견 작성 리뷰 수가 동일한데 반복 표시되고, 주차별 추세/월별 추이/테마별 대표 리뷰 탐색성이 부족하다는 피드백 대응
- 변경:
  - 대시보드 상단 카드와 수집 커버리지 표에서 `리뷰 수`와 `의견 작성 리뷰 수`가 중복 표시되지 않도록 화면 기준을 `수집 리뷰 수` 중심으로 단순화
  - 주차별 평점 추세 차트에 기간 전체 평균선을 추가
  - 주차별 평점 추세 툴팁에 주차별 표준편차와 리뷰 수를 함께 표시
  - 월별 섹션을 평균/표준편차 테이블이 아니라 월별 리뷰 작성건 수 stacked bar chart로 변경
  - 좋은 점/나쁜 점 테마와 의견별 테마 Top에서 테마별 전체 의견을 펼쳐볼 수 있는 `details` 드릴다운 추가
- 검증:
  - `python -m py_compile .agents/skills/app-review-analysis-pipeline/scripts/review_pipeline.py .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py`
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --dashboard-from-excel "tmp_app_review_hana1q_review_first_v3/하나1Q_20260827_134520/app_review_analysis_하나1Q.xlsx" --output-dir tmp_app_review_hana1q_dashboard_from_excel_v7`
  - `node`로 `tmp_app_review_hana1q_dashboard_from_excel_v7/dashboard_하나1Q.html` 인라인 스크립트 문법 확인 완료
- 남은 일: App Store 공개 RSS는 요청 기간을 바꿔도 최신순 제한 페이지 밖의 과거 리뷰 전체 커버리지를 보장하지 못하므로, 장기 과거 리뷰는 App Store Connect 또는 외부 앱 인텔리전스/리뷰 API 연계가 필요

## 2026-08-27 — 대시보드 v3 UX 피드백 반영

- 계기: App Store RSS 수집 시작일 의미가 불명확하고, 일자별 추세/전체 평점 메타/의견 작성 수/경쟁 앱 정렬/감성 도넛 크기/인사이트 제공 방식 개선이 필요하다는 피드백 대응
- 변경:
  - App Store 커버리지 메모를 “요청 시작일”과 “공개 RSS에서 확보된 가장 오래된 리뷰일”이 구분되도록 명확화
  - 일자별 평점 추세 차트를 주차별 평점 추세로 변경
  - 대시보드 상단에서 스토어 전체 평점/전체 별점 수 카드를 제거
  - Google Play / App Store 의견 작성 리뷰 수를 별도 카드로 분리
  - 경쟁 앱/시장 Top 리스트에 클릭 정렬 기능 추가
  - 감성 분포 도넛 그래프를 compact chart 영역으로 축소하고 표와 병렬 배치
  - 부정 테마 건수와 평균 평점 기반 `개선 우선순위 제안` 섹션 추가
- 검증:
  - `python -m py_compile .agents/skills/app-review-analysis-pipeline/scripts/review_pipeline.py .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py`
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --dashboard-from-excel "tmp_app_review_hana1q_review_first_v3/하나1Q_20260827_134520/app_review_analysis_하나1Q.xlsx" --output-dir tmp_app_review_hana1q_dashboard_from_excel_v6`
  - `node`로 생성 HTML 인라인 스크립트 문법 확인 완료
  - 생성 HTML에서 스토어별 의견 작성 리뷰 수, 주차별 평점 추세, 개선 우선순위 제안, sortable 경쟁 앱 테이블 확인
- 남은 일: App Store 과거 리뷰 전체 커버리지는 공개 RSS 외 대체 수집원 연계 필요

## 2026-08-27 — 대시보드 v2 지표/인사이트/경쟁 피어셋 보강

- 계기: 대시보드에서 차트가 보이지 않고, 평점 표준편차/분포/기간별 추이/인사이트/대표 리뷰 구분/경쟁 앱 선정이 부족하다는 피드백 대응
- 변경:
  - 대시보드 평균 평점 표시를 소수점 둘째 자리로 통일
  - 인라인 차트 JavaScript 중괄호 오류 수정 및 Chart.js 로드 실패 시 fallback 메시지 추가
  - 감성 분포/별점 분포에 표 기반 백업과 막대형 비율 표시 추가
  - 평점 표준편차, 스토어별 평점 통계, 월별 평점 추이, 핵심 인사이트 섹션 추가
  - 대표 리뷰를 ` | ` 연결 문자열 대신 목록형 HTML로 분리 표시
  - `banking_kr` 경쟁 피어셋 추가: 하나원큐, KB스타뱅킹, 신한 SOL, 우리WON뱅킹, NH스마트뱅킹, 카카오뱅크, 토스
  - `--skip-dashboard`, `--dashboard-from-excel`, `--competitor-peer-set` CLI 옵션 추가
  - App Store RSS 페이지 수집 중 일시 실패 시 3회 재시도 및 연속 실패 기준으로 중단하도록 보강
- 검증:
  - `python -m py_compile .agents/skills/app-review-analysis-pipeline/scripts/review_pipeline.py .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py`
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --app-name "하나1Q" --google-play-app-id com.hanabank.oqf --app-store-app-id 6743190232 --from-date 2026-03-01 --to-date 2026-08-27 --max-reviews-per-store 5000 --competitor-limit 7 --competitor-peer-set banking_kr --no-llm --skip-dashboard --output-dir tmp_app_review_hana1q_review_first_v3`
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --dashboard-from-excel "tmp_app_review_hana1q_review_first_v3/하나1Q_20260827_134520/app_review_analysis_하나1Q.xlsx" --output-dir tmp_app_review_hana1q_dashboard_from_excel_v4`
  - 산출 결과: 전체 리뷰(별점) 데이터 2,122건, 의견 작성 리뷰 2,122건, Google Play 1,873건, App Store 249건, 평점 표준편차 1.81, 월별 추이 14행, 핵심 인사이트 6개, 경쟁 피어셋 `banking_kr` 반영
  - `node`로 생성 HTML 인라인 스크립트 문법 확인 완료
- 남은 일: App Store 공개 RSS가 같은 기간에서도 249~499건으로 변동되어, 전체 과거 리뷰 커버리지는 AppFollow/Appbot 등 대체 수집원 연계 검토 필요

## 2026-08-27 — 별점 데이터 수와 의견 작성 리뷰 수 지표 추가

- 계기: 전체 리뷰(별점) 데이터 개수와 실제 의견 텍스트를 작성한 리뷰 개수를 대시보드와 품질 리포트에 명확히 포함해야 한다는 요청 대응
- 변경:
  - 정규화 리뷰에 `has_opinion_text` 파생 컬럼 추가
  - `build_dashboard_payload()` 개요에 `reviews_with_rating`, `reviews_with_opinion`, 스토어별 의견 작성 수 추가
  - 대시보드 개요 카드에 `전체 리뷰(별점) 데이터 수`, `의견 작성 리뷰 수` 표시
  - `quality_report_*.json`에 전체/스토어별 의견 작성 리뷰 수 반영
- 검증:
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --app-name "하나1Q" --google-play-app-id com.hanabank.oqf --app-store-app-id 6743190232 --from-date 2026-03-01 --to-date 2026-08-27 --max-reviews-per-store 5000 --competitor-limit 10 --competitor-queries "하나1Q,하나원큐" --no-llm --output-dir tmp_app_review_hana1q_full_v4`
  - 산출 결과: 전체 리뷰(별점) 데이터 2,372건, 의견 작성 리뷰 2,372건, Google Play 1,873건, App Store 499건, 경쟁 앱/시장 인텔리전스 26건
  - 소스별 커버리지: Google Play 2026-03-01~2026-08-26, App Store 2026-06-26~2026-08-25
- 남은 일: App Store 공개 RSS가 과거 리뷰를 2026-03-01까지 내리지 못하는 경우를 보완할 대체 수집원(AppFollow/Appbot 등) 연결 검토

## 2026-08-27 — 경쟁 앱 시장 인텔리전스(순위·다운로드 추정) 수집/대시보드 통합

- 계기: 앱 시장 트렌드 분석(경쟁사 순위/다운로드 관점)을 리뷰 대시보드와 함께 제공해야 한다는 요청 대응
- 변경:
  - `collect_market_intelligence()` 추가: 쿼리별 스토어 검색 결과(상위 N)에서 앱 메타(평점/리뷰수/설치 추정치, 카테고리)를 수집
  - Google Play 메타 수집 보강: 앱별 검색 결과의 `installs`/`installs_num` 반영 및 대상 앱/1위/다운로드 상위 플래그 계산
  - `collect_reviews()`가 시장 인텔리전스 DataFrame까지 함께 반환하도록 반환 스키마 확장
  - `build_dashboard_payload()`/`_dashboard_html()`에서 `market_intelligence` 섹션 반영(경쟁 앱 Top 테이블)
  - `write_outputs()`에서 `market_intelligence_*.csv`, 엑셀 `경쟁앱_상위권` 시트, `quality_report` 시장 인덱스 집계 추가
  - CLI 옵션 확장: `--competitor-limit`, `--competitor-queries`, `--no-market-intelligence`
- 검증:
  - 최신 하나1Q 통합 검증은 상단 `별점 데이터 수와 의견 작성 리뷰 수 지표 추가` 항목의 `com.hanabank.oqf` 실행 결과를 기준으로 확인
- 남은 일: App Store에서 설치 수 수치 획득 소스 보강 및 리테일 경쟁사 정렬 규칙(검색어별/카테고리별 우선순위) 정교화

## 2026-08-27 — Google Play 페이지네이션 및 스토어별 앱 평점 메타 수집 보강

- 계기: 사용자 요청(Play Store 리뷰 수집이 극히 적게 나오는 문제 해결 및 양 스토어 앱 평점 메타 필수 수집)
- 변경:
  - `review_pipeline.py`의 Google Play 수집 로직을 단일 호출에서 페이지네이션 반복 호출로 전환 (`continuation_token` 사용)
  - Google Play, App Store 앱 메타(전체 평점/리뷰 수) 수집 추가
  - 대시보드 개요와 `quality_report_*.json`에 스토어별 앱 평점 메타 반영
  - `store_ratings_*.csv` 산출 추가 및 CLI 출력에 경로 반영
- 검증:
  - `python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py --app-name "하나1Q" --google-play-app-id com.hanafn.oneqgrbs --app-store-app-id 6743190232 --from-date 2019-01-01 --to-date 2026-08-27 --max-reviews-per-store 5000 --output-dir tmp_hana1q_review_v2 --no-llm`
  - 동일 명령으로 2026-03-01~2026-08-27 구간도 추가 검증 예정(실행 결과 파일명/개수 기준 확인 필요)
- 남은 일: Google Play 스크롤 정렬 대비(최신/관련성 옵션) 및 시장별 평점 메타 동기화 이슈 모니터링

## 2026-08-27 — 아이디어 #4의 실행 파이프라인 정착안으로 v1 스크립트 추가

- 계기: 사용자 요청(앱명 + 기간 기반 통합 리뷰 분석)을 MCP에서 바로 호출 가능한 형태로 재사용 코드화.
- 변경: `.agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py`와 `scripts/review_pipeline.py` 추가.
  - 앱 후보 해소(이름→Play/App Store ID)
  - 기간 필터 수집
  - 감성/테마 분석(LLM 우선, 폴백 규칙)
  - 테마 요약, pros/cons 요약, 품질 메트릭
  - dashboard.html + CSV/Excel/JSON 출력 생성
- 검증: 사용자 요청 당시 실행 검증은 생략(요청에 따라 사용 환경에서 실행 후 결과 재현 필요).
- 남은 일: i18n 키워드 사전 보강, App Store 지역별 수집 품질 보강, 대시보드 접근성 가이드 보강.

## 2026-08-27 — v1 실행 테스트를 반영한 안정성 보강

- 계기: 사용자 “진행하고 테스트까지” 요청.
- 변경:
  - `review_pipeline.py` 문법 오류 수정 (HTML 템플릿 f-string 중괄호 이스케이프).
  - 콘솔 UTF-8 안전 출력 처리 추가.
  - 비대화형 환경에서 후보 선택 `EOFError` 발생 시 1순위 앱 자동 선택.
  - 대시보드 별점 분포 키 타입을 문자열로 정규화.
- 검증: 다음 시나리오 실행 및 산출물 생성 확인
  - `python run_app_review_pipeline.py --app-name 하나원큐 --google-play-app-id com.hanabank.oqf --app-store-app-id 6743190232 --from-date 2026-08-01 --to-date 2026-08-27 --max-reviews-per-store 5 --no-llm --output-dir tmp_app_review_test3`
  - `python run_app_review_pipeline.py --app-name 하나원큐 --from-date 2026-08-01 --to-date 2026-08-27 --max-reviews-per-store 5 --no-llm --output-dir tmp_app_review_test2`
  - `python run_app_review_pipeline.py --app-name zxy_non_existing_app_12345 --from-date 2026-08-01 --to-date 2026-08-27 --no-llm` (실패 경로)
- 남은 일: 엔드투엔드 출력물 품질 검토(테마 정확도) 후 규칙 기반 테마 사전 보완.
