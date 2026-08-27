"""Reusable review-analysis primitives for App Review Analysis Pipeline."""
from __future__ import annotations

import json
import re
import statistics
import time
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import sys

import pandas as pd
import requests

try:
    from google_play_scraper import (
        app as gp_app,
        reviews as gp_reviews,
        Sort as GP_SORT,
        search as gp_search,
    )
except Exception:  # pragma: no cover
    gp_reviews = None
    gp_app = None
    GP_SORT = None
    gp_search = None


DATE_FMT = "%Y-%m-%d"
APPSTORE_RSS_URL = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
APPSTORE_SEARCH_URL = "https://itunes.apple.com/search"
APPSTORE_REVIEW_BATCH = 50
GOOGLE_PLAY_REVIEW_BATCH = 200
GOOGLE_PLAY_APP_STORE_INSTALL_MIN = 1_000
SUPPORTED_SENTIMENT = {"긍정", "중립", "부정"}

MARKET_INTELLIGENCE_COLUMNS = [
    "source", "market", "query", "search_rank", "app_id", "title", "developer",
    "average_rating", "review_count", "installs", "installs_num", "category", "review_url",
    "is_target", "is_market_leader", "is_download_leader", "comment",
]

KR_BANKING_COMPETITOR_PEERS = [
    {
        "peer_name": "하나원큐",
        "google_play_app_id": "com.hanabank.oqf",
        "app_store_app_id": "6743190232",
        "app_store_query": "하나원큐",
    },
    {
        "peer_name": "KB국민은행 KB스타뱅킹",
        "google_play_app_id": "com.kbstar.kbbank",
        "app_store_query": "KB스타뱅킹",
    },
    {
        "peer_name": "신한은행 신한 SOL",
        "google_play_app_id": "com.shinhan.sbanking",
        "app_store_query": "신한 SOL뱅크",
    },
    {
        "peer_name": "우리은행 우리WON뱅킹",
        "google_play_app_id": "com.wooribank.smart.npib",
        "app_store_query": "우리WON뱅킹",
    },
    {
        "peer_name": "NH농협은행 NH스마트뱅킹",
        "google_play_app_id": "nh.smart.banking",
        "app_store_query": "NH스마트뱅킹",
    },
    {
        "peer_name": "카카오뱅크",
        "google_play_app_id": "com.kakaobank.channel",
        "app_store_query": "카카오뱅크",
    },
    {
        "peer_name": "토스",
        "google_play_app_id": "viva.republica.toss",
        "app_store_query": "토스",
    },
]


THEME_KEYWORDS: dict[str, list[str]] = {
    "안정성": ["오류", "에러", "에러발생", "크래시", "앱이 멈", "강제종료", "중단", "불안정"],
    "로그인/인증": ["로그인", "인증", "본인확인", "휴대폰", "비밀번호", "보안", "핀", "otp", "문자", "카드", "공인인증"],
    "속도/성능": ["느리", "버벅", "지연", "로딩", "속도", "성능", "딜레이", "터지", "지연", "반응 느림", "끊김"],
    "UI/UX": ["디자인", "화면", "버튼", "레이아웃", "메뉴", "배치", "직관", "사용성", "접근성", "폰트", "알림창"],
    "기능": ["기능", "작동", "추가", "삭제", "이체", "송금", "예약", "알림", "계좌", "입출금", "채팅", "조회"],
    "고객응대": ["센터", "상담", "문의", "채팅봇", "응답", "대응", "피드백", "상담원", "콜센터"],
    "인증/결제": ["카드", "결제", "인증", "간편결제", "환전", "한도", "한도", "충전", "매수", "매도"],
    "접근성": ["한글", "번역", "지원", "언어", "영어", "폰트", "확대", "자막", "보이스"],
}


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class PipelineConfig:
    app_name: str
    app_slug: str
    from_date: datetime
    to_date: datetime
    google_play_app_id: str | None = None
    app_store_app_id: str | None = None
    markets: list[str] | None = None
    appstore_markets: list[str] | None = None
    max_reviews_per_store: int = 800
    timeout_seconds: int = 20
    output_dir: Path | None = None
    top_themes: int = 8
    competitor_limit: int = 8
    competitor_queries: list[str] | None = None
    competitor_peer_set: str = "auto"
    collect_market_intelligence: bool = True


def parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FMT)
    except ValueError:
        return None


def safe_slug(value: str, length: int = 50) -> str:
    norm = re.sub(r"[^\w가-힣a-zA-Z0-9_-]+", "_", value.strip().replace(" ", "_"), flags=re.ASCII)
    if not norm:
        norm = "app_review"
    return norm[:length].strip("_")


def ensure_output_dir(path: Path | None, app_slug: str) -> Path:
    if path is None:
        path = Path.cwd() / "app_review_outputs"
    output_dir = path / f"{app_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def parse_datetime(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none"}:
        return None
    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in candidates:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            return dt
        except Exception:
            pass
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except Exception:
            return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return int(float(text))
    except Exception:
        return None


def parse_comma_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def in_range(dt: datetime | None, start: datetime, end: datetime) -> bool:
    if dt is None:
        return False
    start_ts = datetime.combine(start.date(), datetime.min.time())
    end_ts = datetime.combine(end.date(), datetime.max.time())
    return start_ts <= dt <= end_ts


def _read_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def resolve_google_play_candidates(query: str, markets: list[str], limit: int = 8) -> list[dict[str, Any]]:
    if gp_search is None:
        return []
    candidates: list[dict[str, Any]] = []
    for market in markets:
        try:
            results = gp_search(query, lang="ko", country=market, n_hits=limit)
            for row in results:
                app_id = row.get("appId") or row.get("packageName")
                if not app_id:
                    continue
                candidates.append(
                    {
                        "platform": "google_play",
                        "app_id": app_id,
                        "title": _read_text(row.get("title")),
                        "developer": _read_text(row.get("developer", "") or row.get("developerId")),
                        "market": market,
                        "score": row.get("score"),
                        "url": f"https://play.google.com/store/apps/details?id={app_id}",
                    }
                )
        except Exception:
            continue
    # 중복 제거 (앱ID 기준)
    uniq = {}
    for c in candidates:
        uniq[c["app_id"]] = c
    return list(uniq.values())[:limit]


def resolve_app_store_candidates(query: str, markets: list[str], limit: int = 8) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for market in markets:
        params = {
            "term": query,
            "country": market,
            "entity": "software",
            "media": "software",
            "limit": limit,
        }
        try:
            resp = requests.get(APPSTORE_SEARCH_URL, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            for row in data.get("results", []):
                track_id = row.get("trackId")
                bundle = row.get("bundleId")
                app_id = str(track_id) if track_id else bundle
                if not app_id:
                    continue
                candidates.append(
                    {
                        "platform": "app_store",
                        "app_id": str(app_id),
                        "title": _read_text(row.get("trackName")),
                        "developer": _read_text(row.get("sellerName")),
                        "market": market,
                        "score": row.get("averageUserRating"),
                        "url": row.get("trackViewUrl", ""),
                    }
                )
        except Exception:
            continue
    uniq = {}
    for c in candidates:
        uniq[(c["app_id"], c["market"])] = c
    return list(uniq.values())[:limit]


def _fetch_google_play_app_meta(app_id: str, markets: list[str] | None = None) -> dict[str, dict[str, Any]]:
    if gp_app is None:
        return {}
    markets = markets or ["kr"]
    for market in markets:
        try:
            metadata = gp_app(app_id, lang="ko", country=market)
        except Exception:
            continue
        if not isinstance(metadata, dict):
            continue
        avg = _to_float(metadata.get("score") or metadata.get("scoreText"))
        cnt = _to_int(metadata.get("ratings") or metadata.get("ratingsText") or metadata.get("reviews"))
        installs_text = _read_text(metadata.get("installs") or metadata.get("installsText"))
        category = _read_text(metadata.get("genre"))
        installs_num = _to_int(str(installs_text).replace("+", "").replace(",", "")) if installs_text else None
        return {
            "title": _read_text(metadata.get("title")),
            "developer": _read_text(metadata.get("developer")),
            "average_rating": avg,
            "review_count": cnt,
            "installs_text": installs_text,
            "installs_num": installs_num,
            "category": category,
            "market": market,
        }
    return {}


def _fetch_google_play_store_rating(app_id: str, markets: list[str] | None = None) -> dict[str, dict[str, Any]]:
    if gp_app is None:
        return {}
    markets = markets or ["kr"]
    for market in markets:
        try:
            metadata = _fetch_google_play_app_meta(app_id, [market])
        except Exception:
            continue
        if not metadata:
            continue
        avg = metadata.get("average_rating")
        cnt = metadata.get("review_count")
        if avg is None and cnt is None:
            continue
        return {
            "average_rating": avg,
            "review_count": cnt,
            "market": market,
        }
    return {}


def _fetch_app_store_rating(app_id: str, markets: list[str] | None = None) -> dict[str, dict[str, Any]]:
    markets = markets or ["kr"]
    params_base = {"entity": "software", "limit": 1}
    if app_id.isdigit():
        params_base["id"] = app_id
    else:
        params_base["bundleId"] = app_id
    for market in markets:
        params = dict(params_base)
        params["country"] = market
        try:
            payload = requests.get("https://itunes.apple.com/lookup", params=params, timeout=20).json()
            results = payload.get("results", [])
            if not results:
                continue
            result = results[0]
            avg = _to_float(result.get("averageUserRating"))
            cnt = _to_int(result.get("userRatingCount"))
            if avg is None:
                avg = _to_float(result.get("averageUserRatingForCurrentVersion"))
            if cnt is None:
                cnt = _to_int(result.get("userRatingCountForCurrentVersion"))
            if avg is None and cnt is None:
                continue
            return {
                "average_rating": avg,
                "review_count": cnt,
                "market": market,
                "category": _read_text(result.get("primaryGenreName")),
            }
        except Exception:
            continue
    return {}


def _google_play_collect(
    app_id: str,
    config: PipelineConfig,
    market: str = "kr",
    lang: str = "ko",
) -> list[dict[str, Any]]:
    if gp_reviews is None:
        return []
    records = []
    continuation = None
    while len(records) < max(config.max_reviews_per_store, 1):
        remaining = config.max_reviews_per_store - len(records) if config.max_reviews_per_store > 0 else GOOGLE_PLAY_REVIEW_BATCH
        batch_size = min(GOOGLE_PLAY_REVIEW_BATCH, remaining if remaining > 0 else GOOGLE_PLAY_REVIEW_BATCH)

        try:
            if continuation is None:
                result, token = gp_reviews(
                    app_id,
                    lang=lang,
                    country=market,
                    sort=GP_SORT.NEWEST,
                    count=batch_size,
                )
            else:
                result, token = gp_reviews(
                    app_id,
                    lang=lang,
                    country=market,
                    sort=GP_SORT.NEWEST,
                    count=batch_size,
                    continuation_token=continuation,
                )
        except TypeError:
            break
        except Exception:
            break
        if not result:
            break

        should_break_on_older = False
        for row in result:
            review_time = parse_datetime(row.get("at"))
            if not review_time:
                continue
            if review_time < config.from_date:
                should_break_on_older = True
                break
            if not in_range(review_time, config.from_date, config.to_date):
                continue
            records.append(
                {
                    "source": "google_play",
                    "app_name": config.app_name,
                    "app_id": app_id,
                    "review_id": str(row.get("reviewId", "")),
                    "review_title": "",
                    "review_body": _read_text(row.get("content")),
                    "rating": int(row.get("score", 0) or 0),
                    "review_date": review_time.strftime(DATE_FMT) if review_time else "",
                    "app_version": _read_text(row.get("appVersion")),
                    "helpful_count": int(row.get("thumbsUpCount", 0) or 0),
                    "language": lang,
                    "review_url": f"https://play.google.com/store/apps/details?id={app_id}",
                }
            )
            if len(records) >= max(config.max_reviews_per_store, 1):
                break

        if should_break_on_older:
            break
        if len(records) >= config.max_reviews_per_store:
            break
        if not token or token == continuation:
            break
        continuation = token
        time.sleep(0.15)
    return records


def _app_store_collect(
    app_id: str,
    config: PipelineConfig,
    market: str = "kr",
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    max_pages = min(10, max(1, (config.max_reviews_per_store // APPSTORE_REVIEW_BATCH) + 1))
    consecutive_failures = 0
    for page in range(1, max_pages + 1):
        url = APPSTORE_RSS_URL.format(country=market, page=page, app_id=app_id)
        try:
            payload = None
            for attempt in range(3):
                try:
                    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=config.timeout_seconds)
                    resp.raise_for_status()
                    payload = resp.json()
                    consecutive_failures = 0
                    break
                except Exception:
                    time.sleep(0.5 * (attempt + 1))
            if payload is None:
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    break
                continue
            entries = payload.get("feed", {}).get("entry", [])
            if page == 1 and entries:
                entries = entries[1:]  # first entry is app metadata
            if not entries:
                break

            for row in entries:
                def _label(v: dict[str, Any]) -> str:
                    return _read_text(v.get("label", ""))

                review_date = parse_datetime(_label(row.get("updated", {})))
                if not in_range(review_date, config.from_date, config.to_date):
                    continue
                records.append(
                    {
                        "source": "app_store",
                        "app_name": config.app_name,
                        "app_id": app_id,
                        "review_id": _label(row.get("id", {})),
                        "review_title": _label(row.get("title", {})),
                        "review_body": _label(row.get("content", {})),
                        "rating": int(_label(row.get("im:rating", {})) or 0),
                        "review_date": review_date.strftime(DATE_FMT) if review_date else "",
                        "app_version": _label(row.get("im:version", {})),
                        "helpful_count": int(_label(row.get("im:voteSum", {})) or 0),
                        "language": row.get("im:language", {}).get("label", ""),
                        "review_url": "",
                    }
                )
                if len(records) >= config.max_reviews_per_store:
                    break
            if len(records) >= config.max_reviews_per_store:
                break
            time.sleep(0.3)
        except Exception:
            consecutive_failures += 1
            if consecutive_failures >= 2:
                break
            continue
    return records


def _collect_market_ranked_google_play_apps(
    query: str,
    config: PipelineConfig,
    market: str = "kr",
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    if gp_search is None:
        return []
    max_items = max_items or config.competitor_limit
    max_items = min(max_items, 20)
    rows: list[dict[str, Any]] = []
    try:
        results = gp_search(query, lang="ko", country=market, n_hits=max_items)
    except Exception:
        return []
    for rank, row in enumerate(results[:max_items], start=1):
        app_id = row.get("appId") or row.get("packageName")
        if not app_id:
            continue
        title = _read_text(row.get("title"))
        developer = _read_text(row.get("developer", "") or row.get("developerId"))
        meta = _fetch_google_play_app_meta(str(app_id), [market])
        row_payload = {
            "source": "google_play",
            "market": market,
            "query": query,
            "search_rank": rank,
            "app_id": str(app_id),
            "title": title,
            "developer": developer,
            "average_rating": meta.get("average_rating"),
            "review_count": meta.get("review_count"),
            "installs": meta.get("installs_text") if meta else "",
            "installs_num": meta.get("installs_num") if meta else None,
            "category": meta.get("category") if meta else "",
            "review_url": f"https://play.google.com/store/apps/details?id={app_id}",
        }
        if title:
            rows.append(row_payload)
    return rows


def _collect_market_ranked_app_store_apps(
    query: str,
    config: PipelineConfig,
    market: str = "kr",
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    max_items = max_items or config.competitor_limit
    max_items = min(max_items, 20)
    rows: list[dict[str, Any]] = []
    params = {
        "term": query,
        "country": market,
        "entity": "software",
        "media": "software",
        "limit": max_items,
    }
    try:
        payload = requests.get(APPSTORE_SEARCH_URL, params=params, timeout=20).json()
    except Exception:
        return []
    results = payload.get("results", [])
    if not results:
        return []
    for rank, row in enumerate(results[:max_items], start=1):
        track_id = row.get("trackId")
        bundle = row.get("bundleId")
        app_id = str(track_id) if track_id else str(bundle or "")
        if not app_id:
            continue
        rows.append(
            {
                "source": "app_store",
                "market": market,
                "query": query,
                "search_rank": rank,
                "app_id": app_id,
                "title": _read_text(row.get("trackName")),
                "developer": _read_text(row.get("sellerName")),
                "average_rating": _to_float(row.get("averageUserRating")),
                "review_count": _to_int(row.get("userRatingCount")),
                "installs": None,
                "installs_num": None,
                "category": _read_text(row.get("primaryGenreName")),
                "review_url": _read_text(row.get("trackViewUrl")),
            }
        )
    return rows


def _empty_market_intelligence_df() -> pd.DataFrame:
    return pd.DataFrame(columns=MARKET_INTELLIGENCE_COLUMNS)


def _is_kr_banking_peer_set(config: PipelineConfig) -> bool:
    peer_set = (config.competitor_peer_set or "auto").strip().lower()
    if peer_set in {"banking_kr", "kr_banking", "banking"}:
        return True
    if peer_set not in {"", "auto"}:
        return False
    target_ids = {config.google_play_app_id or "", config.app_store_app_id or ""}
    peer_ids = {
        str(peer.get("google_play_app_id") or "")
        for peer in KR_BANKING_COMPETITOR_PEERS
    } | {
        str(peer.get("app_store_app_id") or "")
        for peer in KR_BANKING_COMPETITOR_PEERS
    }
    if target_ids & peer_ids:
        return True
    lowered_name = config.app_name.lower()
    return any(token in lowered_name for token in ["하나", "은행", "bank", "1q", "원큐"])


def _collect_registered_google_play_peer_apps(
    config: PipelineConfig,
    target_google_app_id: str | None,
    market: str = "kr",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = max(1, min(config.competitor_limit, len(KR_BANKING_COMPETITOR_PEERS)))
    for rank, peer in enumerate(KR_BANKING_COMPETITOR_PEERS[:limit], start=1):
        app_id = str(peer.get("google_play_app_id") or "")
        if not app_id:
            continue
        meta = _fetch_google_play_app_meta(app_id, [market])
        if not meta:
            continue
        rows.append(
            {
                "source": "google_play",
                "market": market,
                "query": "banking_kr",
                "search_rank": rank,
                "app_id": app_id,
                "title": meta.get("title") or peer["peer_name"],
                "developer": meta.get("developer") or "",
                "average_rating": meta.get("average_rating"),
                "review_count": meta.get("review_count"),
                "installs": meta.get("installs_text") or "",
                "installs_num": meta.get("installs_num"),
                "category": meta.get("category") or "",
                "review_url": f"https://play.google.com/store/apps/details?id={app_id}",
                "is_target": bool(target_google_app_id and app_id == str(target_google_app_id)),
            }
        )
    return rows


def _lookup_app_store_row(app_id: str | None, query: str, market: str) -> dict[str, Any] | None:
    try:
        if app_id:
            payload = requests.get(
                "https://itunes.apple.com/lookup",
                params={"id": app_id, "country": market, "entity": "software", "limit": 1},
                timeout=20,
            ).json()
            results = payload.get("results", [])
            if results:
                return results[0]
        payload = requests.get(
            APPSTORE_SEARCH_URL,
            params={"term": query, "country": market, "entity": "software", "media": "software", "limit": 5},
            timeout=20,
        ).json()
        results = payload.get("results", [])
        return results[0] if results else None
    except Exception:
        return None


def _collect_registered_app_store_peer_apps(
    config: PipelineConfig,
    target_app_store_app_id: str | None,
    market: str = "kr",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = max(1, min(config.competitor_limit, len(KR_BANKING_COMPETITOR_PEERS)))
    for rank, peer in enumerate(KR_BANKING_COMPETITOR_PEERS[:limit], start=1):
        query = str(peer.get("app_store_query") or peer.get("peer_name") or "")
        app_id_hint = str(peer.get("app_store_app_id") or "")
        result = _lookup_app_store_row(app_id_hint or None, query, market)
        if not result:
            continue
        track_id = result.get("trackId")
        bundle = result.get("bundleId")
        app_id = str(track_id) if track_id else str(bundle or "")
        if not app_id:
            continue
        rows.append(
            {
                "source": "app_store",
                "market": market,
                "query": "banking_kr",
                "search_rank": rank,
                "app_id": app_id,
                "title": _read_text(result.get("trackName")) or peer["peer_name"],
                "developer": _read_text(result.get("sellerName")),
                "average_rating": _to_float(result.get("averageUserRating")),
                "review_count": _to_int(result.get("userRatingCount")),
                "installs": None,
                "installs_num": None,
                "category": _read_text(result.get("primaryGenreName")),
                "review_url": _read_text(result.get("trackViewUrl")),
                "is_target": bool(target_app_store_app_id and app_id == str(target_app_store_app_id)),
            }
        )
    return rows


def collect_market_intelligence(config: PipelineConfig, target_google_app_id: str | None, target_app_store_app_id: str | None) -> pd.DataFrame:
    if not config.collect_market_intelligence:
        return _empty_market_intelligence_df()

    queries = parse_comma_list(",".join(config.competitor_queries or []))
    if not queries:
        queries = [config.app_name]
    limit = max(1, min(config.competitor_limit, 20))

    rows: list[dict[str, Any]] = []
    use_kr_banking_peer_set = _is_kr_banking_peer_set(config)
    if use_kr_banking_peer_set and target_google_app_id:
        for market in config.markets or ["kr"]:
            rows.extend(_collect_registered_google_play_peer_apps(config, target_google_app_id, market=market))
    elif target_google_app_id:
        for query in queries:
            for market in config.markets or ["kr"]:
                rows.extend(_collect_market_ranked_google_play_apps(query, config, market=market, max_items=limit))
    if use_kr_banking_peer_set and target_app_store_app_id:
        for market in config.appstore_markets or ["kr"]:
            rows.extend(_collect_registered_app_store_peer_apps(config, target_app_store_app_id, market=market))
    elif target_app_store_app_id:
        for query in queries:
            for market in config.appstore_markets or ["kr"]:
                rows.extend(_collect_market_ranked_app_store_apps(query, config, market=market, max_items=limit))

    if not rows:
        return _empty_market_intelligence_df()

    df = pd.DataFrame(rows)
    df["search_rank"] = pd.to_numeric(df["search_rank"], errors="coerce").fillna(0).astype(int)
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")
    df["installs_num"] = pd.to_numeric(df["installs_num"], errors="coerce")
    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce")

    if "is_target" not in df.columns:
        df["is_target"] = False
    else:
        df["is_target"] = df["is_target"].fillna(False).astype(bool)
    if target_google_app_id:
        df.loc[(df["source"] == "google_play") & (df["app_id"] == str(target_google_app_id)), "is_target"] = True
    if target_app_store_app_id:
        df.loc[(df["source"] == "app_store") & (df["app_id"] == str(target_app_store_app_id)), "is_target"] = True

    if use_kr_banking_peer_set:
        df["_market_sort_primary"] = df["installs_num"].fillna(0)
        df["_market_sort_secondary"] = df["review_count"].fillna(0)
        df = df.sort_values(
            ["source", "market", "_market_sort_primary", "_market_sort_secondary", "average_rating"],
            ascending=[True, True, False, False, False],
        ).reset_index(drop=True)
        df["search_rank"] = df.groupby(["source", "market"]).cumcount() + 1
        df = df.drop(columns=["_market_sort_primary", "_market_sort_secondary"], errors="ignore")
    else:
        df = df.sort_values(["source", "query", "search_rank", "market"], ascending=[True, True, True, True]).reset_index(drop=True)

    def mark_flags(group: pd.DataFrame, rank_col: str = "search_rank") -> pd.DataFrame:
        group = group.sort_values(rank_col).copy()
        group["is_market_leader"] = False
        group["is_download_leader"] = False
        if not group.empty:
            group.loc[group.index[0], "is_market_leader"] = True
            if group["installs_num"].notna().any():
                max_inst = group["installs_num"].max()
                if pd.notna(max_inst):
                    group.loc[group["installs_num"] == max_inst, "is_download_leader"] = True
            elif group["review_count"].notna().any():
                max_review = group["review_count"].max()
                if pd.notna(max_review):
                    group.loc[group["review_count"] == max_review, "is_download_leader"] = True
        return group

    df["is_market_leader"] = False
    df["is_download_leader"] = False
    flag_group_cols = ["source", "market"] if use_kr_banking_peer_set else ["source", "query"]
    for _, part in df.groupby(flag_group_cols):
        ranked = mark_flags(part)
        df.loc[ranked.index, "is_market_leader"] = ranked["is_market_leader"]
        df.loc[ranked.index, "is_download_leader"] = ranked["is_download_leader"]

    comments = []
    for _, row in df.iterrows():
        tags = []
        if bool(row["is_market_leader"]):
            tags.append("피어셋 1위" if use_kr_banking_peer_set else "검색 1위")
        if bool(row["is_download_leader"]):
            tags.append("다운로드 추정 상위")
        if bool(row["is_target"]):
            tags.append("타깃 앱")
        comments.append(", ".join(tags))
    df["comment"] = comments

    # keep best-ranked row for duplicated app across query/market duplicates
    df = (
        df.sort_values(["source", "app_id", "search_rank", "market"])
        .drop_duplicates(subset=["source", "app_id"], keep="first")
        .reset_index(drop=True)
    )
    if use_kr_banking_peer_set:
        df = df.sort_values(["source", "market", "search_rank"], ascending=[True, True, True]).reset_index(drop=True)
    else:
        df = df.sort_values(["source", "query", "search_rank", "market"], ascending=[True, True, True, True]).reset_index(drop=True)
    return df


def collect_reviews(config: PipelineConfig) -> tuple[pd.DataFrame, dict[str, dict[str, Any]], pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    store_ratings: dict[str, dict[str, Any]] = {}
    if config.google_play_app_id:
        rating_meta = _fetch_google_play_store_rating(config.google_play_app_id, config.markets or ["kr"])
        if rating_meta:
            store_ratings["google_play"] = rating_meta
        else:
            store_ratings["google_play"] = {}
    if config.app_store_app_id:
        rating_meta = _fetch_app_store_rating(config.app_store_app_id, config.appstore_markets or ["kr"])
        if rating_meta:
            store_ratings["app_store"] = rating_meta
        else:
            store_ratings["app_store"] = {}

    market_intelligence = collect_market_intelligence(config, config.google_play_app_id, config.app_store_app_id)

    if config.google_play_app_id:
        for market in config.markets or ["kr"]:
            rows.extend(_google_play_collect(config.google_play_app_id, config, market=market))

    if config.app_store_app_id:
        for market in config.appstore_markets or ["kr"]:
            rows.extend(_app_store_collect(config.app_store_app_id, config, market=market))

    if not rows:
        return (
            pd.DataFrame(
                columns=[
                    "source", "app_name", "app_id", "review_id", "review_title", "review_body",
                    "rating", "review_date", "app_version", "helpful_count", "language", "review_url",
                ]
            ),
            store_ratings,
            market_intelligence,
        )

    df = pd.DataFrame(rows)
    df["review_body"] = df["review_body"].fillna("").astype(str).str.strip()
    df["review_id"] = df["review_id"].fillna("").astype(str).str.strip()

    dedupe_before = len(df)
    df = df.drop_duplicates(subset=["source", "review_id"]).copy()
    df["dedupe_removed"] = dedupe_before - len(df)
    df["has_opinion_text"] = df["review_body"].str.len().gt(0).astype(int)

    df["review_date_parsed"] = df["review_date"].apply(parse_datetime)
    df = df.sort_values("review_date_parsed", ascending=False).reset_index(drop=True)
    return df, store_ratings, market_intelligence


def classify_sentiment_by_rules(text: str, rating: int) -> tuple[str, float, list[str], str]:
    lower = text.lower()
    positive_markers = ["좋다", "편하다", "안정", "빠르", "간편", "만족", "좋음", "추천", "좋아요"]
    negative_markers = ["불편", "느리", "문제", "오류", "에러", "실패", "멈춰", "버그", "안됨", "안돼", "안되"]
    pos = sum(1 for w in positive_markers if w in lower)
    neg = sum(1 for w in negative_markers if w in lower)
    if neg >= 2:
        sentiment = "부정"
        confidence = 0.77
    elif pos >= 2 and neg == 0:
        sentiment = "긍정"
        confidence = 0.74
    elif rating >= 4 and neg == 0:
        sentiment = "긍정"
        confidence = 0.68
    elif rating <= 2 and pos == 0:
        sentiment = "부정"
        confidence = 0.66
    else:
        sentiment = "중립"
        confidence = 0.62
    themes = infer_themes_from_text(text)
    tone = "mixed" if len(themes) > 1 else themes[0] if themes else "기타"
    return sentiment, confidence, themes, tone


def infer_themes_from_text(text: str, top_k: int = 3) -> list[str]:
    lower = text.lower()
    themes = []
    for theme, keyword_list in THEME_KEYWORDS.items():
        if any(k in lower for k in keyword_list):
            themes.append(theme)
            if len(themes) >= top_k:
                break
    if not themes:
        themes = ["기타"]
    return themes


def _extract_json_from_text(text: str) -> str | None:
    match = re.search(r"\[[\\s\\S]*\]", text)
    if not match:
        return None
    candidate = match.group(0)
    try:
        json.loads(candidate)
        return candidate
    except Exception:
        return None


def _gemini_analyze_batch(rows: list[dict[str, Any]], api_key: str, batch_size: int = 25) -> dict[str, dict[str, Any]]:
    import google.generativeai as genai  # type: ignore

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt_tpl = (
        "너는 UX 리뷰 분석가다. 아래 리뷰 배열을 감성/테마로 분류한다.\n"
        "반드시 JSON 배열만 반환한다.\n"
        "각 원소: {\"review_id\": \"...\", \"sentiment\": \"긍정|중립|부정\", \"confidence\": 0-1 숫자,\n"
        "\"themes\": [\"테마\", \"...\"], \"summary\": \"한줄 요약\"}\n"
        "허용된 테마: 안정성, 로그인/인증, 속도/성능, UI/UX, 기능, 고객응대, 인증/결제, 접근성, 기타\n\n"
        "입력:\n"
        "{payload}\n"
    )

    results: dict[str, dict[str, Any]] = {}
    total = len(rows)

    for start in range(0, total, batch_size):
        batch = rows[start : start + batch_size]
        if not batch:
            continue
        payload = json.dumps(batch, ensure_ascii=False)
        try:
            resp = model.generate_content(prompt_tpl.format(payload=payload))
            parsed_text = resp.text or ""
            raw = _extract_json_from_text(parsed_text)
            if not raw:
                continue
            parsed = json.loads(raw)
            for item in parsed:
                rid = str(item.get("review_id", "")).strip()
                if not rid:
                    continue
                sentiment = str(item.get("sentiment", "중립")).strip()
                if sentiment not in SUPPORTED_SENTIMENT:
                    sentiment = "중립"
                themes = item.get("themes") or []
                if isinstance(themes, str):
                    themes = [t.strip() for t in themes.split(",") if t.strip()]
                if not themes:
                    themes = ["기타"]
                results[rid] = {
                    "sentiment": sentiment,
                    "confidence": float(item.get("confidence", 0.5)),
                    "themes": themes[:3],
                    "summary": _read_text(item.get("summary")),
                }
        except Exception:
            continue
    return results


def analyze_sentiment_and_theme(df: pd.DataFrame, use_llm: bool = True) -> pd.DataFrame:
    if df.empty:
        df["sentiment"] = []
        df["sentiment_confidence"] = []
        df["themes"] = []
        df["theme_summary"] = []
        return df

    df = df.copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

    api_key = __import__("os").environ.get("GEMINI_API_KEY", "")
    llm_map: dict[str, dict[str, Any]] = {}
    if use_llm and api_key:
        sample_rows = [
            {
                "review_id": row["review_id"],
                "source": row["source"],
                "rating": int(row["rating"]),
                "text": row["review_body"][:500],
            }
            for _, row in df.iterrows()
        ]
        llm_map = _gemini_analyze_batch(sample_rows, api_key)

    sentiments: list[str] = []
    confidences: list[float] = []
    themes_list: list[list[str]] = []
    summaries: list[str] = []

    for _, row in df.iterrows():
        review_id = str(row["review_id"])
        sentiment = None
        confidence = 0.0
        themes = None
        summary = ""
        if review_id in llm_map:
            pred = llm_map[review_id]
            sentiment = pred.get("sentiment")
            confidence = pred.get("confidence", 0.5)
            themes = pred.get("themes") or ["기타"]
            summary = pred.get("summary", "")
        if sentiment is None:
            sentiment, confidence, themes, _ = classify_sentiment_by_rules(_read_text(row["review_body"]), int(row["rating"]))
            if not summary:
                summary = _read_text(row["review_body"][:80])
        sentiments.append(sentiment or "중립")
        confidences.append(float(confidence))
        themes_list.append(list(themes) if themes else ["기타"])
        summaries.append(summary)

    df["sentiment"] = sentiments
    df["sentiment_confidence"] = confidences
    df["themes"] = [",".join(v) for v in themes_list]
    df["themes_list"] = themes_list
    df["theme_summary"] = summaries
    return df


def build_theme_summary(df: pd.DataFrame, top_per_tone: int = 8) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=["tone", "theme", "count", "share_pct", "avg_rating", "representative_quotes"]
        )

    exploded_rows = []
    for _, row in df.iterrows():
        rating = float(row["rating"]) if pd.notna(row["rating"]) else None
        body = _read_text(row["review_body"])[:180]
        themes = row["themes_list"] if isinstance(row["themes_list"], list) else ["기타"]
        for t in themes:
            exploded_rows.append(
                {
                    "tone": row["sentiment"],
                    "theme": t,
                    "rating": rating,
                    "review_body": body,
                }
            )

    if not exploded_rows:
        return pd.DataFrame(
            columns=["tone", "theme", "count", "share_pct", "avg_rating", "representative_quotes"]
        )

    expanded = pd.DataFrame(exploded_rows)
    output_rows = []
    for tone, tone_df in expanded.groupby("tone"):
        total = len(tone_df)
        for theme, theme_df in tone_df.groupby("theme"):
            cnt = len(theme_df)
            ratings = [v for v in theme_df["rating"].tolist() if v is not None and pd.notna(v)]
            avg_rating = round(statistics.mean(ratings), 2) if ratings else None
            quotes = list(dict.fromkeys([q for q in theme_df["review_body"].tolist() if q][:3]))
            output_rows.append(
                {
                    "tone": tone,
                    "theme": theme,
                    "count": cnt,
                    "share_pct": round((cnt / total * 100), 2) if total else 0.0,
                    "avg_rating": avg_rating,
                    "representative_quotes": " | ".join(quotes),
                }
            )

    summary_df = pd.DataFrame(output_rows).sort_values(["tone", "count"], ascending=[True, False]).reset_index(drop=True)
    return summary_df.groupby("tone").head(top_per_tone).reset_index(drop=True)


def build_pros_cons(df_summary: pd.DataFrame) -> pd.DataFrame:
    if df_summary.empty:
        return pd.DataFrame(columns=["type", "theme", "count", "avg_rating", "share_pct", "representative_quotes"])

    output = []
    for tone in ["긍정", "부정"]:
        df_tone = df_summary[df_summary["tone"] == tone].sort_values("count", ascending=False)
        for _, row in df_tone.iterrows():
            output.append(
                {
                    "type": tone,
                    "theme": row["theme"],
                    "count": int(row["count"]),
                    "avg_rating": row["avg_rating"],
                    "share_pct": row["share_pct"],
                    "representative_quotes": row["representative_quotes"],
                }
            )
    return pd.DataFrame(output)


def build_source_coverage(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in ("google_play", "app_store"):
        if df.empty or "source" not in df.columns:
            source_df = pd.DataFrame()
        else:
            source_df = df[df["source"] == source]
        if source_df.empty:
            rows.append(
                {
                    "source": source,
                    "review_count": 0,
                    "reviews_with_rating": 0,
                    "reviews_with_opinion": 0,
                    "min_date": "",
                    "max_date": "",
                    "coverage_note": "",
                }
            )
            continue
        opinion_count = (
            int(source_df["has_opinion_text"].sum())
            if "has_opinion_text" in source_df.columns
            else int(source_df["review_body"].astype(str).str.strip().ne("").sum())
        )
        rows.append(
            {
                "source": source,
                "review_count": int(len(source_df)),
                "reviews_with_rating": int(pd.to_numeric(source_df["rating"], errors="coerce").gt(0).sum()),
                "reviews_with_opinion": opinion_count,
                "min_date": str(source_df["review_date"].min()),
                "max_date": str(source_df["review_date"].max()),
                "coverage_note": "",
            }
        )
    parsed_min_dates = [
        parse_datetime(row.get("min_date"))
        for row in rows
        if row.get("review_count", 0) and row.get("min_date")
    ]
    parsed_min_dates = [dt for dt in parsed_min_dates if dt is not None]
    earliest_date = min(parsed_min_dates).date() if parsed_min_dates else None
    for row in rows:
        source_min = parse_datetime(row.get("min_date"))
        if row.get("source") == "app_store" and row.get("review_count", 0) and earliest_date and source_min:
            if source_min.date() > earliest_date:
                row["coverage_note"] = (
                    "Apple 공개 RSS는 최신순으로 노출되는 제한된 페이지까지만 내려오므로, "
                    f"이번 대시보드의 App Store 시작일은 요청 시작일이 아니라 RSS에서 확보된 가장 오래된 리뷰 날짜({row.get('min_date')})입니다."
                )
    return rows


def build_rating_stats(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_frames: list[tuple[str, pd.DataFrame]] = [("overall", df)]
    if not df.empty and "source" in df.columns:
        source_frames.extend((source, df[df["source"] == source]) for source in ["google_play", "app_store"])

    for source, source_df in source_frames:
        ratings = pd.to_numeric(source_df.get("rating", pd.Series(dtype=float)), errors="coerce").dropna()
        ratings = ratings[ratings > 0]
        if ratings.empty:
            rows.append(
                {
                    "source": source,
                    "count": 0,
                    "avg_rating": None,
                    "rating_std": None,
                    "min_rating": None,
                    "max_rating": None,
                }
            )
            continue
        rows.append(
            {
                "source": source,
                "count": int(len(ratings)),
                "avg_rating": round(float(ratings.mean()), 2),
                "rating_std": round(float(ratings.std(ddof=1)), 2) if len(ratings) > 1 else 0.0,
                "min_rating": int(ratings.min()),
                "max_rating": int(ratings.max()),
            }
        )
    return rows


def build_rating_distribution_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_frames: list[tuple[str, pd.DataFrame]] = [("overall", df)]
    if not df.empty and "source" in df.columns:
        source_frames.extend((source, df[df["source"] == source]) for source in ["google_play", "app_store"])

    for source, source_df in source_frames:
        ratings = pd.to_numeric(source_df.get("rating", pd.Series(dtype=float)), errors="coerce").dropna()
        ratings = ratings[ratings > 0].astype(int)
        total = int(len(ratings))
        for rating in range(1, 6):
            count = int((ratings == rating).sum())
            rows.append(
                {
                    "source": source,
                    "rating": rating,
                    "count": count,
                    "share_pct": round((count / total * 100), 2) if total else 0.0,
                }
            )
    return rows


def build_period_trend(df: pd.DataFrame, freq: str = "M") -> list[dict[str, Any]]:
    if df.empty:
        return []
    working = df[["source", "review_date", "rating"]].copy()
    working["review_date"] = pd.to_datetime(working["review_date"], errors="coerce")
    working["rating"] = pd.to_numeric(working["rating"], errors="coerce")
    working = working.dropna(subset=["review_date", "rating"])
    working = working[working["rating"] > 0]
    if working.empty:
        return []

    working["period"] = working["review_date"].dt.to_period(freq).astype(str)
    frames = [("overall", working)]
    frames.extend((source, working[working["source"] == source]) for source in ["google_play", "app_store"])

    rows: list[dict[str, Any]] = []
    for source, source_df in frames:
        if source_df.empty:
            continue
        grouped = source_df.groupby("period")["rating"].agg(["count", "mean", "std"]).reset_index()
        for _, row in grouped.iterrows():
            rows.append(
                {
                    "source": source,
                    "period": row["period"],
                    "review_count": int(row["count"]),
                    "avg_rating": round(float(row["mean"]), 2),
                    "rating_std": round(float(row["std"]), 2) if pd.notna(row["std"]) else 0.0,
                }
            )
    return sorted(rows, key=lambda row: (row["period"], row["source"]))


def build_dashboard_insights(
    df: pd.DataFrame,
    theme_summary: pd.DataFrame,
    rating_stats: list[dict[str, Any]],
    period_trend: list[dict[str, Any]],
    source_coverage: list[dict[str, Any]],
    market_intelligence: pd.DataFrame | None = None,
) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    stats = {row["source"]: row for row in rating_stats}
    overall = stats.get("overall", {})
    avg = overall.get("avg_rating")
    std = overall.get("rating_std")
    if avg is not None:
        if std is not None and std >= 1.5:
            body = f"전체 평균은 {avg:.2f}점이지만 표준편차가 {std:.2f}로 높아, 만족 집단과 강한 불만 집단이 함께 존재합니다."
        else:
            body = f"전체 평균은 {avg:.2f}점, 표준편차는 {std:.2f}로 현재 수집 구간의 평점 변동 폭을 함께 봐야 합니다."
        insights.append({"title": "평점은 평균만으로 보기 어렵습니다", "body": body})

    if "tone" in theme_summary.columns and not theme_summary.empty:
        negative = theme_summary[theme_summary["tone"] == "부정"].sort_values("count", ascending=False)
        positive = theme_summary[theme_summary["tone"] == "긍정"].sort_values("count", ascending=False)
        if not negative.empty:
            top = negative.iloc[0]
            insights.append(
                {
                    "title": "우선 점검할 불만 테마",
                    "body": f"부정 리뷰에서는 '{top['theme']}' 테마가 가장 많이 나타났습니다. 관련 리뷰 {int(top['count'])}건의 대표 문장을 먼저 확인하는 것이 좋습니다.",
                }
            )
        if not positive.empty:
            top = positive.iloc[0]
            insights.append(
                {
                    "title": "유지해야 할 강점 테마",
                    "body": f"긍정 리뷰에서는 '{top['theme']}' 테마가 가장 많이 언급됐습니다. 개선 과정에서 이 강점이 훼손되지 않도록 기준 기능으로 관리해야 합니다.",
                }
            )

    overall_periods = [row for row in period_trend if row["source"] == "overall"]
    if len(overall_periods) >= 2:
        first = overall_periods[0]
        last = overall_periods[-1]
        delta = round(float(last["avg_rating"]) - float(first["avg_rating"]), 2)
        direction = "상승" if delta > 0 else "하락" if delta < 0 else "유지"
        insights.append(
            {
                "title": "기간별 평점 흐름",
                "body": f"{first['period']} 평균 {first['avg_rating']:.2f}점에서 {last['period']} 평균 {last['avg_rating']:.2f}점으로 {abs(delta):.2f}점 {direction}했습니다.",
            }
        )

    global_min_date = None
    if not df.empty and "review_date" in df.columns:
        parsed_dates = pd.to_datetime(df["review_date"], errors="coerce").dropna()
        if not parsed_dates.empty:
            global_min_date = parsed_dates.min().date()
    for row in source_coverage:
        min_date = row.get("min_date")
        source = row.get("source")
        source_min_date = parse_datetime(min_date).date() if parse_datetime(min_date) else None
        if row.get("review_count") and source_min_date and global_min_date and source == "app_store" and source_min_date > global_min_date:
            insights.append(
                {
                    "title": "App Store 수집 범위 확인 필요",
                    "body": f"App Store 공개 RSS 기준 수집 시작일은 {min_date}입니다. 요청 기간 전체 판단에는 대체 수집원 또는 사내 보유 원자료 보강이 필요할 수 있습니다.",
                }
            )
            break

    if market_intelligence is not None and not market_intelligence.empty:
        gp = market_intelligence[market_intelligence["source"] == "google_play"].copy()
        if not gp.empty and "is_target" in gp.columns:
            target = gp[gp["is_target"] == True]
            peers = gp[gp["is_target"] != True]
            if not target.empty and not peers.empty:
                target_rating = _to_float(target.iloc[0].get("average_rating"))
                top_peer = peers.sort_values(["review_count", "average_rating"], ascending=[False, False]).iloc[0]
                peer_rating = _to_float(top_peer.get("average_rating"))
                if target_rating is not None and peer_rating is not None:
                    insights.append(
                        {
                            "title": "경쟁 앱 대비 위치",
                            "body": f"Google Play 기준 하나원큐 평점은 {target_rating:.2f}점이며, 피어셋 내 리뷰 규모 상위 앱 '{top_peer.get('title')}'은 {peer_rating:.2f}점입니다.",
                        }
                    )
    return insights[:6]


def build_action_recommendations(theme_summary: pd.DataFrame, limit: int = 5) -> list[dict[str, Any]]:
    if theme_summary.empty or "tone" not in theme_summary.columns:
        return []
    negative = theme_summary[theme_summary["tone"] == "부정"].copy()
    if negative.empty:
        return []
    action_map = {
        "로그인/인증": "인증 실패/반복 인증/생체인증 이탈 구간을 먼저 재현하고, 오류 메시지와 복구 동선을 점검합니다.",
        "인증/결제": "이체·카드·외화·결제 관련 인증 단계를 태스크별로 분리해 실패 지점과 중복 인증을 줄입니다.",
        "기능": "계좌 조회, 이체, 상품 가입처럼 빈도가 높은 핵심 업무의 누락/제한/전환 문제를 우선 확인합니다.",
        "안정성": "오류 코드, 흰 화면, 멈춤, 재설치 유도 케이스를 묶어 재현 조건과 서버/클라이언트 원인을 분리합니다.",
        "UI/UX": "홈 화면 정보 구조, 계좌 목록, 메뉴 탐색, 이전 앱 대비 달라진 조작 방식을 집중 점검합니다.",
        "속도/성능": "초기 실행, 메뉴 진입, 인증 후 전환 구간의 로딩 시간을 실측하고 저사양/해외망 조건을 포함합니다.",
        "고객응대": "리뷰 답변, 앱 내 오류 안내, 상담 연결까지 이어지는 불만 회수 동선을 개선합니다.",
        "접근성": "고령층·저시력·보조기술 사용자가 막히는 문구, 글자 크기, 인증 안내를 함께 점검합니다.",
        "기타": "대표 원문을 재코딩해 세부 원인을 분리하고, 반복 키워드가 새 테마로 승격될지 확인합니다.",
    }
    negative["avg_rating_num"] = pd.to_numeric(negative["avg_rating"], errors="coerce").fillna(3.0)
    negative["count_num"] = pd.to_numeric(negative["count"], errors="coerce").fillna(0)
    negative["severity_score"] = negative["count_num"] * (5 - negative["avg_rating_num"])
    negative = negative.sort_values(["severity_score", "count_num"], ascending=[False, False]).head(limit)
    rows: list[dict[str, Any]] = []
    for idx, (_, row) in enumerate(negative.iterrows(), start=1):
        theme = str(row.get("theme") or "기타")
        rows.append(
            {
                "priority": idx,
                "theme": theme,
                "negative_count": int(row["count_num"]),
                "avg_rating": round(float(row["avg_rating_num"]), 2),
                "severity_score": round(float(row["severity_score"]), 2),
                "recommended_action": action_map.get(theme, action_map["기타"]),
            }
        )
    return rows


def _split_themes_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_read_text(item) for item in value if _read_text(item)]
    text = _read_text(value)
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        text = text.strip("[]").replace("'", "").replace('"', "")
    return [part.strip() for part in text.split(",") if part.strip()]


def build_theme_review_index(df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    """Group every written review by sentiment/theme for expandable dashboard drill-downs."""
    if df.empty:
        return {}

    grouped: dict[str, list[dict[str, Any]]] = {}
    for _, row in df.iterrows():
        review_body = _read_text(row.get("review_body"))
        if not review_body:
            continue

        sentiment = _read_text(row.get("sentiment")) or "중립"
        themes = _split_themes_value(row.get("themes"))
        if not themes:
            themes = _split_themes_value(row.get("themes_list"))
        if not themes:
            themes = ["기타"]

        item = {
            "source": _read_text(row.get("source")),
            "date": _read_text(row.get("review_date")),
            "rating": _to_float(row.get("rating")),
            "review_body": review_body,
        }
        for theme in themes:
            grouped.setdefault(f"{sentiment}::{theme}", []).append(item)

    return grouped


def build_dashboard_payload(
    df: pd.DataFrame,
    theme_summary: pd.DataFrame,
    pros_cons: pd.DataFrame,
    store_ratings: dict[str, dict[str, Any]] | None = None,
    market_intelligence: pd.DataFrame | None = None,
) -> dict[str, Any]:
    store_ratings = store_ratings or {}
    gp_meta = store_ratings.get("google_play", {})
    as_meta = store_ratings.get("app_store", {})
    by_source = df.groupby("source").size().to_dict()
    source_coverage = build_source_coverage(df)
    rating_stats = build_rating_stats(df)
    rating_distribution_rows = build_rating_distribution_rows(df)
    period_trend = build_period_trend(df)
    rating_dist_raw = (
        df[df["rating"] > 0]
        .groupby(["source", "rating"])
        .size()
        .unstack(fill_value=0)
        .sort_index(axis=1)
        .to_dict(orient="index")
    )
    rating_dist = {
        source: {str(int(k)): int(v) for k, v in row.items()}
        for source, row in rating_dist_raw.items()
    }
    trend_data = [
        {
            "date": row["period"],
            "source": row["source"],
            "avg_rating": row["avg_rating"],
            "review_count": row["review_count"],
            "rating_std": row["rating_std"],
        }
        for row in build_period_trend(df, freq="W")
        if row["source"] != "overall"
    ]
    sentiment_dist = df["sentiment"].value_counts(dropna=True).to_dict()
    market_rows = []
    if market_intelligence is not None and not market_intelligence.empty:
        market_rows = json.loads(
            market_intelligence.sort_values(
                by=["source", "query", "search_rank", "market"], ascending=[True, True, True, True]
            )
            .to_json(orient="records", force_ascii=False)
        )

    return {
        "overview": {
            "app_name": df["app_name"].iloc[0] if not df.empty else "",
            "start_date": df["review_date"].min() if not df.empty else "",
            "end_date": df["review_date"].max() if not df.empty else "",
            "total_reviews": int(len(df)),
            "reviews_with_rating": int(pd.to_numeric(df["rating"], errors="coerce").gt(0).sum()) if not df.empty else 0,
            "reviews_with_opinion": int(df["has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df["review_body"].str.strip().ne("").sum()),
            "avg_rating": round(float(pd.to_numeric(df["rating"], errors="coerce").mean()), 2) if not df.empty else 0.0,
            "rating_std": next((row["rating_std"] for row in rating_stats if row["source"] == "overall"), None),
            "coverage": {
                "google_play_reviews": int(by_source.get("google_play", 0)),
                "app_store_reviews": int(by_source.get("app_store", 0)),
                "google_play_reviews_with_opinion": int(df.loc[df["source"] == "google_play", "has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df.loc[df["source"] == "google_play", "review_body"].str.strip().ne("").sum()),
                "app_store_reviews_with_opinion": int(df.loc[df["source"] == "app_store", "has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df.loc[df["source"] == "app_store", "review_body"].str.strip().ne("").sum()),
            },
            "store_ratings": {
                "google_play": {
                    "average_rating": gp_meta.get("average_rating"),
                    "review_count": gp_meta.get("review_count"),
                },
                "app_store": {
                    "average_rating": as_meta.get("average_rating"),
                    "review_count": as_meta.get("review_count"),
                },
            },
        },
        "rating_distribution": rating_dist,
        "rating_distribution_rows": rating_distribution_rows,
        "rating_stats": rating_stats,
        "period_trend": period_trend,
        "trend": trend_data,
        "theme_review_index": build_theme_review_index(df),
        "sentiment_distribution": sentiment_dist,
        "source_coverage": source_coverage,
        "insights": build_dashboard_insights(
            df,
            theme_summary,
            rating_stats,
            period_trend,
            source_coverage,
            market_intelligence=market_intelligence,
        ),
        "action_recommendations": build_action_recommendations(theme_summary),
        "theme_summary": json.loads(theme_summary.to_json(orient="records", force_ascii=False)) if not theme_summary.empty else [],
        "pros_cons": json.loads(pros_cons.to_json(orient="records", force_ascii=False)) if not pros_cons.empty else [],
        "market_intelligence": market_rows,
    }


def _dashboard_html(template_ctx: dict[str, Any], output_path: Path) -> None:
    overview = template_ctx["overview"]
    rating = template_ctx["rating_distribution"]
    trend = template_ctx["trend"]
    sentiment = template_ctx["sentiment_distribution"]
    theme_summary = template_ctx["theme_summary"]
    pros_cons = template_ctx["pros_cons"]
    market_intelligence = template_ctx.get("market_intelligence", [])
    source_coverage = template_ctx.get("source_coverage", [])
    rating_stats = template_ctx.get("rating_stats", [])
    rating_distribution_rows = template_ctx.get("rating_distribution_rows", [])
    period_trend = template_ctx.get("period_trend", [])
    theme_review_index = template_ctx.get("theme_review_index", {})
    insights = template_ctx.get("insights", [])
    action_recommendations = template_ctx.get("action_recommendations", [])
    store_rating = template_ctx["overview"].get("store_ratings", {})
    gp_store_rating = store_rating.get("google_play", {})
    as_store_rating = store_rating.get("app_store", {})
    gp_store_average = gp_store_rating.get("average_rating")
    gp_store_count = gp_store_rating.get("review_count")
    as_store_average = as_store_rating.get("average_rating")
    as_store_count = as_store_rating.get("review_count")

    def _safe(text: Any) -> str:
        return (
            "" if text is None else
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _fmt_decimal(value: Any, digits: int = 2) -> str:
        number = _to_float(value)
        if number is None or pd.isna(number):
            return "-"
        return f"{number:.{digits}f}"

    def _fmt_int(value: Any) -> str:
        number = _to_int(value)
        if number is None:
            return "-"
        return f"{number:,}"

    def _source_label(source: Any) -> str:
        return {
            "overall": "전체",
            "google_play": "Google Play",
            "app_store": "App Store",
        }.get(str(source), str(source))

    def _quote_list_html(value: Any) -> str:
        quotes = [q.strip() for q in str(value or "").split(" | ") if q.strip()]
        if not quotes:
            return ""
        return "<ol class='quote-list'>" + "".join(f"<li>{_safe(q)}</li>" for q in quotes) + "</ol>"

    def _theme_review_details_html(tone: Any, theme: Any) -> str:
        rows = theme_review_index.get(f"{_read_text(tone)}::{_read_text(theme)}", [])
        if not rows:
            return ""
        items = []
        for item in rows:
            meta_parts = [
                _source_label(item.get("source")),
                _read_text(item.get("date"))[:10],
                f"{_fmt_decimal(item.get('rating'))}점" if _to_float(item.get("rating")) is not None else "",
            ]
            meta = " / ".join(part for part in meta_parts if part)
            items.append(
                "<li>"
                f"<div class='review-meta'>{_safe(meta)}</div>"
                f"<div>{_safe(item.get('review_body', ''))}</div>"
                "</li>"
            )
        return (
            "<details class='theme-details'>"
            f"<summary>전체 의견 보기 ({len(rows)}건)</summary>"
            "<ol class='theme-review-list'>"
            + "".join(items)
            + "</ol></details>"
        )

    market_rows_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(_source_label(row.get('source', '')))}</td>"
            f"<td>{_safe(row.get('market', ''))}</td>"
            f"<td>{_safe(row.get('query', ''))}</td>"
            f"<td>{_safe(row.get('search_rank', ''))}</td>"
            f"<td><a href='{_safe(row.get('review_url', ''))}' target='_blank'>{_safe(row.get('title', ''))}</a></td>"
            f"<td>{_safe(row.get('developer', ''))}</td>"
            f"<td>{_fmt_decimal(row.get('average_rating'))}</td>"
            f"<td>{_fmt_int(row.get('review_count'))}</td>"
            f"<td>{_safe(row.get('installs', '') or '')}</td>"
            f"<td>{_safe('1위') if row.get('is_market_leader') else ''}</td>"
            f"<td>{_safe('O') if row.get('is_download_leader') else ''}</td>"
            f"<td>{_safe('대상 앱') if row.get('is_target') else ''}</td>"
            f"<td>{_safe(row.get('comment', ''))}</td>"
            "</tr>"
            for row in market_intelligence
        ]
    )
    source_coverage_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(_source_label(row.get('source', '')))}</td>"
            f"<td>{_safe(row.get('review_count', 0))}건</td>"
            f"<td>{_safe(row.get('min_date', ''))} ~ {_safe(row.get('max_date', ''))}</td>"
            f"<td>{_safe(row.get('coverage_note', ''))}</td>"
            "</tr>"
            for row in source_coverage
        ]
    )
    rating_stats_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(_source_label(row.get('source')))}</td>"
            f"<td>{_fmt_int(row.get('count'))}건</td>"
            f"<td>{_fmt_decimal(row.get('avg_rating'))}</td>"
            f"<td>{_fmt_decimal(row.get('rating_std'))}</td>"
            f"<td>{_safe(row.get('min_rating', ''))}~{_safe(row.get('max_rating', ''))}</td>"
            "</tr>"
            for row in rating_stats
        ]
    )
    rating_distribution_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(_source_label(row.get('source')))}</td>"
            f"<td>{_safe(row.get('rating', ''))}점</td>"
            f"<td>{_fmt_int(row.get('count'))}건</td>"
            f"<td><div class='bar'><span style='width:{max(0, min(100, _to_float(row.get('share_pct')) or 0)):.2f}%'></span></div>{_fmt_decimal(row.get('share_pct'))}%</td>"
            "</tr>"
            for row in rating_distribution_rows
        ]
    )
    period_trend_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(row.get('period', ''))}</td>"
            f"<td>{_safe(_source_label(row.get('source')))}</td>"
            f"<td>{_fmt_int(row.get('review_count'))}건</td>"
            f"<td>{_fmt_decimal(row.get('avg_rating'))}</td>"
            f"<td>{_fmt_decimal(row.get('rating_std'))}</td>"
            "</tr>"
            for row in period_trend
        ]
    )
    insights_html = ''.join(
        [
            "<li>"
            f"<strong>{_safe(row.get('title', ''))}</strong>"
            f"<p>{_safe(row.get('body', ''))}</p>"
            "</li>"
            for row in insights
        ]
    )
    action_recommendations_html = ''.join(
        [
            "<tr>"
            f"<td>{_safe(row.get('priority', ''))}</td>"
            f"<td>{_safe(row.get('theme', ''))}</td>"
            f"<td>{_fmt_int(row.get('negative_count'))}건</td>"
            f"<td>{_fmt_decimal(row.get('avg_rating'))}</td>"
            f"<td>{_fmt_decimal(row.get('severity_score'))}</td>"
            f"<td>{_safe(row.get('recommended_action', ''))}</td>"
            "</tr>"
            for row in action_recommendations
        ]
    )
    sentiment_total = sum(int(v or 0) for v in sentiment.values())
    sentiment_distribution_html = ''.join(
        [
            "<tr>"
            f"<td><span class='tone {tone}'>{_safe(tone)}</span></td>"
            f"<td>{_fmt_int(count)}건</td>"
            f"<td><div class='bar'><span style='width:{(count / sentiment_total * 100) if sentiment_total else 0:.2f}%'></span></div>{_fmt_decimal((count / sentiment_total * 100) if sentiment_total else 0)}%</td>"
            "</tr>"
            for tone, count in sentiment.items()
        ]
    )
    pros_cons_html = ''.join(
        [
            "<tr>"
            f"<td><span class='tone {str(row.get('type', '')).lower()}'>{_safe(row.get('type', ''))}</span></td>"
            f"<td>{_safe(row.get('theme', ''))}</td>"
            f"<td>{_fmt_int(row.get('count'))}</td>"
            f"<td>{_fmt_decimal(row.get('avg_rating'))}</td>"
            f"<td>{_quote_list_html(row.get('representative_quotes'))}{_theme_review_details_html(row.get('type', ''), row.get('theme', ''))}</td>"
            "</tr>"
            for row in pros_cons
        ]
    )
    theme_summary_html = ''.join(
        [
            "<tr>"
            f"<td><span class='tone {str(row.get('tone', '')).lower()}'>{_safe(row.get('tone', ''))}</span></td>"
            f"<td>{_safe(row.get('theme', ''))}</td>"
            f"<td>{_fmt_int(row.get('count'))}</td>"
            f"<td>{_fmt_decimal(row.get('share_pct'))}%</td>"
            f"<td>{_fmt_decimal(row.get('avg_rating'))}</td>"
            f"<td>{_quote_list_html(row.get('representative_quotes'))}{_theme_review_details_html(row.get('tone', ''), row.get('theme', ''))}</td>"
            "</tr>"
            for row in theme_summary
        ]
    )

    page = f"""
<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\"/>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
  <title>{overview['app_name']} 앱 리뷰 대시보드</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <style>
    :root {{
      --bg: #0f172a;
      --panel: #ffffff;
      --line: #e5e7eb;
      --text: #0f172a;
      --muted: #475569;
    }}
    body {{
      margin: 0;
      font-family: Inter, "Noto Sans KR", Arial, sans-serif;
      color: var(--text);
      background: linear-gradient(140deg, #ecfeff, #eef2ff 50%, #f8fafc);
    }}
    .wrap {{max-width: 1200px; margin: 24px auto; padding: 0 16px;}}
    .title {{font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;}}
    .meta {{color: var(--muted); margin-bottom: 16px;}}
    .grid {{display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;}}
    .card {{background: var(--panel); border:1px solid var(--line); border-radius: 12px; padding: 14px;}}
    .big {{font-size: 1.4rem; font-weight: 700;}}
    .section {{background: var(--panel); border:1px solid var(--line); border-radius: 12px; margin-bottom: 12px; padding: 14px;}}
    .section h2 {{font-size: 1.08rem; margin: 0 0 12px;}}
    table {{width: 100%; border-collapse: collapse; font-size: 0.93rem;}}
    th, td {{padding: 8px; border-bottom:1px solid var(--line); text-align: left; vertical-align: top;}}
    th {{background: #f8fafc; font-weight: 700;}}
    table.sortable th[data-sort] {{cursor: pointer; user-select: none; white-space: nowrap;}}
    table.sortable th[data-sort]::after {{content: ' ↕'; color: #94a3b8; font-size: 0.78rem;}}
    table.sortable th[data-sort-dir='asc']::after {{content: ' ↑'; color: #2563eb;}}
    table.sortable th[data-sort-dir='desc']::after {{content: ' ↓'; color: #2563eb;}}
    .list {{margin: 0; padding-left: 18px;}}
    .list li {{margin-bottom: 6px;}}
    .insight-list {{margin: 0; padding-left: 18px;}}
    .insight-list li {{margin-bottom: 10px;}}
    .insight-list p {{margin: 3px 0 0; color: var(--muted); line-height: 1.5;}}
    .quote-list {{margin: 0; padding-left: 18px;}}
    .quote-list li {{margin-bottom: 6px; line-height: 1.45;}}
    .theme-details {{margin-top: 8px;}}
    .theme-details summary {{cursor: pointer; color: #2563eb; font-size: 0.86rem; font-weight: 700;}}
    .theme-review-list {{margin: 8px 0 0; padding-left: 18px; max-height: 320px; overflow: auto;}}
    .theme-review-list li {{margin-bottom: 10px; line-height: 1.45;}}
    .review-meta {{color: var(--muted); font-size: 0.78rem; margin-bottom: 2px;}}
    .tone {{display: inline-block; min-width: 38px; padding: 2px 7px; border-radius: 999px; font-size: 0.82rem; font-weight: 700; text-align: center;}}
    .tone.긍정 {{background: #dcfce7; color: #166534;}}
    .tone.부정 {{background: #fee2e2; color: #991b1b;}}
    .tone.중립 {{background: #e2e8f0; color: #334155;}}
    .bar {{display: inline-block; width: 130px; height: 8px; margin-right: 8px; border-radius: 99px; background: #e5e7eb; overflow: hidden; vertical-align: middle;}}
    .bar span {{display: block; height: 100%; background: #2563eb;}}
    .compact-chart-grid {{display: grid; grid-template-columns: 220px 1fr; gap: 16px; align-items: center;}}
    .donut-box {{width: 220px; height: 190px;}}
    .donut-box canvas {{max-width: 220px; max-height: 190px;}}
    .chart-fallback {{padding: 14px; border: 1px dashed var(--line); color: var(--muted); background: #f8fafc;}}
    @media (max-width: 900px) {{
      .grid {{grid-template-columns: 1fr;}}
      .compact-chart-grid {{grid-template-columns: 1fr;}}
      .donut-box {{width: 100%; max-width: 220px; height: 180px;}}
      .bar {{width: 84px;}}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <h1 class=\"title\">{overview['app_name']} 앱 리뷰 분석 대시보드</h1>
    <div class=\"meta\">수집기간: {overview['start_date']} ~ {overview['end_date']} / 총 {overview['total_reviews']}건</div>
    <div class=\"grid\">
      <div class=\"card\"><div>전체 수집 리뷰 수</div><div class=\"big\">{overview['total_reviews']}건</div></div>
      <div class=\"card\"><div>전체 평균 평점</div><div class=\"big\">{_fmt_decimal(overview['avg_rating'])}</div></div>
      <div class=\"card\"><div>평점 표준편차</div><div class=\"big\">{_fmt_decimal(overview.get('rating_std'))}</div></div>
      <div class=\"card\"><div>Google Play 리뷰 수</div><div class=\"big\">{overview['coverage']['google_play_reviews']}건</div></div>
      <div class=\"card\"><div>App Store 리뷰 수</div><div class=\"big\">{overview['coverage']['app_store_reviews']}건</div></div>
    </div>

    <div class=\"section\">
      <h2>핵심 인사이트</h2>
      <ol class=\"insight-list\">
        {insights_html}
      </ol>
    </div>

    <div class=\"section\">
      <h2>개선 우선순위 제안</h2>
      <table>
        <thead>
          <tr><th>우선순위</th><th>테마</th><th>부정 리뷰 수</th><th>평균 평점</th><th>심각도 점수</th><th>권장 액션</th></tr>
        </thead>
        <tbody>
          {action_recommendations_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>수집 데이터 커버리지</h2>
      <table>
        <thead>
          <tr><th>스토어</th><th>수집 리뷰 수</th><th>수집 날짜 범위</th><th>메모</th></tr>
        </thead>
        <tbody>
          {source_coverage_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>스토어별 평점 통계</h2>
      <table>
        <thead>
          <tr><th>구분</th><th>리뷰 수</th><th>평균 평점</th><th>표준편차</th><th>최소~최대</th></tr>
        </thead>
        <tbody>
          {rating_stats_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>경쟁 앱/시장 Top 리스트</h2>
      <table class=\"sortable\" id=\"marketTable\">
        <thead>
          <tr><th data-sort=\"text\">스토어</th><th data-sort=\"text\">마켓</th><th data-sort=\"text\">피어셋/검색어</th><th data-sort=\"number\">순위</th><th data-sort=\"text\">앱</th><th data-sort=\"text\">개발사</th><th data-sort=\"number\">평점</th><th data-sort=\"number\">리뷰 수</th><th data-sort=\"number\">설치 추정</th><th data-sort=\"text\">최상위</th><th data-sort=\"text\">다운로드 상위</th><th data-sort=\"text\">대상 앱</th><th data-sort=\"text\">비고</th></tr>
        </thead>
        <tbody>
          {market_rows_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>감성 분포</h2>
      <div class=\"compact-chart-grid\">
        <div class=\"donut-box\"><canvas id=\"sentChart\"></canvas></div>
        <table>
          <thead>
            <tr><th>감성</th><th>건수</th><th>비율</th></tr>
          </thead>
          <tbody>
            {sentiment_distribution_html}
          </tbody>
        </table>
      </div>
    </div>

    <div class=\"section\">
      <h2>별점 분포</h2>
      <canvas id=\"ratingChart\" height=\"130\"></canvas>
      <table>
        <thead>
          <tr><th>구분</th><th>평점</th><th>건수</th><th>비율</th></tr>
        </thead>
        <tbody>
          {rating_distribution_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>주차별 평점 추세</h2>
      <canvas id=\"trendChart\" height=\"130\"></canvas>
    </div>

    <div class=\"section\">
      <h2>월별 리뷰 작성건 수</h2>
      <canvas id=\"monthlyCountChart\" height=\"110\"></canvas>
    </div>

    <div class=\"section\">
      <h2>좋은 점 / 나쁜 점 테마</h2>
      <table>
        <thead>
          <tr><th>구분</th><th>테마</th><th>건수</th><th>평균 평점</th><th>대표 리뷰</th></tr>
        </thead>
        <tbody>
          {pros_cons_html}
        </tbody>
      </table>
    </div>

    <div class=\"section\">
      <h2>의견별 테마 Top</h2>
      <table>
        <thead>
          <tr><th>톤</th><th>테마</th><th>건수</th><th>비율</th><th>평균 평점</th><th>대표 리뷰</th></tr>
        </thead>
        <tbody>
          {theme_summary_html}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const ratingData = {json.dumps(rating, ensure_ascii=False)};
    const trendRaw = {json.dumps(trend, ensure_ascii=False)};
    const periodTrendRaw = {json.dumps(period_trend, ensure_ascii=False)};
    const sentimentRaw = {json.dumps(sentiment, ensure_ascii=False)};
    const overallAverage = {json.dumps(overview.get("avg_rating"), ensure_ascii=False)};

    const parseSortValue = (text, type) => {{
      const raw = String(text || '').trim();
      if (type === 'number') {{
        const normalized = raw.replace(/,/g, '').replace(/[^\\d.-]/g, '');
        const value = Number(normalized);
        return Number.isFinite(value) ? value : Number.NEGATIVE_INFINITY;
      }}
      return raw.toLocaleLowerCase('ko-KR');
    }};

    document.querySelectorAll('table.sortable th[data-sort]').forEach((th, index) => {{
      th.addEventListener('click', () => {{
        const table = th.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const nextDir = th.dataset.sortDir === 'asc' ? 'desc' : 'asc';
        table.querySelectorAll('th[data-sort-dir]').forEach((node) => delete node.dataset.sortDir);
        th.dataset.sortDir = nextDir;
        rows.sort((a, b) => {{
          const aValue = parseSortValue(a.children[index]?.textContent, th.dataset.sort);
          const bValue = parseSortValue(b.children[index]?.textContent, th.dataset.sort);
          if (aValue < bValue) return nextDir === 'asc' ? -1 : 1;
          if (aValue > bValue) return nextDir === 'asc' ? 1 : -1;
          return 0;
        }});
        rows.forEach((row) => tbody.appendChild(row));
      }});
    }});

    if (typeof Chart === 'undefined') {{
      document.querySelectorAll('canvas').forEach((canvas) => {{
        const fallback = document.createElement('div');
        fallback.className = 'chart-fallback';
        fallback.textContent = '차트 라이브러리를 불러오지 못했습니다. 아래 표에서 동일 데이터를 확인할 수 있습니다.';
        canvas.replaceWith(fallback);
      }});
    }} else {{
      const sentimentLabels = Object.keys(sentimentRaw);
      const sentimentCounts = sentimentLabels.map((k) => sentimentRaw[k]);

      new Chart(document.getElementById('sentChart'), {{
        type: 'doughnut',
        data: {{
          labels: sentimentLabels,
          datasets: [{{
            data: sentimentCounts,
            backgroundColor: ['#16a34a', '#64748b', '#dc2626']
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{legend: {{position: 'bottom'}}}}
        }}
      }});

      const ratingLabels = ['1', '2', '3', '4', '5'];
      const buildCount = (source) => ratingLabels.map((r) => (ratingData[source] && ratingData[source][r]) ? Number(ratingData[source][r]) : 0);
      new Chart(document.getElementById('ratingChart'), {{
        type: 'bar',
        data: {{
          labels: ratingLabels,
          datasets: [
            {{label: 'Google Play', data: buildCount('google_play'), backgroundColor: '#0ea5e9'}},
            {{label: 'App Store', data: buildCount('app_store'), backgroundColor: '#2563eb'}}
          ]
        }},
        options: {{
          responsive: true,
          scales: {{
            x: {{stacked: true, ticks: {{autoSkip: true, maxRotation: 0}}}},
            y: {{beginAtZero: true}}
          }}
        }}
      }});

      const dateMap = {{}};
      const stdMap = {{}};
      const countMap = {{}};
      trendRaw.forEach((row) => {{
        if (!dateMap[row.date]) dateMap[row.date] = {{google_play: null, app_store: null}};
        if (!stdMap[row.date]) stdMap[row.date] = {{}};
        if (!countMap[row.date]) countMap[row.date] = {{}};
        if (row.source === 'google_play' || row.source === 'app_store') {{
          dateMap[row.date][row.source] = row.avg_rating == null ? null : Number(row.avg_rating);
          stdMap[row.date][row.source] = row.rating_std == null ? null : Number(row.rating_std);
          countMap[row.date][row.source] = row.review_count == null ? 0 : Number(row.review_count);
        }}
      }});
      const trendLabels = Object.keys(dateMap).sort();
      const gp = trendLabels.map((k) => dateMap[k].google_play ?? null);
      const as = trendLabels.map((k) => dateMap[k].app_store ?? null);
      const trendDatasets = [
        {{label: 'Google Play', sourceKey: 'google_play', data: gp, borderColor: '#0ea5e9', fill: false, tension: 0.25}},
        {{label: 'App Store', sourceKey: 'app_store', data: as, borderColor: '#16a34a', fill: false, tension: 0.25}}
      ];
      if (overallAverage !== null && Number.isFinite(Number(overallAverage))) {{
        trendDatasets.push({{
          label: '기간 전체 평균',
          sourceKey: 'overall',
          data: trendLabels.map(() => Number(overallAverage)),
          borderColor: '#111827',
          borderDash: [6, 4],
          pointRadius: 0,
          fill: false,
          tension: 0
        }});
      }}
      new Chart(document.getElementById('trendChart'), {{
        type: 'line',
        data: {{
          labels: trendLabels,
          datasets: trendDatasets
        }},
        options: {{
          responsive: true,
          plugins: {{
            tooltip: {{
              callbacks: {{
                label: (context) => {{
                  const value = context.parsed.y;
                  if (value === null || Number.isNaN(value)) return '';
                  if (context.dataset.sourceKey === 'overall') {{
                    return '기간 전체 평균: ' + Number(value).toFixed(2) + '점';
                  }}
                  const period = context.label;
                  const std = stdMap[period]?.[context.dataset.sourceKey];
                  const count = countMap[period]?.[context.dataset.sourceKey];
                  const stdText = Number.isFinite(Number(std)) ? Number(std).toFixed(2) : '-';
                  const countText = Number.isFinite(Number(count)) ? Number(count).toLocaleString('ko-KR') : '0';
                  return context.dataset.label + ': ' + Number(value).toFixed(2) + '점 / 표준편차 ' + stdText + ' / n=' + countText;
                }}
              }}
            }}
          }},
          scales: {{
            x: {{ticks: {{autoSkip: true, maxRotation: 0}}}},
            y: {{min: 1, max: 5}}
          }}
        }}
      }});

      const monthMap = {{}};
      periodTrendRaw.forEach((row) => {{
        if (row.source === 'overall') return;
        if (!monthMap[row.period]) monthMap[row.period] = {{google_play: 0, app_store: 0}};
        if (row.source === 'google_play' || row.source === 'app_store') {{
          monthMap[row.period][row.source] = Number(row.review_count || 0);
        }}
      }});
      const monthLabels = Object.keys(monthMap).sort();
      new Chart(document.getElementById('monthlyCountChart'), {{
        type: 'bar',
        data: {{
          labels: monthLabels,
          datasets: [
            {{label: 'Google Play', data: monthLabels.map((k) => monthMap[k].google_play), backgroundColor: '#0ea5e9'}},
            {{label: 'App Store', data: monthLabels.map((k) => monthMap[k].app_store), backgroundColor: '#16a34a'}}
          ]
        }},
        options: {{
          responsive: true,
          scales: {{
            x: {{stacked: true, ticks: {{autoSkip: true, maxRotation: 0}}}},
            y: {{stacked: true, beginAtZero: true}}
          }}
        }}
      }});
    }}
  </script>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")


def write_outputs(
    df: pd.DataFrame,
    theme_summary: pd.DataFrame,
    pros_cons: pd.DataFrame,
    config: PipelineConfig,
    store_ratings: dict[str, dict[str, Any]] | None = None,
    market_intelligence: pd.DataFrame | None = None,
    create_dashboard: bool = True,
) -> dict[str, str]:
    out = ensure_output_dir(config.output_dir, config.app_slug)
    app_slug = config.app_slug

    raw_csv = out / f"normalized_reviews_{app_slug}.csv"
    theme_csv = out / f"theme_summary_{app_slug}.csv"
    pros_csv = out / f"pros_cons_summary_{app_slug}.csv"
    ratings_csv = out / f"store_ratings_{app_slug}.csv"
    market_intel_csv = out / f"market_intelligence_{app_slug}.csv"
    dashboard_html = out / f"dashboard_{app_slug}.html"
    quality_json = out / f"quality_report_{app_slug}.json"
    excel_path = out / f"app_review_analysis_{app_slug}.xlsx"
    market_intel_df = market_intelligence if market_intelligence is not None else pd.DataFrame()
    market_intel_row_count = int(len(market_intel_df))
    source_coverage = build_source_coverage(df)
    source_coverage_quality = []
    for row in source_coverage:
        min_date = parse_datetime(row.get("min_date"))
        requested_start_reached = bool(min_date and min_date.date() <= config.from_date.date())
        note = str(row.get("coverage_note", "") or "")
        if row.get("review_count", 0) and not requested_start_reached:
            note = note or (
                "요청 시작일보다 늦은 리뷰까지만 수집됨. 공개 스토어 엔드포인트가 최신순 제한 페이지까지만 "
                "반환하는 경우가 있어, 전체 과거 커버리지는 대체 수집원 확인이 필요함."
            )
        source_coverage_quality.append(
            {
                **row,
                "requested_start_reached": requested_start_reached,
                "coverage_note": note,
            }
        )

    out_df = df.copy().drop(columns=["review_date_parsed"], errors="ignore")
    out_df.to_csv(raw_csv, index=False, encoding="utf-8-sig")
    theme_summary.to_csv(theme_csv, index=False, encoding="utf-8-sig")
    pros_cons.to_csv(pros_csv, index=False, encoding="utf-8-sig")
    rating_rows = []
    for source in ("google_play", "app_store"):
        meta = (store_ratings or {}).get(source, {})
        rating_rows.append(
            {
                "source": source,
                "average_rating": meta.get("average_rating"),
                "review_count": meta.get("review_count"),
                "market": meta.get("market", ""),
            }
        )
    pd.DataFrame(rating_rows).to_csv(ratings_csv, index=False, encoding="utf-8-sig")
    market_intel_df.to_csv(market_intel_csv, index=False, encoding="utf-8-sig")

    payload = build_dashboard_payload(
        df,
        theme_summary,
        pros_cons,
        store_ratings,
        market_intelligence=market_intel_df,
    )
    if create_dashboard:
        _dashboard_html(payload, dashboard_html)

    quality = {
        "app_name": config.app_name,
        "from_date": config.from_date.strftime(DATE_FMT),
        "to_date": config.to_date.strftime(DATE_FMT),
        "google_play_app_id": config.google_play_app_id,
        "app_store_app_id": config.app_store_app_id,
        "requested_markets": config.markets or ["kr"],
        "requested_appstore_markets": config.appstore_markets or ["kr"],
        "max_reviews_per_store": config.max_reviews_per_store,
        "raw_count": int(len(df)),
        "reviews_with_rating": int(pd.to_numeric(df["rating"], errors="coerce").gt(0).sum()) if not df.empty else 0,
        "reviews_with_opinion": int(df["has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df["review_body"].str.strip().ne("").sum()),
        "coverage": {
            "google_play": int((df["source"] == "google_play").sum()),
            "app_store": int((df["source"] == "app_store").sum()),
            "google_play_with_opinion": int(df.loc[df["source"] == "google_play", "has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df.loc[df["source"] == "google_play", "review_body"].str.strip().ne("").sum()),
            "app_store_with_opinion": int(df.loc[df["source"] == "app_store", "has_opinion_text"].sum()) if "has_opinion_text" in df.columns else int(df.loc[df["source"] == "app_store", "review_body"].str.strip().ne("").sum()),
        },
        "source_coverage": source_coverage_quality,
        "store_ratings": {
            "google_play": {
                "average_rating": (store_ratings or {}).get("google_play", {}).get("average_rating"),
                "review_count": (store_ratings or {}).get("google_play", {}).get("review_count"),
            },
            "app_store": {
                "average_rating": (store_ratings or {}).get("app_store", {}).get("average_rating"),
                "review_count": (store_ratings or {}).get("app_store", {}).get("review_count"),
            },
        },
        "market_intelligence": {
            "rows": market_intel_row_count,
            "targets": {
                "google_play_app_id": config.google_play_app_id,
                "app_store_app_id": config.app_store_app_id,
            },
            "peer_set": config.competitor_peer_set,
            "queries": config.competitor_queries if config.competitor_queries else [config.app_name],
        },
        "rating_stats": payload.get("rating_stats", []),
        "rating_distribution_rows": payload.get("rating_distribution_rows", []),
        "period_trend": payload.get("period_trend", []),
        "insights": payload.get("insights", []),
        "action_recommendations": payload.get("action_recommendations", []),
        "dashboard_created": bool(create_dashboard),
        "dedupe_removed": int(df["dedupe_removed"].iloc[0]) if "dedupe_removed" in df.columns and not df.empty else 0,
    }
    quality_json.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="정규화_리뷰")
        theme_summary.to_excel(writer, index=False, sheet_name="테마_요약")
        pros_cons.to_excel(writer, index=False, sheet_name="pros_cons")
        pd.DataFrame(rating_rows).to_excel(writer, index=False, sheet_name="스토어_평점")
        market_intel_df.to_excel(writer, index=False, sheet_name="경쟁앱_상위권")
        pd.DataFrame([quality]).to_excel(writer, index=False, sheet_name="메타")

    return {
        "output_dir": str(out),
        "raw_csv": str(raw_csv),
        "theme_csv": str(theme_csv),
        "pros_csv": str(pros_csv),
        "ratings_csv": str(ratings_csv),
        "market_intelligence_csv": str(market_intel_csv),
        "dashboard_html": str(dashboard_html) if create_dashboard else "",
        "quality_json": str(quality_json),
        "excel_path": str(excel_path),
    }


def write_dashboard_from_excel(excel_path: Path, output_dir: Path | None = None) -> dict[str, str]:
    out = output_dir or excel_path.parent
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(excel_path, sheet_name="정규화_리뷰")
    theme_summary = pd.read_excel(excel_path, sheet_name="테마_요약")
    pros_cons = pd.read_excel(excel_path, sheet_name="pros_cons")
    try:
        ratings_df = pd.read_excel(excel_path, sheet_name="스토어_평점")
    except Exception:
        ratings_df = pd.DataFrame()
    try:
        market_intel_df = pd.read_excel(excel_path, sheet_name="경쟁앱_상위권")
    except Exception:
        market_intel_df = pd.DataFrame()

    if "review_body" in df.columns:
        df["review_body"] = df["review_body"].fillna("").astype(str).str.strip()
    if "has_opinion_text" not in df.columns and "review_body" in df.columns:
        df["has_opinion_text"] = df["review_body"].str.len().gt(0).astype(int)

    store_ratings: dict[str, dict[str, Any]] = {}
    if not ratings_df.empty and "source" in ratings_df.columns:
        for _, row in ratings_df.iterrows():
            source = str(row.get("source") or "").strip()
            if not source:
                continue
            store_ratings[source] = {
                "average_rating": row.get("average_rating"),
                "review_count": row.get("review_count"),
                "market": row.get("market", ""),
            }

    app_name = _read_text(df["app_name"].iloc[0]) if not df.empty and "app_name" in df.columns else safe_slug(excel_path.stem)
    dashboard_html = out / f"dashboard_{safe_slug(app_name)}.html"
    payload = build_dashboard_payload(
        df,
        theme_summary,
        pros_cons,
        store_ratings,
        market_intelligence=market_intel_df,
    )
    _dashboard_html(payload, dashboard_html)
    return {
        "output_dir": str(out),
        "dashboard_html": str(dashboard_html),
        "excel_path": str(excel_path),
    }


def prompt_for_period() -> tuple[datetime, datetime]:
    today = datetime.now().date()
    defaults = (today - timedelta(days=30), today)
    print("수집할 기간을 입력해주세요. 형식: YYYY-MM-DD YYYY-MM-DD")
    print(f"예시: {defaults[0]} {defaults[1]}")
    raw = input("입력(엔터 시 기본값 사용): ").strip()
    if raw:
        parts = raw.replace("~", " ").replace("/", "-").split()
        if len(parts) >= 2:
            s = parse_date(parts[0])
            e = parse_date(parts[1])
            if s and e:
                return s, e
    return datetime.combine(defaults[0], datetime.min.time()), datetime.combine(defaults[1], datetime.max.time())


def choose_candidate(candidates: list[dict[str, Any]], title: str) -> str | None:
    if not candidates:
        return None
    if len(candidates) == 1:
        return str(candidates[0]["app_id"])

    print(f"\n[{title}] 후보 앱 목록")
    for i, c in enumerate(candidates[:8], start=1):
        print(f"  {i}. {c.get('title')} / id={c.get('app_id')} / developer={c.get('developer')} / market={c.get('market')}")
    if not __import__('sys').stdin.isatty():
        return str(candidates[0]["app_id"])
    while True:
        try:
            raw = input("사용할 번호를 입력하세요(예: 1): ").strip()
        except EOFError:
            return str(candidates[0]["app_id"])
        if raw.isdigit() and 1 <= int(raw) <= min(len(candidates), 8):
            return str(candidates[int(raw) - 1]["app_id"])
        print("범위 내 숫자로 입력해 주세요.")
