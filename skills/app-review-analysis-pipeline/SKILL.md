---
name: app-review-analysis-pipeline
description: Collect Play Store and App Store reviews for a user-specified app and period, then produce a sentiment + theme summary dashboard (pros/cons + opinion themes) in CSV/Excel/HTML for UX review workflows. Use this when Codex user asks for app-store review intelligence and wants consistent, reproducible 분석 결과 instead of 수동 복붙.
---

# App Review Analysis Pipeline

## 개요

이 스킬은 앱 이름(또는 앱 ID/번들ID)을 입력 받아 아래 파이프라인을 수행한다.

1. 앱 식별
   - 앱 이름을 받으면 Google Play / App Store 후보를 조회해 앱 ID를 확인한다.
2. 리뷰 수집
   - 지정한 기간 동안 Google Play 리뷰와 App Store 리뷰를 각각 수집한다.
3. 정규화
   - 서로 다른 소스 스키마를 통합 컬럼으로 정리한다.
4. 분석
   - 감성 분류(긍정/중립/부정) 및 테마 추출을 수행한다.
5. 산출
   - 기본은 CSV/Excel/JSON 검토본을 먼저 생성한다.
   - 사용자가 `app_review_analysis_*.xlsx`를 확인한 뒤 HTML 대시보드를 생성할 수 있다.

## 언제 쓰는지

- “이 앱 최신 리뷰를 기간별로 모아줘”
- “플레이스토어/앱스토어 평점 분포와 부정 의견 테마를 뽑아줘”
- “좋은 점/나쁜 점, 의견 테마가 분리된 대시보드 형태로 정리해줘”

## 입력 가정

- 앱명은 1개 단위로 입력한다.
- 수집 기간은 기본적으로 사용자 질의로 받되, 미제공 시 인터랙티브로 요청한다.
- API/라이브러리 가용성은 환경마다 다를 수 있으므로, LLM 분석은 보조 모드로 동작한다.

## 실행 워크플로우

### 1) 앱 식별

- 앱 ID가 이미 주어지면 바로 수집한다.
- 앱 ID가 없으면 스크립트가 후보를 보여주고 상단 1개 또는 수동 선택을 사용한다.

### 2) 리뷰 수집

- Google Play: `google-play-scraper`의 `reviews(...)` 사용
- App Store: Apple RSS(`itunes.apple.com`) 사용 (별도 라이브러리 불필요)

### 3) 정규화/분석

- 공통 스키마:
  - `source, app_id, review_id, review_title, review_body, rating, review_date, app_version, helpful_count, language, review_url, has_opinion_text`
- 기간 필터: `from_date`, `to_date`로 포함 범위 처리
- 감성 분류: LLM 가능 시 `긍정/중립/부정` + 테마 2~3개 추출
- LLM이 비활성일 경우 규칙 기반 감성·테마 폴백으로 처리
- 경쟁 앱: `--competitor-peer-set banking_kr` 사용 시 국내 대표 은행 앱 피어셋(KB스타뱅킹, 신한 SOL, 우리WON뱅킹, NH스마트뱅킹, 카카오뱅크, 토스 등)을 직접 조회한다.

### 4) 산출물

- `dashboard.html`: 대시보드(요약 지표, 별점 분포, 기간별 추세, 주요 pros/cons)
- `normalized_reviews_*.csv`: 정규화 리뷰
- `theme_summary_*.csv`: 테마별 건수/평균 평점/비율
- `pros_cons_summary_*.csv`: 좋은점/나쁜점 핵심 정리
- `quality_report_*.json`: 수집/중복/누락률 메타
- `store_ratings_*.csv`: Google Play / App Store 앱 전체 평점(average rating) + 총 평점 리뷰 수
- `market_intelligence_*.csv`: 스토어/쿼리별 경쟁 앱 상위 항목(순위, 추정 설치량, 리뷰 수, 대상 앱/상위권 여부)

- 추가 메트릭: `collect_market_intelligence` 실행 시 경쟁 앱 시장 Top 테이블을 수집해 `market_intelligence_*` 산출물과 대시보드의 `경쟁 앱/시장 Top` 섹션에 함께 반영한다.

- 추가 메트릭: Google Play / App Store 앱 ID가 주어지면 각 스토어의 앱 전체 평점을 별도 메타(`store_ratings_*`, `quality_report_*`)로 저장한다. 대시보드 메인 카드는 수집 리뷰 데이터 중심으로 구성한다.

- 추가 메트릭: `quality_report_*`에는 `전체 리뷰(별점) 데이터 수`, `의견 작성 리뷰 수`, 스토어별 의견 작성 리뷰 수를 함께 보존한다. 단, 대시보드에서는 리뷰 수와 의견 작성 리뷰 수가 동일하면 중복 카드/컬럼을 만들지 않고 `수집 리뷰 수` 중심으로 한 번만 표시한다.

- 커버리지 경고: 소스별 수집 날짜 범위를 `source_coverage`로 기록하고, 요청 시작일보다 늦은 리뷰까지만 수집된 경우 `coverage_note`로 공개 스토어 엔드포인트 한계를 표시한다.

- 대시보드 인사이트: 평균 평점은 소수점 둘째 자리까지 표시하고, 표준편차, 평점 분포, 기간별(월별) 평점 추이, 핵심 인사이트, 대표 리뷰 목록형 표시를 포함한다.
- 대시보드 v3 UX 기준:
  - 스토어 전체 평점/전체 별점 수 메타는 메인 카드에서 제외하고, 수집 리뷰 데이터 중심으로 표시한다.
  - 의견 작성 리뷰 수는 Google Play / App Store를 분리해 표시한다.
  - 긴 수집 기간에서는 일자별 차트 대신 주차별 평점 추세를 기본으로 사용한다.
  - 경쟁 앱/시장 Top 리스트는 클릭 정렬 가능한 테이블로 제공한다.
  - 감성 분포 도넛 그래프는 작은 요약 그래프로 표시하고, 표 기반 수치를 함께 제공한다.
  - 개선 우선순위 제안은 부정 테마 건수와 평균 평점을 결합해 산출한다.
- 대시보드 v4 UX 기준:
  - 주차별 평점 추세에는 기간 전체 평균선을 함께 표시한다.
  - 주차별 평점 추세 툴팁에는 해당 주차의 평균 평점, 표준편차, 리뷰 수를 함께 제공한다.
  - 월별 섹션은 월별 리뷰 작성건 수만 그래프로 표시하고, 평균/표준편차 테이블은 기본 노출하지 않는다.
  - 좋은 점/나쁜 점 테마와 의견별 테마 Top에는 테마별 전체 의견을 펼쳐볼 수 있는 드릴다운을 제공한다.

## 실행 방법

```bash
python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py \
  --app-name "하나원큐" \
  --from-date 2026-08-01 \
  --to-date 2026-08-27 \
  --max-reviews-per-store 500
```

```bash
python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py \
  --app-name "하나원큐" \
  --google-play-app-id com.hanabank.oqf \
  --app-store-app-id 6743190232 \
  --from-date 2026-08-01 \
  --to-date 2026-08-27 \
  --competitor-limit 10 \
  --competitor-peer-set banking_kr \
  --no-llm
```

검토용 Excel을 먼저 만들고, 사용자가 확인한 뒤 대시보드만 생성하는 흐름:

```bash
python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py \
  --app-name "하나원큐" \
  --google-play-app-id com.hanabank.oqf \
  --app-store-app-id 6743190232 \
  --from-date 2026-03-01 \
  --to-date 2026-08-27 \
  --max-reviews-per-store 5000 \
  --competitor-peer-set banking_kr \
  --skip-dashboard \
  --no-llm
```

```bash
python .agents/skills/app-review-analysis-pipeline/scripts/run_app_review_pipeline.py \
  --dashboard-from-excel app_review_analysis_하나원큐.xlsx \
  --output-dir reviewed_dashboard
```

## 의존성

- `pandas`, `requests`, `google-play-scraper`, `openpyxl`
- 감성/테마 LLM을 쓰려면 `google-generativeai`와 `GEMINI_API_KEY` 필요

## 경고

- 수집량은 스토어 정책/요청 실패에 따라 제한될 수 있다.
- App Store RSS는 국가/언어 필터 특성상 기간 포함 결과가 빈번히 밀릴 수 있다. `--from-date`, `--to-date`, `--appstore-markets`로 요청 범위와 국가를 바꿀 수는 있지만, 공개 RSS가 최신순 제한 페이지 밖의 과거 리뷰를 노출하지 않으면 요청 시작일까지 강제로 내려갈 수 없다. 장기 과거 리뷰 전체 커버리지는 App Store Connect 권한, 사내 보유 원자료, 또는 외부 앱 리뷰/마켓 인텔리전스 API 연계가 필요하다.
- LLM 반환은 외부 모델 비정형 출력일 수 있어 파싱 실패 시 규칙 폴백으로 자동 복원한다.
