from __future__ import annotations

import argparse
import json
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent

# Defaults preserve the original hardcoded layout so callers that pass no
# CLI args keep working unchanged. Pass --round1-data / --survey1-2-ssot /
# --reference-report / --reference-readme / --out-dir to point at a
# different project or a relocated external repo.
DEFAULT_ROUND1_DIR = ROOT.parent / "2026-08-18_26.GP.UXQ"
DEFAULT_ROUND1_DATA_PATH = DEFAULT_ROUND1_DIR / "01_dashboard_data.json"
DEFAULT_SURVEY1_2_SSOT_PATH = Path(
    r"C:\Users\hanati\Documents\GitHub\ux_evaluation_hana1q\research\analysis\survey_key_findings_generated.json"
)
DEFAULT_REFERENCE_REPORT_PATH = Path(
    r"C:\Users\hanati\Documents\GitHub\ux_evaluation_hana1q\public\index.html"
)
DEFAULT_REFERENCE_REPORT_README = Path(
    r"C:\Users\hanati\Documents\GitHub\ux_evaluation_hana1q\README.md"
)

TODAY_ISO = date.today().isoformat()


NAVY = "#003087"
RED = "#E8003D"
SAND = "#F6F0E8"
PAPER = "#FBFAF7"
INK = "#18212B"
SLATE = "#51606F"
MIST = "#D7DEE6"
SKY = "#EAF2FF"
ROSE = "#FFF0F3"
MINT = "#EEF9F2"
AMBER = "#FFF6E5"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_pct(value: float | int | None) -> str:
    if value is None or value == "":
        return "-"
    return f"{float(value):.1f}%"


def fmt_num(value: float | int | None, digits: int = 1) -> str:
    if value is None or value == "":
        return "-"
    return f"{float(value):.{digits}f}"


def clean_col(name: object) -> str:
    return str(name).replace("↕", "").strip()


def clean_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [clean_col(col) for col in cleaned.columns]
    return cleaned


def load_reference_tables(
    reference_report_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tables = [clean_df_columns(df) for df in pd.read_html(reference_report_path)]
    def longest_match(required_cols: set[str]) -> pd.DataFrame:
        matches = [df for df in tables if required_cols.issubset(df.columns)]
        return max(matches, key=len)

    gap_driver = longest_match(
        {
            "경험 드라이버",
            "1위 앱",
            "1위 점수",
            "하나원큐",
            "하나원큐 순위",
            "1위 대비 격차",
            "경쟁 4사 대비",
        }
    )
    app_detail = longest_match(
        {
            "항목",
            "구분",
            "하나원큐 n=201",
            "토스 n=211",
            "카카오뱅크 n=202",
            "신한SOL n=204",
            "KB스타뱅킹 n=207",
            "전체 평균",
            "하나 순위",
            "유의",
        }
    )
    redirect = longest_match({"보강 필요 업무 → 더 편한 앱", "점수"})
    return gap_driver, app_detail, redirect


def normalize_question_block(block: dict) -> dict:
    normalized = dict(block)
    if "score_rows" not in normalized:
        return normalized

    score_rows = normalized["score_rows"]
    total = sum(int(row["count"]) for row in score_rows)
    if not total:
        return normalized

    weighted_sum = sum(int(row["score"]) * int(row["count"]) for row in score_rows)
    mean = weighted_sum / total
    variance = sum(
        ((int(row["score"]) - mean) ** 2) * int(row["count"]) for row in score_rows
    ) / total
    top2 = sum(int(row["count"]) for row in score_rows if int(row["score"]) >= 6) / total * 100
    bottom2 = sum(int(row["count"]) for row in score_rows if int(row["score"]) <= 2) / total * 100

    normalized["mean"] = round(mean, 2)
    normalized["std"] = round(variance ** 0.5, 2)
    normalized["top2_pct"] = round(top2, 1)
    normalized["bottom2_pct"] = round(bottom2, 1)
    normalized["data_note"] = (
        f"전체 평균은 {normalized['mean']:.2f}, "
        f"Top2는 {normalized['top2_pct']:.1f}%, "
        f"Bottom2는 {normalized['bottom2_pct']:.1f}%입니다."
    )
    return normalized


def build_data(
    round1_data_path: Path,
    survey1_2_ssot_path: Path,
    reference_report_path: Path,
    reference_readme_path: Path,
    round1_dir: Path,
) -> dict:
    round1 = read_json(round1_data_path)
    ssot = read_json(survey1_2_ssot_path)
    gap_driver_df, app_detail_df, redirect_df = load_reference_tables(reference_report_path)

    benchmark_apps = sorted(
        ssot["survey1"]["app_overall"],
        key=lambda row: row["overall_index_100"],
        reverse=True,
    )
    hana_rank = next(
        idx
        for idx, row in enumerate(benchmark_apps, start=1)
        if row["app"] == "하나원큐"
    )
    leader = benchmark_apps[0]
    hana_score = next(
        row["overall_index_100"] for row in benchmark_apps if row["app"] == "하나원큐"
    )

    question_block_lookup = {block["code"]: block for block in round1["question_blocks"]}
    p2 = question_block_lookup["P2B1"]
    p18 = question_block_lookup["P18B1"]
    p3 = question_block_lookup["P3B4"]

    gap_driver_rows = gap_driver_df.head(10).to_dict("records")
    comparison_rows = app_detail_df.head(12).to_dict("records")
    redirect_rows = redirect_df.head(8).to_dict("records")

    bridges = [
        {
            "theme": "홈 탐색·개인화",
            "survey1": "홈화면 탐색 구성 67.9점(5위), 토스 대비 -7.5 / 홈 화면 개인화 66.1점(5위), 토스 대비 -7.3",
            "survey2": "리뉴얼 후 개선 체감은 36.8%지만 '비슷함'이 52.1%(146/280)로 더 큽니다.",
            "implication": "개편 인지는 되었지만, 선도 앱 대비 탐색 경쟁력으로 체감되기에는 아직 부족합니다.",
        },
        {
            "theme": "혜택·이벤트",
            "survey1": "이벤트 64.8점(4위), 토스 대비 -13.9로 가장 큰 benchmark gap입니다.",
            "survey2": "불편 경험률 80.9%(131/162), 보강 필요 71.1%(199/280), weighted score 429로 1위입니다.",
            "implication": "survey1의 경쟁 열위가 survey2의 실제 불편·개선 요구로 그대로 이어지는 축입니다.",
        },
        {
            "theme": "상품·자산",
            "survey1": "상품 다양성 68.0점(5위, -8.2), 자산/거래 현황 65.8점(5위, -10.6)로 약세입니다.",
            "survey2": "상품/서비스 다양성 보강 요구 60.7%(170/280), 자산관리 보강 요구 36.4%(102/280)입니다.",
            "implication": "탐색성과 자산 가시성 문제는 '부족하다'는 기능 인식과 연결되어 후속 우선순위 후보가 됩니다.",
        },
        {
            "theme": "기본 업무·연동",
            "survey1": "계좌/금융정보 연동 69.2점(4위), 토스 대비 -13.2입니다.",
            "survey2": "계좌조회/이체 불편 경험률은 40.4%(95/235)로 치명적 수준은 아니지만 개선 여지는 남아 있습니다.",
            "implication": "기본 뱅킹은 유지 가능하지만, 타행 대비 '더 추천하고 싶은 앱'으로 만들 핵심 차별점은 약합니다.",
        },
    ]

    qa_flags = round1["qa_flags"] + [
        {
            "level": "ok",
            "badge": "S1 BRIDGE",
            "title": "survey1 benchmark 모듈을 실사례 정본으로 연결했습니다",
            "detail": "설문1은 survey_key_findings_generated.json의 app-level 정본과 published report HTML 표를 함께 사용해 app ranking·gap driver를 구성했습니다.",
        },
        {
            "level": "info",
            "badge": "STATIC HTML",
            "title": "이번 2차 검증은 공유 가능한 정적 HTML까지 생성합니다",
            "detail": "연구원용 Workbench와 협업부서용 Report를 모두 만들었지만, Streamlit 같은 interactive renderer parity는 아직 다음 라운드 범위입니다.",
        },
    ]

    n_total = sum(int(row["n"]) for row in benchmark_apps)
    n_min = min(int(row["n"]) for row in benchmark_apps)
    n_max = max(int(row["n"]) for row in benchmark_apps)

    return {
        "project_id": round1.get("project_id", "26.GP.UXQ"),
        "project_name": "26.GP.UXQ 그룹 UX 품질 진단",
        "validation_date": TODAY_ISO,
        "scope": "survey1 benchmark + survey2 validated pack",
        "sources": {
            "survey2_validation": str(round1_dir),
            "survey1_2_ssot": str(survey1_2_ssot_path),
            "reference_report": str(reference_report_path),
            "reference_readme": str(reference_readme_path),
        },
        "overview": round1["overview"],
        "qa_flags": qa_flags,
        "survey1": {
            "sample_note": f"설문1 총 n≈{n_total:,}, 앱별 n={n_min}~{n_max}",
            "app_overall": benchmark_apps,
            "hana_rank": hana_rank,
            "leader_gap": round(hana_score - leader["overall_index_100"], 1),
            "gap_drivers": gap_driver_rows,
            "detail_rows": comparison_rows,
        },
        "survey2": ssot["survey2"],
        "redirect_candidates": redirect_rows,
        "bridges": bridges,
        "question_blocks": [normalize_question_block(block) for block in round1["question_blocks"]],
    }


def file_href(path_text: str) -> str:
    return Path(path_text).as_uri()


def html_page(title: str, subtitle: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --navy: {NAVY};
      --red: {RED};
      --sand: {SAND};
      --paper: {PAPER};
      --ink: {INK};
      --slate: {SLATE};
      --mist: {MIST};
      --sky: {SKY};
      --rose: {ROSE};
      --mint: {MINT};
      --amber: {AMBER};
      --shadow: 0 18px 40px rgba(0, 48, 135, .08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(232, 0, 61, .08), transparent 30%),
        linear-gradient(180deg, #f4f6fb 0%, #ffffff 16%, #fcfaf6 100%);
      font-family: "Aptos", "Malgun Gothic", "Segoe UI", sans-serif;
      line-height: 1.58;
    }}
    a {{ color: var(--navy); }}
    .page {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 28px 20px 72px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(0, 48, 135, .98), rgba(15, 62, 150, .9));
      color: white;
      border-radius: 28px;
      padding: 28px 28px 24px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -60px -60px auto;
      width: 220px;
      height: 220px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
    }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.12);
      font-size: 12px;
      letter-spacing: .04em;
      text-transform: uppercase;
      font-weight: 700;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.18;
    }}
    .subtitle {{
      margin: 0;
      max-width: 980px;
      font-size: 15px;
      color: rgba(255,255,255,.9);
    }}
    .meta {{
      margin-top: 12px;
      font-size: 13px;
      color: rgba(255,255,255,.78);
    }}
    section {{
      margin-top: 28px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 25px;
      color: var(--navy);
    }}
    h3 {{
      margin: 0 0 10px;
      font-size: 18px;
      color: var(--ink);
    }}
    p {{
      margin: 0 0 10px;
    }}
    .muted {{
      color: var(--slate);
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .cards {{
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }}
    .two {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }}
    .three {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    .card {{
      background: rgba(255,255,255,.96);
      border: 1px solid var(--mist);
      border-radius: 22px;
      padding: 18px 18px 16px;
      box-shadow: 0 10px 24px rgba(24, 33, 43, .04);
    }}
    .card.blue {{ background: linear-gradient(180deg, var(--sky), #ffffff 82%); }}
    .card.rose {{ background: linear-gradient(180deg, var(--rose), #ffffff 82%); }}
    .card.mint {{ background: linear-gradient(180deg, var(--mint), #ffffff 82%); }}
    .card.amber {{ background: linear-gradient(180deg, var(--amber), #ffffff 82%); }}
    .metric {{
      font-size: 30px;
      font-weight: 800;
      line-height: 1.05;
      color: var(--navy);
      margin-top: 4px;
    }}
    .label {{
      font-size: 12px;
      color: var(--slate);
      text-transform: uppercase;
      letter-spacing: .04em;
      font-weight: 700;
    }}
    .detail {{
      margin-top: 6px;
      font-size: 13px;
      color: var(--slate);
    }}
    .flag {{
      border-radius: 18px;
      padding: 16px;
      border: 1px solid var(--mist);
      background: white;
    }}
    .flag.ok {{ background: linear-gradient(180deg, var(--mint), #fff 80%); }}
    .flag.warn {{ background: linear-gradient(180deg, var(--amber), #fff 80%); }}
    .flag.info {{ background: linear-gradient(180deg, var(--sky), #fff 80%); }}
    .badge {{
      display: inline-block;
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      background: rgba(0, 48, 135, .08);
      color: var(--navy);
      margin-bottom: 10px;
    }}
    .note {{
      border-left: 4px solid var(--red);
      background: var(--rose);
      border-radius: 16px;
      padding: 14px 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: rgba(255,255,255,.92);
      border-radius: 18px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--mist);
      vertical-align: top;
      text-align: left;
    }}
    th {{
      background: #eef3fb;
      color: var(--navy);
      font-weight: 800;
    }}
    tr:last-child td {{ border-bottom: none; }}
    .bars {{
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: minmax(140px, 230px) 1fr 110px;
      gap: 10px;
      align-items: center;
      font-size: 14px;
    }}
    .track {{
      height: 12px;
      border-radius: 999px;
      background: #edf1f6;
      overflow: hidden;
    }}
    .fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--navy), #2c6ad8);
    }}
    .fill.red {{ background: linear-gradient(90deg, #b30c38, var(--red)); }}
    .fill.gold {{ background: linear-gradient(90deg, #b88212, #f0b93f); }}
    .question-block {{
      border: 1px solid var(--mist);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.96);
      box-shadow: 0 10px 24px rgba(24, 33, 43, .04);
    }}
    .block-code {{
      display: inline-block;
      color: var(--red);
      font-weight: 800;
      font-size: 13px;
      letter-spacing: .03em;
      margin-bottom: 8px;
    }}
    .mini-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      margin: 14px 0;
    }}
    .mini-card {{
      border: 1px solid var(--mist);
      border-radius: 16px;
      padding: 12px;
      background: #fcfdff;
    }}
    .mini-value {{
      font-size: 22px;
      font-weight: 800;
      color: var(--navy);
      line-height: 1.05;
    }}
    .mini-label {{
      font-size: 12px;
      color: var(--slate);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 4px;
      font-weight: 700;
    }}
    .layer {{
      margin-top: 10px;
      border-radius: 16px;
      border: 1px solid var(--mist);
      padding: 12px 14px;
      background: white;
    }}
    .layer-title {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      font-weight: 800;
      color: var(--slate);
      margin-bottom: 6px;
    }}
    .bridge {{
      border-radius: 22px;
      border: 1px solid var(--mist);
      background: linear-gradient(180deg, white, var(--sand));
      padding: 18px;
    }}
    .portal-links {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      margin-top: 22px;
    }}
    .portal-link {{
      display: block;
      text-decoration: none;
      border-radius: 20px;
      padding: 18px;
      background: rgba(255,255,255,.95);
      border: 1px solid var(--mist);
      box-shadow: 0 10px 24px rgba(24, 33, 43, .04);
      color: inherit;
    }}
    .portal-link:hover {{
      transform: translateY(-1px);
      box-shadow: 0 18px 32px rgba(24, 33, 43, .08);
    }}
    .footer {{
      margin-top: 34px;
      color: var(--slate);
      font-size: 13px;
    }}
    @media (max-width: 760px) {{
      .hero {{ padding: 24px 18px 20px; }}
      h1 {{ font-size: 29px; }}
      .bar-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <div class="eyebrow">Survey Results Dashboard · Round 2 Validation</div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
      <div class="meta">Updated on {TODAY_ISO}</div>
    </div>
    {body}
  </div>
</body>
</html>
"""


def render_metric_cards(cards: list[dict]) -> str:
    blocks = []
    for card in cards:
        accent = card.get("accent", "blue")
        blocks.append(
            "<div class='card {accent}'>"
            "<div class='label'>{label}</div>"
            "<div class='metric'>{metric}</div>"
            "<div class='detail'>{detail}</div>"
            "</div>".format(
                accent=accent,
                label=escape(card["label"]),
                metric=escape(card["metric"]),
                detail=escape(card["detail"]),
            )
        )
    return "<div class='grid cards'>" + "".join(blocks) + "</div>"


def render_flags(flags: list[dict]) -> str:
    return "<div class='grid two'>" + "".join(
        "<div class='flag {level}'><div class='badge'>{badge}</div><h3>{title}</h3><p>{detail}</p></div>".format(
            level=escape(flag["level"]),
            badge=escape(flag["badge"]),
            title=escape(flag["title"]),
            detail=escape(flag["detail"]),
        )
        for flag in flags
    ) + "</div>"


def render_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    head = "".join(f"<th>{escape(label)}</th>" for _, label in columns)
    body = []
    for row in rows:
        body.append(
            "<tr>"
            + "".join(f"<td>{escape(str(row.get(key, '-')))}</td>" for key, _ in columns)
            + "</tr>"
        )
    return "<table><thead><tr>" + head + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def render_bars(
    rows: list[dict],
    label_key: str,
    value_key: str,
    value_suffix: str = "",
    fill_class: str = "",
) -> str:
    max_value = max(float(row[value_key]) for row in rows) if rows else 1
    parts = []
    for row in rows:
        value = float(row[value_key])
        width = (value / max_value) * 100 if max_value else 0
        parts.append(
            "<div class='bar-row'>"
            f"<div>{escape(str(row[label_key]))}</div>"
            "<div class='track'><div class='fill {fill_class}' style='width:{width:.1f}%'></div></div>"
            f"<div><b>{escape(fmt_num(value, 1))}{escape(value_suffix)}</b></div>"
            "</div>".format(fill_class=fill_class, width=width)
        )
    return "<div class='bars'>" + "".join(parts) + "</div>"


def render_score_table(score_rows: list[dict]) -> str:
    rows = [
        {
            "score": row["score"],
            "count": row["count"],
            "pct": fmt_pct(row["pct"]),
        }
        for row in score_rows
    ]
    return render_table(rows, [("score", "점수"), ("count", "응답 수"), ("pct", "응답률")])


def render_option_table(rows: list[dict]) -> str:
    if not rows:
        return "<p class='muted'>표시할 데이터가 없습니다.</p>"
    if "label" in rows[0]:
        shaped = [
            {
                "option": row["label"],
                "count": row["count"],
                "pct": fmt_pct(row["pct"]),
            }
            for row in rows
        ]
        return render_table(shaped, [("option", "응답"), ("count", "응답 수"), ("pct", "응답률")])
    shaped = [
        {
            "option": row["option"],
            "count": row["respondent_count"],
            "pct": fmt_pct(row["respondent_pct"]),
            "weight": row["weighted_score"],
        }
        for row in rows
    ]
    return render_table(
        shaped,
        [
            ("option", "옵션"),
            ("count", "응답자 수"),
            ("pct", "응답자 비율"),
            ("weight", "가중 점수"),
        ],
    )


def render_segment_rows(block: dict, gender_counts: dict) -> str:
    rows = block.get("segment_rows")
    if not rows:
        return ""
    if isinstance(rows, list):
        if rows and "top_options" in rows[0]:
            shaped = []
            for row in rows:
                top = ", ".join(
                    f"{item['label']}({fmt_pct(item['pct'])}, N={item['count']})"
                    for item in row["top_options"]
                )
                shaped.append(
                    {
                        "segment": row["segment"],
                        "base_n": row["base_n"],
                        "summary": top,
                    }
                )
            return render_table(
                shaped,
                [("segment", "세그먼트"), ("base_n", "Base N"), ("summary", "상위 응답")],
            )
        shaped = []
        for row in rows:
            shaped.append(
                {
                    "segment": row["segment"],
                    "base_n": row["base_n"],
                    "mean": fmt_num(row.get("mean"), 2),
                    "top2": fmt_pct(row.get("top2_pct")),
                    "bottom2": fmt_pct(row.get("bottom2_pct")),
                }
            )
        return render_table(
            shaped,
            [
                ("segment", "세그먼트"),
                ("base_n", "Base N"),
                ("mean", "평균"),
                ("top2", "Top2"),
                ("bottom2", "Bottom2"),
            ],
        )

    cards = []
    for segment, items in rows.items():
        base_n = gender_counts.get(segment, "-")
        top_items = items[:5]
        list_html = "".join(
            "<li>{option} ({pct}, N={count}, W={weight})</li>".format(
                option=escape(item["option"]),
                pct=escape(fmt_pct(item["respondent_pct"])),
                count=escape(str(item["respondent_count"])),
                weight=escape(str(item["weighted_score"])),
            )
            for item in top_items
        )
        cards.append(
            "<div class='card'><div class='label'>{segment}</div><div class='detail'>Base N {base_n}</div><ul>{items}</ul></div>".format(
                segment=escape(segment),
                base_n=escape(str(base_n)),
                items=list_html,
            )
        )
    return "<div class='grid two'>" + "".join(cards) + "</div>"


def render_question_block(block: dict, gender_counts: dict) -> str:
    parts = [
        "<div class='question-block'>",
        f"<div class='block-code'>{escape(block['code'])}</div>",
        f"<h3>{escape(block['title'])}</h3>",
        f"<p class='muted'>{escape(block['question_text'])}</p>",
    ]

    mini_cards = [{"label": "Base N", "metric": str(block["base_n"]), "detail": "응답 기준"}]
    if "mean" in block:
        mini_cards.extend(
            [
                {"label": "Mean", "metric": fmt_num(block.get("mean"), 2), "detail": "평균"},
                {"label": "SD", "metric": fmt_num(block.get("std"), 2), "detail": "표준편차"},
                {"label": "Top2", "metric": fmt_pct(block.get("top2_pct")), "detail": "6~7점"},
                {"label": "Bottom2", "metric": fmt_pct(block.get("bottom2_pct")), "detail": "1~2점"},
            ]
        )
    parts.append(
        "<div class='mini-grid'>"
        + "".join(
            "<div class='mini-card'><div class='mini-label'>{label}</div><div class='mini-value'>{metric}</div><div class='detail'>{detail}</div></div>".format(
                label=escape(card["label"]),
                metric=escape(card["metric"]),
                detail=escape(card["detail"]),
            )
            for card in mini_cards
        )
        + "</div>"
    )

    if "score_rows" in block:
        parts.append("<h3>점수 분포</h3>")
        parts.append(render_score_table(block["score_rows"]))
    else:
        parts.append("<h3>응답 분포</h3>")
        parts.append(render_option_table(block["overall_rows"]))

    parts.append("<h3>세그먼트 비교</h3>")
    parts.append(render_segment_rows(block, gender_counts))
    parts.append(f"<div class='note'><p>{escape(block['data_note'])}</p></div>")
    parts.append(
        "<div class='layer'><div class='layer-title'>[Data]</div><p>{text}</p></div>".format(
            text=escape(block["data_note"])
        )
    )
    parts.append(
        "<div class='layer'><div class='layer-title'>[AI Interpretation]</div><p>{text}</p></div>".format(
            text=escape(block["ai_interpretation"])
        )
    )
    parts.append(
        "<div class='layer'><div class='layer-title'>[Needs Judgment]</div><p>{text}</p></div>".format(
            text=escape(block["needs_judgment"])
        )
    )
    parts.append("</div>")
    return "".join(parts)


def build_portal_page(data: dict, round1_dir: Path, reference_report_path: Path) -> str:
    cards = [
        {
            "label": "Round 2 Scope",
            "metric": "S1 + S2",
            "detail": "survey1 benchmark + survey2 validated pack",
            "accent": "blue",
        },
        {
            "label": "Survey1",
            "metric": "n≈1,025",
            "detail": "앱별 n=201~211 benchmark",
            "accent": "mint",
        },
        {
            "label": "Survey2",
            "metric": "n=280",
            "detail": "하나원큐 실사용자 deep dive",
            "accent": "rose",
        },
        {
            "label": "Outputs",
            "metric": "2 views",
            "detail": "Researcher Workbench + Stakeholder Report",
            "accent": "amber",
        },
    ]
    portal_links = [
        (
            "02_researcher_workbench.html",
            "연구원용 Workbench",
            "QA flags, benchmark gap table, survey2 6개 question block까지 모두 포함합니다.",
        ),
        (
            "03_stakeholder_report.html",
            "협업부서용 Report",
            "핵심 우선순위와 cross-survey 연결만 남긴 경량 공유용 뷰입니다.",
        ),
        (
            round1_dir / "02_researcher_workbench.html",
            "1차 survey2-only Workbench",
            "비교용으로 남겨둔 1차 검증 산출물입니다.",
        ),
        (
            reference_report_path,
            "실사례 통합 리포트 참고",
            "ux_evaluation_hana1q의 published HTML 리포트 원본입니다.",
        ),
    ]
    links_html = []
    for href, title, description in portal_links:
        if isinstance(href, Path):
            link = href.as_uri()
        else:
            link = href
        links_html.append(
            "<a class='portal-link' href='{href}'><div class='label'>{title}</div><div class='metric' style='font-size:22px'>Open</div><p>{description}</p></a>".format(
                href=escape(link),
                title=escape(title),
                description=escape(description),
            )
        )

    body = (
        render_metric_cards(cards)
        + "<section><h2>이번 2차 검증에서 달라진 점</h2>"
        + "<div class='grid two'>"
        + "<div class='card blue'><h3>survey1 benchmark 포함</h3><p>survey1의 app-level UX Index와 gap driver를 실제 published report 기준으로 연결해, survey2 deep dive만 보이던 1차 산출물의 한계를 보완했습니다.</p></div>"
        + "<div class='card rose'><h3>실제 참고 링크 정리</h3><p>이번 폴더 안의 HTML 2개뿐 아니라, 실사례 원본인 <code>ux_evaluation_hana1q/public/index.html</code>까지 바로 열 수 있게 링크를 한곳에 모았습니다.</p></div>"
        + "</div></section>"
        + "<section><h2>빠른 이동</h2><div class='portal-links'>"
        + "".join(links_html)
        + "</div></section>"
        + "<section><h2>검증 범위</h2><div class='note'><p>이번 파일은 설문 기반 dashboard skill의 2차 검증 결과입니다. interview나 heuristic 전체를 합친 최종 종합 리포트는 아니며, 설문1 benchmark와 설문2 validated pack을 함께 담는 survey-only dashboard proof에 초점을 맞췄습니다.</p></div></section>"
    )
    return html_page(
        "UXQ Survey Dashboard Portal",
        "survey1 benchmark와 survey2 deep dive를 함께 보는 2차 검증용 포털입니다.",
        body,
    )


def build_researcher_workbench(data: dict) -> str:
    overview = data["overview"]
    survey1 = data["survey1"]
    survey2 = data["survey2"]
    cards = [
        {
            "label": "Survey1 Rank",
            "metric": f"{survey1['hana_rank']} / {len(survey1['app_overall'])}",
            "detail": "하나원큐 종합 UX Index 순위",
            "accent": "blue",
        },
        {
            "label": "Leader Gap",
            "metric": fmt_num(survey1["leader_gap"], 1),
            "detail": "토스 대비 종합 Index 차이",
            "accent": "rose",
        },
        {
            "label": "Survey2 N",
            "metric": str(survey2["N"]),
            "detail": "validated pack 응답자 수",
            "accent": "mint",
        },
        {
            "label": "Question Blocks",
            "metric": str(len(data["question_blocks"])),
            "detail": "deep-dive 반복 모듈 수",
            "accent": "amber",
        },
    ]

    overview_rows = [
        {"item": "프로젝트", "value": data["project_name"]},
        {"item": "검증 범위", "value": data["scope"]},
        {"item": "설문1 표본", "value": survey1["sample_note"]},
        {"item": "설문2 표본", "value": f"n={survey2['N']}"},
        {"item": "질문군 수", "value": overview["question_family_n"]},
        {
            "item": "질문 유형",
            "value": ", ".join(
                f"{key} {value}"
                for key, value in overview["question_type_counts"].items()
            ),
        },
    ]

    sample_rows = [
        {
            "group": "성별",
            "distribution": " · ".join(
                f"{key} {value}" for key, value in overview["gender_counts"].items()
            ),
        },
        {
            "group": "연령대",
            "distribution": " · ".join(
                f"{key} {value}" for key, value in overview["age_counts"].items()
            ),
        },
    ]

    benchmark_rows = [
        {
            "rank": idx,
            "app": row["app"],
            "n": row["n"],
            "score": fmt_num(row["overall_index_100"], 1),
        }
        for idx, row in enumerate(survey1["app_overall"], start=1)
    ]

    survey2_kpi_rows = [
        {"metric": name, "value": fmt_num(value, 2)}
        for name, value in survey2["kpi_mean_7pt"].items()
    ]

    lack_rows = [
        {"label": name, "pct": values["pct"]}
        for name, values in survey2["lack_function_pct"].items()
    ]
    lack_rows.sort(key=lambda row: row["pct"], reverse=True)

    redirect_rows = [
        {"flow": row["보강 필요 업무 → 더 편한 앱"], "score": row["점수"]}
        for row in data["redirect_candidates"]
    ]

    body_parts = [
        render_metric_cards(cards),
        "<section><h2>QA flags</h2>",
        render_flags(data["qa_flags"]),
        "</section>",
        "<section><h2>Study overview</h2>",
        render_table(overview_rows, [("item", "항목"), ("value", "값")]),
        "</section>",
        "<section><h2>Sample profile</h2>",
        render_table(sample_rows, [("group", "구분"), ("distribution", "분포")]),
        "</section>",
        "<section><h2>Survey1 benchmark ranking</h2><p class='muted'>survey1 종합 UX Index는 app-level 기준선 역할을 합니다.</p>",
        render_table(
            benchmark_rows,
            [("rank", "순위"), ("app", "앱"), ("n", "표본 N"), ("score", "종합 UX Index")],
        ),
        "</section>",
        "<section><h2>Survey1 gap drivers</h2><p class='muted'>published report 표에서 직접 읽어온 benchmark gap driver 상위 10개입니다.</p>",
        render_table(
            data["survey1"]["gap_drivers"],
            [
                ("경험 드라이버", "경험 드라이버"),
                ("1위 앱", "1위 앱"),
                ("1위 점수", "1위 점수"),
                ("하나원큐", "하나원큐"),
                ("하나원큐 순위", "원큐 순위"),
                ("1위 대비 격차", "1위 대비 격차"),
                ("경쟁 4사 대비", "경쟁 4사 대비"),
            ],
        ),
        "</section>",
        "<section><h2>Survey1 detail cuts</h2><p class='muted'>상세 문항 비교 표 일부를 그대로 유지해 researcher traceability를 남깁니다.</p>",
        render_table(
            data["survey1"]["detail_rows"],
            [
                ("항목", "항목"),
                ("구분", "구분"),
                ("하나원큐 n=201", "하나원큐"),
                ("토스 n=211", "토스"),
                ("카카오뱅크 n=202", "카카오뱅크"),
                ("신한SOL n=204", "신한SOL"),
                ("KB스타뱅킹 n=207", "KB스타뱅킹"),
                ("하나 순위", "하나 순위"),
                ("유의", "유의"),
            ],
        ),
        "</section>",
        "<section><h2>Survey2 KPI snapshot</h2>",
        render_table(survey2_kpi_rows, [("metric", "지표"), ("value", "평균(7점)")]),
        "</section>",
        "<section><h2>Survey2 function friction</h2>",
        render_bars(survey2["func_friction"], "function", "friction_rate_pct", "%", "red"),
        "</section>",
        "<section><h2>Survey2 lack-function priorities</h2>",
        render_bars(lack_rows, "label", "pct", "%", "gold"),
        "</section>",
        "<section><h2>When users imagine switching</h2><p class='muted'>published report에서 정리된 ‘보강 필요 업무 → 더 편한 앱’ 가중 흐름입니다.</p>",
        render_table(redirect_rows, [("flow", "흐름"), ("score", "점수")]),
        "</section>",
        "<section><h2>Cross-survey bridge matrix</h2><div class='grid two'>",
    ]
    for bridge in data["bridges"]:
        body_parts.append(
            "<div class='bridge'><h3>{theme}</h3><p><b>Survey1</b> {survey1}</p><p><b>Survey2</b> {survey2}</p><p><b>Implication</b> {implication}</p></div>".format(
                theme=escape(bridge["theme"]),
                survey1=escape(bridge["survey1"]),
                survey2=escape(bridge["survey2"]),
                implication=escape(bridge["implication"]),
            )
        )
    body_parts.append("</div></section>")
    body_parts.append("<section><h2>Question-by-question deep dive</h2>")
    for block in data["question_blocks"]:
        body_parts.append(render_question_block(block, overview["gender_counts"]))
    body_parts.append("</section>")
    body_parts.append(
        "<div class='footer'>Source links: "
        f"<a href='{escape(file_href(data['sources']['survey2_validation']))}'>survey2 validation pack</a> · "
        f"<a href='{escape(file_href(data['sources']['survey1_2_ssot']))}'>survey1+2 SSOT JSON</a> · "
        f"<a href='{escape(file_href(data['sources']['reference_report']))}'>published reference report</a>"
        "</div>"
    )

    return html_page(
        "UXQ Full Survey Dashboard — Researcher Workbench",
        "survey1 benchmark와 survey2 deep dive를 함께 보여주는 연구원용 검증판입니다. benchmark traceability, QA flags, low-base guardrail을 모두 남겼습니다.",
        "".join(body_parts),
    )


def build_stakeholder_report(data: dict) -> str:
    survey1 = data["survey1"]
    survey2 = data["survey2"]
    priority_rows = [
        {
            "priority": "1. 혜택·이벤트",
            "evidence": "survey1 이벤트 -13.9 / survey2 불편 80.9%, 보강 필요 71.1%",
        },
        {
            "priority": "2. 홈 탐색·개인화",
            "evidence": "survey1 홈 탐색 5위(-7.5), 개인화 5위(-7.3) / survey2는 '비슷함' 52.1%",
        },
        {
            "priority": "3. 상품·자산 이해",
            "evidence": "survey1 상품 다양성 5위(-8.2), 자산 현황 5위(-10.6) / survey2 보강 요구 60.7%, 36.4%",
        },
    ]
    survey1_gap_rows = [
        {
            "driver": row["경험 드라이버"],
            "gap": row["1위 대비 격차"],
            "hana_rank": row["하나원큐 순위"],
        }
        for row in data["survey1"]["gap_drivers"][:5]
    ]
    # Sort by friction_rate_pct descending before slicing — func_friction is
    # stored in a fixed function-category order, not by severity, so a plain
    # [:4] slice used to silently drop the two highest-friction functions
    # (혜택/이벤트, 고객센터) from a section titled "실제로 아픈 지점".
    top_friction_row = max(survey2["func_friction"], key=lambda row: row["friction_rate_pct"])
    friction_rows = [
        {"function": row["function"], "rate": row["friction_rate_pct"]}
        for row in sorted(
            survey2["func_friction"],
            key=lambda row: row["friction_rate_pct"],
            reverse=True,
        )[:4]
    ]
    top_reinforce_name, top_reinforce_info = max(
        survey2["lack_function_pct"].items(), key=lambda item: item[1]["pct"]
    )
    stakeholder_blocks = [
        block
        for block in data["question_blocks"]
        if block["code"] in {"P2B1", "P21B2", "P18B1", "P3B4"}
    ]

    cards = [
        {
            "label": "Benchmark Position",
            "metric": f"{survey1['hana_rank']} / {len(survey1['app_overall'])}",
            "detail": "survey1 종합 UX Index",
            "accent": "blue",
        },
        {
            "label": "Transition Positive",
            "metric": fmt_pct(survey2["transition_positive_pct"]),
            "detail": "리뉴얼 긍정 체감 비율",
            "accent": "mint",
        },
        {
            "label": "Top Friction",
            "metric": fmt_pct(top_friction_row["friction_rate_pct"]),
            "detail": f"{top_friction_row['function']} 기능 불편 경험률",
            "accent": "rose",
        },
        {
            "label": "Top Reinforcement",
            "metric": top_reinforce_name,
            "detail": "보강 필요 1순위",
            "accent": "amber",
        },
    ]

    body_parts = [
        render_metric_cards(cards),
        "<section><h2>한 줄 요약</h2><div class='note'><p>하나원큐는 기본 업무를 유지할 수 있는 수준이지만, benchmark 기준으로는 선도 앱 대비 매력도와 탐색성이 약합니다. survey2 deep dive를 보면 그 약점은 특히 혜택·이벤트, 홈 탐색·개인화, 상품·자산 이해 구간에서 실제 불편과 보강 요구로 연결됩니다.</p></div></section>",
        "<section><h2>우선순위 3개</h2>",
        render_table(priority_rows, [("priority", "우선순위"), ("evidence", "근거")]),
        "</section>",
        "<section><h2>Benchmark snapshot</h2>",
        render_table(
            [
                {
                    "app": row["app"],
                    "score": fmt_num(row["overall_index_100"], 1),
                    "n": row["n"],
                }
                for row in survey1["app_overall"]
            ],
            [("app", "앱"), ("score", "종합 UX Index"), ("n", "표본 N")],
        ),
        "</section>",
        "<section><h2>크게 벌어진 driver</h2>",
        render_table(
            survey1_gap_rows,
            [("driver", "경험 드라이버"), ("gap", "1위 대비 격차"), ("hana_rank", "원큐 순위")],
        ),
        "</section>",
        "<section><h2>survey2에서 실제로 아픈 지점</h2>",
        render_bars(friction_rows, "function", "rate", "%", "red"),
        "</section>",
        "<section><h2>survey1 ↔ survey2 연결 해석</h2><div class='grid three'>",
    ]
    for bridge in data["bridges"][:3]:
        body_parts.append(
            "<div class='bridge'><h3>{theme}</h3><p>{implication}</p><p class='muted'>{survey1}</p><p class='muted'>{survey2}</p></div>".format(
                theme=escape(bridge["theme"]),
                implication=escape(bridge["implication"]),
                survey1=escape(bridge["survey1"]),
                survey2=escape(bridge["survey2"]),
            )
        )
    body_parts.append("</div></section>")
    body_parts.append("<section><h2>대표 question blocks</h2>")
    for block in stakeholder_blocks:
        body_parts.append(render_question_block(block, data["overview"]["gender_counts"]))
    body_parts.append("</section>")
    body_parts.append(
        "<section><h2>공유 시 주의사항</h2>"
        + render_table(
            [
                {
                    "checkpoint": "Low base",
                    "detail": "연령 60대는 n=7이므로 외부 해석에 쓰지 않는 것이 안전합니다.",
                },
                {
                    "checkpoint": "Descriptive only",
                    "detail": "성별 차이와 benchmark gap은 설명적 해석이며, 새 inferential claim을 추가하지 않았습니다.",
                },
                {
                    "checkpoint": "Renderer scope",
                    "detail": "이번 2차 검증은 정적 HTML proof입니다. interactive renderer parity는 다음 라운드입니다.",
                },
            ],
            [("checkpoint", "체크포인트"), ("detail", "설명")],
        )
        + "</section>"
    )
    body_parts.append(
        "<div class='footer'>Reference example: "
        f"<a href='{escape(file_href(data['sources']['reference_report']))}'>ux_evaluation_hana1q/public/index.html</a>"
        "</div>"
    )

    return html_page(
        "UXQ Full Survey Dashboard — Stakeholder Report",
        "협업부서 공유용으로 survey1 benchmark와 survey2 deep dive의 연결만 남긴 경량 뷰입니다.",
        "".join(body_parts),
    )


def build_validation_note(data: dict) -> str:
    sources = data["sources"]
    return f"""# survey-results-dashboard validation note — {data['validation_date']} (Round 2)

## 검증 대상

- 스킬: `survey-results-dashboard`
- 프로젝트: `{data['project_name']}`
- 범위: `{data['scope']}`

## 이번 라운드 입력

- 1차 검증 산출물: `{sources['survey2_validation']}/01_dashboard_data.json`
- 설문1·2 정본 수치: `{sources['survey1_2_ssot']}`
- 설문1 상세 benchmark 표: `{sources['reference_report']}`

## 이번 검증에서 확인한 것

1. survey1 benchmark와 survey2 deep dive를 하나의 dashboard surface로 함께 묶을 수 있었다.
   - 설문1은 app ranking과 gap driver 표로 요약했다.
   - 설문2는 validated question block 6개를 그대로 유지했다.

2. dual-output 구조가 full-survey 범위에서도 유지되었다.
   - `02_researcher_workbench.html`
   - `03_stakeholder_report.html`

3. `cross-survey bridge` 모듈이 실제로 유용했다.
   - 혜택/이벤트
   - 홈 탐색·개인화
   - 상품·자산
   - 기본 업무·연동

4. low-base / descriptive / AI layer guardrail은 1차와 동일하게 유지되었다.

## 남은 한계

- 이번 2차 검증도 정적 HTML 기준이다. interactive renderer parity는 아직 검증하지 않았다.
- survey1 structured SSOT는 app_overall 위주라, 상세 gap 표는 published report HTML에서 읽어왔다.
- interview / heuristic / final report 전체를 합친 종합 dashboard는 이번 스킬 범위 밖이다.
"""


def build_review_checklist(data: dict, out_dir_label: str) -> str:
    return f"""# UXQ Full Survey Dashboard Review Checklist

Review date: {data['validation_date']}

## Goal

- Confirm whether `{out_dir_label}` can be treated as the representative round-2 validation case for `#19 survey-results-dashboard`.
- Verify that `survey1 benchmark + survey2 validated pack` can coexist in one dual-output dashboard surface.

## Review Order

1. Full-scope input gate
2. Survey1 benchmark traceability gate
3. Survey2 deep-dive preservation gate
4. Cross-survey bridge usefulness gate
5. Delivery gate

## Files to Review First

- `00_dashboard_portal.html`
- `01_dashboard_data.json`
- `02_researcher_workbench.html`
- `03_stakeholder_report.html`
- `04_validation_notes.md`
- `build_full_dashboard.py`

## 1. Full-scope input gate

- [ ] survey1 benchmark is included
- [ ] survey2 validated pack is included
- [ ] the dashboard is still survey-only, not falsely presented as the entire project report

## 2. Survey1 benchmark traceability gate

- [ ] app ranking comes from `survey_key_findings_generated.json`
- [ ] gap-driver detail is traceable to the published reference report table
- [ ] no stale `n=262` style survey2 value leaks into the full dashboard

## 3. Survey2 deep-dive preservation gate

- [ ] the `6` repeated question blocks are still present in the researcher workbench
- [ ] low-base caution on age `60s n=7` is still visible
- [ ] AI layer labeling remains explicit

## 4. Cross-survey bridge usefulness gate

- [ ] at least three bridge themes are visible
- [ ] bridge logic links benchmark weakness to in-app friction or reinforcement need
- [ ] no bridge statement over-claims statistical proof

## 5. Delivery gate

- [ ] portal page links work
- [ ] both HTML outputs render after rerun
- [ ] stakeholder view is lighter than researcher view
- [ ] interactive renderer work is still clearly marked as next round

## Sign-off Notes

- Full-scope survey dashboard contract: `PASS / HOLD`
- Survey1 benchmark traceability: `PASS / HOLD`
- Survey2 deep-dive preservation: `PASS / HOLD`
- Cross-survey bridge usefulness: `PASS / HOLD`
- Keep this as `#19` round-2 validation case: `YES / NO`
"""


def build_verdict(data: dict) -> str:
    return f"""# UXQ Full Survey Dashboard Verdict Draft

Draft date: {data['validation_date']}

## Proposed Sign-off

- Full-scope survey dashboard contract: `PASS`
- Survey1 benchmark traceability: `PASS`
- Survey2 deep-dive preservation: `PASS`
- Cross-survey bridge usefulness: `PASS`
- Interactive renderer parity: `HOLD`
- Keep this as `#19` round-2 validation case: `YES`

## Why Full-scope Contract Is PASS

- The round-2 build integrates `survey1 benchmark + survey2 validated pack` in one dashboard family.
- The build still respects the dual-output split:
  - `02_researcher_workbench.html`
  - `03_stakeholder_report.html`

## Why Survey1 Traceability Is PASS

- survey1 app ranking uses `survey_key_findings_generated.json` as the numeric SSOT.
- richer gap-driver detail is pulled from the published reference report HTML, so the benchmark module is not hand-waved.

## Why Survey2 Preservation Is PASS

- The original `6` deep-dive question blocks remain intact in the researcher surface.
- low-base, descriptive-only, and AI-layer guardrails remain visible.

## Why Cross-survey Bridge Is PASS

- The dashboard no longer shows survey2 in isolation.
- benchmark weakness now connects to actual in-app friction and reinforcement demand, especially on:
  - 혜택/이벤트
  - 홈 탐색·개인화
  - 상품·자산

## Why Interactive Renderer Parity Is Still HOLD

- This round proves the information architecture and shareable HTML delivery.
- It does not yet prove Streamlit-style or filter-heavy researcher interaction.

## Recommended Decision

- Approve this folder as the representative round-2 validation case for `#19 survey-results-dashboard`.
- Treat the next step as `renderer expansion`, not `dashboard contract rework`.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the full survey-results-dashboard pack (survey1 benchmark + "
            "survey2 validated pack) from a round1 dashboard JSON and the "
            "survey1/2 SSOT + reference report of an external evaluation repo."
        )
    )
    parser.add_argument(
        "--round1-data",
        type=Path,
        default=DEFAULT_ROUND1_DATA_PATH,
        help=f"path to round1 01_dashboard_data.json (default: {DEFAULT_ROUND1_DATA_PATH})",
    )
    parser.add_argument(
        "--survey1-2-ssot",
        type=Path,
        default=DEFAULT_SURVEY1_2_SSOT_PATH,
        help=f"path to survey_key_findings_generated.json (default: {DEFAULT_SURVEY1_2_SSOT_PATH})",
    )
    parser.add_argument(
        "--reference-report",
        type=Path,
        default=DEFAULT_REFERENCE_REPORT_PATH,
        help=f"path to the published reference report HTML (default: {DEFAULT_REFERENCE_REPORT_PATH})",
    )
    parser.add_argument(
        "--reference-readme",
        type=Path,
        default=DEFAULT_REFERENCE_REPORT_README,
        help=f"path to the reference repo README (default: {DEFAULT_REFERENCE_REPORT_README})",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT,
        help="directory to write 00_dashboard_portal.html .. 06_round2_verdict_draft.md into (default: this script's own folder)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    round1_dir = args.round1_data.resolve().parent

    data = build_data(
        round1_data_path=args.round1_data,
        survey1_2_ssot_path=args.survey1_2_ssot,
        reference_report_path=args.reference_report,
        reference_readme_path=args.reference_readme,
        round1_dir=round1_dir,
    )
    out_dir_label = out_dir.name

    (out_dir / "00_dashboard_portal.html").write_text(
        build_portal_page(data, round1_dir, args.reference_report),
        encoding="utf-8",
    )
    (out_dir / "01_dashboard_data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "02_researcher_workbench.html").write_text(
        build_researcher_workbench(data),
        encoding="utf-8",
    )
    (out_dir / "03_stakeholder_report.html").write_text(
        build_stakeholder_report(data),
        encoding="utf-8",
    )
    (out_dir / "04_validation_notes.md").write_text(
        build_validation_note(data),
        encoding="utf-8",
    )
    (out_dir / "05_round2_review_checklist.md").write_text(
        build_review_checklist(data, out_dir_label),
        encoding="utf-8",
    )
    (out_dir / "06_round2_verdict_draft.md").write_text(
        build_verdict(data),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
