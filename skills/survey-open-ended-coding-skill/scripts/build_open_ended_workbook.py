"""survey-open-ended-coding-skill canonical script.

Extracts free-text "기타 답변" (other, write-in) responses from a
`cleaned_dataset.csv` (as produced by survey-data-preprocessing's
`build_cleaned_dataset.py`) plus its matching `column_ledger.csv`, applies a
hardcoded starter codebook via keyword matching, and writes both the raw
extracted records and a coding workbook.

The codebook below is UXQ/26.GP.UXQ-specific (its keywords were tuned against
that project's actual free-text responses) — treat it as a starting point to
edit per project, not a universal classifier. See `04_validation_notes.md` in
the matching validation_runs folder for what this reproduces and what's still
project-specific about it.

Originally hardcoded to a fixed relative path into a since-superseded ad-hoc
validation folder; refactored to take `cleaned_dataset.csv` +
`column_ledger.csv` as CLI arguments so it composes with
survey-data-preprocessing's canonical output instead of a one-off snapshot.

Usage:
    python build_open_ended_workbook.py <cleaned_dataset.csv> <column_ledger.csv> <out_dir> [--project-id ID]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


CODEBOOK = [
    {
        "code": "no_specific_issue",
        "definition": "응답자가 뚜렷한 불편이나 부족 요소가 없다고 말함",
        "include_when": "없음, 불편한 점 없음, 문제 없음, 특별히 부족하지 않음",
        "exclude_when": "명확한 개선 요청이나 불만을 함께 말하는 경우",
        "parent_theme": "null_or_positive",
    },
    {
        "code": "positive_satisfaction",
        "definition": "긍정 평가나 만족 이유를 직접 언급함",
        "include_when": "편리하다, 마음에 든다, 원활하다, 한눈에 들어온다",
        "exclude_when": "단순히 '없음'만 말하는 경우",
        "parent_theme": "null_or_positive",
    },
    {
        "code": "ui_visual_design",
        "definition": "아이콘, 색상, 글씨, 화면 구성 등 시각적 UI 요소를 지적함",
        "include_when": "아이콘, 컬러, 회색, 화면, 글씨, 메인화면",
        "exclude_when": "기능 부족이나 탐색 문제만 말하는 경우",
        "parent_theme": "product_experience",
    },
    {
        "code": "navigation_discoverability",
        "definition": "기능이나 메뉴를 찾기 어려운 탐색 문제를 지적함",
        "include_when": "찾기 어렵다, 메뉴를 눌러봤다, 한눈에 안 들어온다",
        "exclude_when": "속도나 오류 문제만 말하는 경우",
        "parent_theme": "product_experience",
    },
    {
        "code": "speed_stability",
        "definition": "속도 저하, 오류, 재실행 등 안정성 문제를 말함",
        "include_when": "느리다, 속도, 오류, 재실행",
        "exclude_when": "상담/인증 절차 문제만 말하는 경우",
        "parent_theme": "product_experience",
    },
    {
        "code": "customer_support_resolution",
        "definition": "고객센터, 상담원 연결, 문제 해결 경로를 지적함",
        "include_when": "상담원, 고객센터, 전화 연결, 해결 방법",
        "exclude_when": "단순 탐색 문제만 말하는 경우",
        "parent_theme": "support_resolution",
    },
    {
        "code": "authentication_transfer_flow",
        "definition": "인증서, 비밀번호, 이체, 한도 등 핵심 금융 흐름의 마찰을 지적함",
        "include_when": "인증서, 비밀번호, 이체, 한도 증가",
        "exclude_when": "일반 UI 감상만 말하는 경우",
        "parent_theme": "product_experience",
    },
    {
        "code": "feature_request_or_gap",
        "definition": "원하는 기능이나 구조 개선, 추가 보완 요구를 말함",
        "include_when": "메뉴 모음, 메인화면 변경, 기능 요청, 부족",
        "exclude_when": "다른 앱 이름만 말하는 경우",
        "parent_theme": "product_experience",
    },
    {
        "code": "feature_reference",
        "definition": "특정 기능·서비스명을 단순 지칭하며 사용 맥락을 남김",
        "include_when": "앱테크, 놀이터 기능 등 기능 이름을 직접 언급",
        "exclude_when": "명확한 긍정/부정 평가가 함께 있는 경우 그 코드를 우선 사용",
        "parent_theme": "product_experience",
    },
    {
        "code": "benefits_rewards_value",
        "definition": "이벤트, 혜택, 포인트, 리워드 가치에 대한 반응을 말함",
        "include_when": "이벤트, 하나머니, 머니 적립, 보상",
        "exclude_when": "일반 만족만 말하는 경우",
        "parent_theme": "value_content",
    },
    {
        "code": "competitor_reference",
        "definition": "타 금융앱이나 서비스 이름을 답으로 제시함",
        "include_when": "케이뱅크, 부산은행, 기업은행, IBK, 모니모, 제주은행, 토스 등",
        "exclude_when": "기존 하나원큐 내부 비교만 말하는 경우",
        "parent_theme": "market_frame",
    },
    {
        "code": "comparative_neutrality",
        "definition": "앱 간 차이가 크지 않거나 특별히 부족하지 않다고 봄",
        "include_when": "다 비슷하다, 크게 다른지 모르겠다, 부족한 부분이 느껴지지 않는다",
        "exclude_when": "명확한 칭찬이나 불만이 있는 경우",
        "parent_theme": "market_frame",
    },
    {
        "code": "habit_or_lock_in",
        "definition": "경험 품질 외 이유로 계속 쓰는 관성·락인을 말함",
        "include_when": "사업자통장, 오래 사용, 옮기기 어렵다",
        "exclude_when": "단순 선호나 만족을 말하는 경우",
        "parent_theme": "relationship_context",
    },
    {
        "code": "review_needed",
        "definition": "짧거나 모호해서 추가 해석이 필요한 응답",
        "include_when": "문맥 없이 한 단어만 남았거나 의미가 불분명함",
        "exclude_when": "기존 코드로 충분히 설명 가능한 경우",
        "parent_theme": "review",
    },
]


COMPETITOR_TOKENS = [
    "케이뱅크",
    "부산은행",
    "기업은행",
    "ibk",
    "i-one bank",
    "뱅크샐러드",
    "모니모",
    "제주은행",
    "토스",
]


def normalize_text(text: str) -> str:
    return " ".join(str(text).replace("\r", " ").replace("\n", " ").split()).strip()


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered


def assign_codes(text: str, question_code: str) -> tuple[list[str], str]:
    raw = normalize_text(text)
    lower = raw.lower()
    codes: list[str] = []
    notes: list[str] = []

    if any(token in raw for token in ["딱히 없음", "없음", "없어요", "특별히 불편함 없음", "불편한적 없음", "문제 발생한적 없음", "부족한 부분이 느껴지지 않았음"]):
        codes.append("no_specific_issue")

    if any(token in raw for token in ["마음에 들어", "편리", "편했다", "원활", "한눈에 잘 들어오", "좋았음", "즐거움"]):
        codes.append("positive_satisfaction")

    if any(token in lower for token in ["아이콘", "컬러", "색깔", "회색", "메인화면", "화면", "글씨", "ui", "ux"]):
        codes.append("ui_visual_design")

    if any(token in raw for token in ["찾기어려", "찾는데", "메뉴", "눌러", "한눈에", "찾음"]):
        codes.append("navigation_discoverability")

    if any(token in raw for token in ["속도", "느리", "오류", "재실행", "껐다 켬", "끊기", "튕겨"]):
        codes.append("speed_stability")

    if any(token in raw for token in ["상담원", "고객센터", "전화"]):
        codes.append("customer_support_resolution")

    if any(token in raw for token in ["인증서", "비밀번호", "이체", "한도"]):
        codes.append("authentication_transfer_flow")

    if any(token in raw for token in ["메뉴 모음", "메인화면", "알림음", "한도 증가", "자주 쓰는", "부족", "개선이 필요", "간결함"]):
        codes.append("feature_request_or_gap")

    if any(token in raw for token in ["앱테크", "놀이터 기능"]):
        codes.append("feature_reference")

    if any(token in raw for token in ["이벤트", "하나머니", "머니", "보상"]):
        codes.append("benefits_rewards_value")

    if any(token in lower for token in COMPETITOR_TOKENS):
        codes.append("competitor_reference")

    if any(token in raw for token in ["다 비슷", "비슷비슷", "크게다른걸모르겠다", "비슷한 구성", "부족한 부분이 느껴지지 않았음", "다른 것 없이"]):
        codes.append("comparative_neutrality")

    if any(token in raw for token in ["사업자통장", "10년", "이동이 편하지 않아", "오래 사용"]):
        codes.append("habit_or_lock_in")

    if question_code in {"P4B1", "P4B2", "P4B3"} and not codes:
        codes.append("competitor_reference")

    if question_code == "P3B4" and raw == "속도":
        codes.extend(["speed_stability", "feature_request_or_gap"])

    if question_code == "P19B2" and raw in {"메뉴 하너씩 다눌러봄", "아무거나 누르다가 찾음"}:
        codes.append("navigation_discoverability")

    if raw in {"딱히 없음", "없음", "불편한적 없음"}:
        notes.append("의미가 짧아 맥락 확인 필요")

    codes = dedupe_keep_order(codes)

    if not codes:
        codes = ["review_needed"]
        notes.append("자동 규칙으로 명확한 코드 배정 실패")

    if len(codes) > 3:
        notes.append(f"초기 후보 {len(codes)}개 중 상위 3개만 유지")
        codes = codes[:3]

    if len(raw) <= 4:
        if "review_needed" not in codes:
            codes.append("review_needed")
            codes = codes[:3]
        notes.append("응답 길이가 매우 짧음")

    return codes, " | ".join(dedupe_keep_order(notes))


def selection_reason(text: str) -> str:
    normalized = normalize_text(text)
    if len(normalized) >= 35:
        return "구체성이 높아 대표 인용문으로 적합"
    if len(normalized) <= 8:
        return "짧지만 응답 의도가 선명해 보조 예시로 유지"
    return "핵심 의미가 선명해 대표 예시로 유지"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cleaned_dataset_csv")
    parser.add_argument("column_ledger_csv")
    parser.add_argument("out_dir")
    parser.add_argument("--project-id", default="unknown")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cleaned_df = pd.read_csv(args.cleaned_dataset_csv, encoding="utf-8-sig")
    column_ledger = pd.read_csv(args.column_ledger_csv, encoding="utf-8-sig").fillna("")

    # question_code -> question_text, derived directly from column_ledger
    # (no separate question_family_summary.csv needed).
    question_map: dict[str, str] = {}
    for _, row in column_ledger.iterrows():
        code = str(row["question_code"])
        if code not in question_map:
            question_map[code] = str(row["question_text"])

    open_cols = [c for c in cleaned_df.columns if c.endswith("__기타 답변")]
    records = []
    for row_idx, row in cleaned_df.iterrows():
        respondent_id = row.get("응답자ID", "")
        segment = f"성별={row.get('성별', '')} | 연령대={row.get('연령대', '')}"
        for col in open_cols:
            value = row.get(col)
            if pd.isna(value):
                continue
            response_text = normalize_text(value)
            if not response_text:
                continue
            question_code = col.split("__", 1)[0]
            question_text = question_map.get(question_code, question_code)
            codes, coder_note = assign_codes(response_text, question_code)
            records.append(
                {
                    "row_id": f"{question_code}_{row_idx + 1}",
                    "question": question_text,
                    "question_code": question_code,
                    "respondent_id": respondent_id,
                    "segment": segment,
                    "response_text": response_text,
                    "codes": ", ".join(codes),
                    "coder_note": coder_note,
                }
            )

    responses_df = pd.DataFrame(records)
    responses_df = responses_df.sort_values(["question_code", "row_id"]).reset_index(drop=True)
    responses_df.insert(0, "#", range(1, len(responses_df) + 1))

    extracted_path = out_dir / "00_extracted_open_ended_responses.csv"
    responses_df.to_csv(extracted_path, index=False, encoding="utf-8-sig")

    code_counter: Counter[str] = Counter()
    question_code_counter: Counter[tuple[str, str]] = Counter()
    question_totals: Counter[str] = Counter()
    segment_gender_counter: Counter[tuple[str, str, str]] = Counter()

    for _, row in responses_df.iterrows():
        question_code = row["question_code"]
        question_totals[question_code] += 1
        gender = "미상"
        if "성별=여성" in row["segment"]:
            gender = "여성"
        elif "성별=남성" in row["segment"]:
            gender = "남성"
        codes = [code.strip() for code in str(row["codes"]).split(",") if code.strip()]
        for code in codes:
            code_counter[code] += 1
            question_code_counter[(question_code, code)] += 1
            segment_gender_counter[(question_code, code, gender)] += 1

    codebook_rows = []
    for item in CODEBOOK:
        codebook_rows.append(
            {
                "code": item["code"],
                "definition": item["definition"],
                "include_when": item["include_when"],
                "exclude_when": item["exclude_when"],
                "parent_theme": item["parent_theme"],
                "count": code_counter.get(item["code"], 0),
            }
        )
    codebook_df = pd.DataFrame(codebook_rows)

    summary_rows = []
    for question_code, total in sorted(question_totals.items()):
        related = [(code, count) for (q, code), count in question_code_counter.items() if q == question_code]
        related.sort(key=lambda item: (-item[1], item[0]))
        for rank, (code, count) in enumerate(related, start=1):
            summary_rows.append(
                {
                    "question": question_map.get(question_code, question_code),
                    "question_code": question_code,
                    "code": code,
                    "count": count,
                    "percent": round(count / total * 100, 1),
                    "rank": rank,
                    "female_count": segment_gender_counter.get((question_code, code, "여성"), 0),
                    "male_count": segment_gender_counter.get((question_code, code, "남성"), 0),
                    "insight_note": (
                        "기타 답변에서 이 코드가 상대적으로 자주 반복됨"
                        if rank <= 2
                        else "희소하지만 구체적 맥락 보존 필요"
                    ),
                }
            )
    summary_df = pd.DataFrame(summary_rows)

    quote_rows = []
    for (question_code, code), subset in responses_df.assign(
        code_list=responses_df["codes"].str.split(", ")
    ).explode("code_list").groupby(["question_code", "code_list"]):
        if not isinstance(question_code, tuple):
            q_code, code_value = question_code, code
        else:
            q_code, code_value = question_code
        sorted_subset = subset.sort_values(
            by="response_text",
            key=lambda col: col.astype(str).str.len(),
            ascending=False,
        ).head(2)
        for _, row in sorted_subset.iterrows():
            quote_rows.append(
                {
                    "question": question_map.get(q_code, q_code),
                    "question_code": q_code,
                    "code": code_value,
                    "quote": row["response_text"],
                    "respondent_id": row["respondent_id"],
                    "selection_reason": selection_reason(row["response_text"]),
                }
            )
    quotes_df = pd.DataFrame(quote_rows)

    outlier_rows = []
    for _, row in responses_df.iterrows():
        codes = [code.strip() for code in str(row["codes"]).split(",") if code.strip()]
        issue_type = ""
        review_notes = []
        if "review_needed" in codes:
            issue_type = "review_needed"
            review_notes.append("자동 규칙만으로 해석이 애매하거나 응답이 짧음")
        if "competitor_reference" in codes and len(normalize_text(row["response_text"])) <= 6:
            issue_type = issue_type or "competitor_name_only"
            review_notes.append("단일 앱 이름 응답으로 질문 맥락 보완 필요")
        if "no_specific_issue" in codes and len(codes) == 1:
            issue_type = issue_type or "null_or_minimal"
            review_notes.append("불편·개선 요구보다 '없음' 성격의 응답")
        if row["coder_note"]:
            review_notes.append(str(row["coder_note"]))
        if issue_type:
            outlier_rows.append(
                {
                    "row_id": row["row_id"],
                    "question": row["question"],
                    "question_code": row["question_code"],
                    "response_text": row["response_text"],
                    "issue_type": issue_type,
                    "review_note": " | ".join(dict.fromkeys(review_notes)),
                }
            )
    outliers_df = pd.DataFrame(outlier_rows)

    overview_rows = [
        {
            "field": "project_id",
            "value": args.project_id,
            "note": "26.GP.UXQ 설문2 validation pack",
        },
        {
            "field": "validation_date",
            "value": "2026-08-18",
            "note": "Tuesday, August 18, 2026",
        },
        {
            "field": "source_scope",
            "value": "기타 답변 columns from uxq_survey2 cleaned_dataset.csv",
            "note": "전용 장문 주관식이 아니라 기타 응답 기반 검증",
        },
        {
            "field": "response_records",
            "value": str(len(responses_df)),
            "note": "question별로 분리된 자유서술 response unit",
        },
        {
            "field": "question_count",
            "value": str(responses_df['question_code'].nunique()),
            "note": "기타 답변이 실제로 존재한 question code 수",
        },
        {
            "field": "codebook_status",
            "value": "draft",
            "note": "AI-generated starter codebook; team approval not yet applied",
        },
        {
            "field": "segment_fields",
            "value": "성별, 연령대",
            "note": "core sheet에는 combined segment 문자열로 보존",
        },
        {
            "field": "main_limit",
            "value": "sparse other-text",
            "note": "질문당 응답 수가 낮고 맥락이 짧아 review_needed를 함께 유지",
        },
    ]
    overview_df = pd.DataFrame(overview_rows)

    workbook_path = out_dir / "open_ended_coding_workbook.xlsx"
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        overview_df.to_excel(writer, sheet_name="coding_overview", index=False)
        responses_df[
            ["row_id", "question", "respondent_id", "segment", "response_text", "codes", "coder_note"]
        ].to_excel(writer, sheet_name="responses_coded", index=False)
        codebook_df.to_excel(writer, sheet_name="codebook", index=False)
        summary_df.to_excel(writer, sheet_name="question_code_summary", index=False)
        quotes_df.to_excel(writer, sheet_name="representative_quotes", index=False)
        outliers_df.to_excel(writer, sheet_name="outliers_review", index=False)

    # NOTE: this script intentionally does NOT auto-write its own
    # 04_validation_notes.md. It used to, with a hardcoded "2026-08-18" date
    # baked into the template text — which went stale the moment the script
    # was reused on a later date, and would silently clobber any
    # hand-authored notes on every re-run. Write validation_notes.md as a
    # separate, session-authored file instead (matching the convention used
    # by survey-data-preprocessing / survey-basic-stats-analysis /
    # survey-analysis-verification's canonical scripts).
    print(
        f"extracted {len(responses_df)} responses across "
        f"{responses_df['question_code'].nunique()} question codes "
        f"({len(CODEBOOK)} codes in the starter codebook) -> {out_dir}"
    )


if __name__ == "__main__":
    main()
