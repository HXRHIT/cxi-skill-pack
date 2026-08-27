"""CLI entrypoint for app review analysis."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from review_pipeline import (
    PipelineConfig,
    parse_comma_list,
    analyze_sentiment_and_theme,
    build_pros_cons,
    build_theme_summary,
    choose_candidate,
    collect_reviews,
    parse_date,
    prompt_for_period,
    resolve_app_store_candidates,
    resolve_google_play_candidates,
    safe_slug,
    write_dashboard_from_excel,
    write_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="앱 리뷰 수집/분석을 위한 공용 파이프라인")
    parser.add_argument("--app-name", default="", help="리뷰를 수집할 앱 이름")
    parser.add_argument("--google-play-app-id", default="", help="Google Play 패키지명(예: com.hanabank.oqf)")
    parser.add_argument("--app-store-app-id", default="", help="App Store 앱 ID(예: 6743190232)")
    parser.add_argument("--from-date", default="", help="시작일 (YYYY-MM-DD)")
    parser.add_argument("--to-date", default="", help="종료일 (YYYY-MM-DD)")
    parser.add_argument(
        "--markets",
        default="kr",
        help="Google Play 후보/수집 시장 코드 (콤마 구분, 기본 kr)",
    )
    parser.add_argument(
        "--appstore-markets",
        default="kr",
        help="App Store 후보/수집 시장 코드 (콤마 구분, 기본 kr)",
    )
    parser.add_argument("--max-reviews-per-store", type=int, default=500, help="스토어별 최대 수집 건수")
    parser.add_argument("--output-dir", default="", help="출력 기본 폴더(비워두면 app_review_outputs)")
    parser.add_argument("--skip-dashboard", action="store_true", help="검토용 Excel/CSV/JSON까지만 생성하고 HTML 대시보드는 생성하지 않음")
    parser.add_argument("--dashboard-from-excel", default="", help="검토 완료된 app_review_analysis_*.xlsx에서 HTML 대시보드만 생성")
    parser.add_argument("--no-llm", action="store_true", help="LLM 기반 분석 사용 안 함(규칙 기반만 사용)")
    parser.add_argument("--top-themes", type=int, default=8, help="테마 요약에서 보일 상위 테마 수")
    parser.add_argument("--competitor-limit", type=int, default=8, help="스토어별 경쟁 앱 상위 N개 수집")
    parser.add_argument(
        "--competitor-queries",
        default="",
        help="경쟁 앱 검색 쿼리(콤마 구분). 비워두면 앱명 사용",
    )
    parser.add_argument(
        "--competitor-peer-set",
        default="auto",
        help="경쟁 앱 피어셋(auto, banking_kr, search). banking_kr은 국내 대표 은행 앱을 직접 조회",
    )
    parser.add_argument("--no-market-intelligence", action="store_true", help="경쟁 앱 시장 인텔리전스 수집 생략")
    return parser.parse_args()


def _split_markets(raw: str) -> list[str]:
    return [v.strip() for v in raw.split(",") if v.strip()]


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_dir) if args.output_dir else None

    if args.dashboard_from_excel:
        artifact_paths = write_dashboard_from_excel(
            Path(args.dashboard_from_excel),
            output_dir=output_root,
        )
        print("대시보드 생성 완료:")
        print(f"  - 출력 폴더: {artifact_paths['output_dir']}")
        print(f"  - dashboard: {artifact_paths['dashboard_html']}")
        print(f"  - excel: {artifact_paths['excel_path']}")
        return

    if not args.app_name.strip():
        print("--app-name 또는 --dashboard-from-excel 중 하나는 필요합니다.")
        sys.exit(1)

    markets = _split_markets(args.markets) or ["kr"]
    appstore_markets = _split_markets(args.appstore_markets) or ["kr"]

    start = parse_date(args.from_date) if args.from_date else None
    end = parse_date(args.to_date) if args.to_date else None
    if start is None or end is None:
        start, end = prompt_for_period()
    if start > end:
        start, end = end, start

    gp_id = args.google_play_app_id.strip() or None
    as_id = args.app_store_app_id.strip() or None

    if not gp_id:
        candidates = resolve_google_play_candidates(args.app_name, markets=markets, limit=8)
        gp_id = choose_candidate(candidates, "Google Play")
        if gp_id is None:
            print("Google Play 후보가 없어 해당 소스 수집을 생략합니다.")

    if not as_id:
        candidates = resolve_app_store_candidates(args.app_name, markets=appstore_markets, limit=8)
        as_id = choose_candidate(candidates, "App Store")
        if as_id is None:
            print("App Store 후보가 없어 해당 소스 수집을 생략합니다.")

    if not gp_id and not as_id:
        print("Google Play/App Store 앱 식별에 실패해 종료합니다.")
        sys.exit(1)

    config = PipelineConfig(
        app_name=args.app_name.strip(),
        app_slug=safe_slug(args.app_name),
        from_date=start,
        to_date=end,
        google_play_app_id=gp_id,
        app_store_app_id=as_id,
        markets=markets,
        appstore_markets=appstore_markets,
        max_reviews_per_store=args.max_reviews_per_store,
        output_dir=output_root,
        competitor_limit=args.competitor_limit,
        competitor_queries=parse_comma_list(args.competitor_queries),
        competitor_peer_set=args.competitor_peer_set,
        collect_market_intelligence=not args.no_market_intelligence,
    )

    raw_df, store_ratings, market_intelligence = collect_reviews(config)
    if raw_df.empty:
        print("수집된 리뷰가 없습니다. 앱/기간/국가를 다시 확인해 주세요.")
        sys.exit(2)

    analyzed_df = analyze_sentiment_and_theme(raw_df, use_llm=not args.no_llm)
    theme_summary = build_theme_summary(analyzed_df, top_per_tone=args.top_themes)
    pros_cons = build_pros_cons(theme_summary)
    artifact_paths = write_outputs(
        analyzed_df,
        theme_summary,
        pros_cons,
        config,
        store_ratings,
        market_intelligence=market_intelligence,
        create_dashboard=not args.skip_dashboard,
    )

    print("완료:")
    print(f"  - 출력 폴더: {artifact_paths['output_dir']}")
    if artifact_paths["dashboard_html"]:
        print(f"  - dashboard: {artifact_paths['dashboard_html']}")
    else:
        print("  - dashboard: 생성 생략(--skip-dashboard)")
    print(f"  - raw_csv: {artifact_paths['raw_csv']}")
    print(f"  - theme_csv: {artifact_paths['theme_csv']}")
    print(f"  - pros_cons_csv: {artifact_paths['pros_csv']}")
    print(f"  - store_ratings_csv: {artifact_paths['ratings_csv']}")
    print(f"  - market_intelligence_csv: {artifact_paths['market_intelligence_csv']}")
    print(f"  - quality_json: {artifact_paths['quality_json']}")
    print(f"  - excel: {artifact_paths['excel_path']}")


if __name__ == "__main__":
    main()
