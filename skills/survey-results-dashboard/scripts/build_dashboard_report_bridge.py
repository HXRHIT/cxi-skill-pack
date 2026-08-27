from __future__ import annotations

import argparse
import html
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT / "01_dashboard_data.json"
DEFAULT_STAKEHOLDER_PATH = ROOT / "03_stakeholder_report.html"
DEFAULT_HANDOFF_PATH = ROOT / "09_report_writer_handoff.md"
TODAY_ISO = date.today().isoformat()


def read_data(data_path: Path) -> dict:
    return json.loads(data_path.read_text(encoding="utf-8"))


def fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{float(value):.1f}%"


def fmt_num(value: float | int | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, int) or float(value).is_integer():
        return f"{int(value)}"
    return f"{float(value):.2f}"


def fmt_pct_n(pct: float | int | None, count: int | None) -> str:
    pct_text = fmt_pct(pct)
    if count is None:
        return pct_text
    return f"{pct_text}, N={count}"


def block_by_code(data: dict) -> dict[str, dict]:
    return {block["code"]: block for block in data["question_blocks"]}


def top_friction(data: dict) -> dict:
    return max(data["survey2"]["func_friction"], key=lambda row: row["friction_rate_pct"])


def top_reinforcement(data: dict) -> tuple[str, dict]:
    items = data["survey2"]["lack_function_pct"].items()
    return max(items, key=lambda item: item[1]["pct"])


def sorted_choice_rows(block: dict) -> list[dict]:
    rows = list(block.get("overall_rows", []))
    if not rows:
        return rows
    if "weighted_score" in rows[0]:
        return sorted(
            rows,
            key=lambda row: (
                -float(row.get("weighted_score", 0)),
                -float(row.get("respondent_count", 0)),
                str(row.get("option", "")),
            ),
        )
    return sorted(
        rows,
        key=lambda row: (
            -float(row.get("count", 0)),
            -float(row.get("pct", 0)),
            str(row.get("label", "")),
        ),
    )


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        "<table><thead><tr>"
        f"{header_html}"
        "</tr></thead><tbody>"
        f"{''.join(body_rows)}"
        "</tbody></table>"
    )


def render_scale_block(block: dict) -> str:
    score_rows = block.get("score_rows", [])
    dist_rows = [
        [
            html.escape(str(row["score"])),
            html.escape(fmt_num(row["count"])),
            html.escape(fmt_pct_n(row["pct"], row["count"])),
        ]
        for row in score_rows
    ]
    segment_rows = [
        [
            html.escape(row["segment"]),
            html.escape(fmt_num(row["base_n"])),
            html.escape(fmt_num(row.get("mean"))),
            html.escape(fmt_pct(row.get("top2_pct"))),
            html.escape(fmt_pct(row.get("bottom2_pct"))),
        ]
        for row in block.get("segment_rows", [])
    ]
    return f"""
    <div class="question-block">
      <div class="code">{html.escape(block["code"])}</div>
      <h3>{html.escape(block["title"])}</h3>
      <p class="muted">{html.escape(block["question_text"])}</p>
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-label">Base</div><div class="metric-value">{html.escape(fmt_num(block["base_n"]))}</div></div>
        <div class="metric-card"><div class="metric-label">Mean</div><div class="metric-value">{html.escape(fmt_num(block.get("mean")))}</div></div>
        <div class="metric-card"><div class="metric-label">SD</div><div class="metric-value">{html.escape(fmt_num(block.get("std")))}</div></div>
        <div class="metric-card"><div class="metric-label">Top2</div><div class="metric-value">{html.escape(fmt_pct(block.get("top2_pct")))}</div></div>
        <div class="metric-card"><div class="metric-label">Bottom2</div><div class="metric-value">{html.escape(fmt_pct(block.get("bottom2_pct")))}</div></div>
      </div>
      {html_table(["점수", "응답 수", "비율"], dist_rows)}
      {html_table(["세그먼트", "Base", "평균", "Top2", "Bottom2"], segment_rows)}
      <div class="layer"><div class="layer-title">Data</div><p>{html.escape(block["data_note"])}</p></div>
      <div class="layer"><div class="layer-title">AI Interpretation</div><p>{html.escape(block["ai_interpretation"])}</p></div>
      <div class="layer"><div class="layer-title">Needs Judgment</div><p>{html.escape(block["needs_judgment"])}</p></div>
    </div>
    """


def render_choice_block(block: dict) -> str:
    rows = sorted_choice_rows(block)
    if rows and "weighted_score" in rows[0]:
        table_rows = [
            [
                html.escape(row["option"]),
                html.escape(fmt_num(row["respondent_count"])),
                html.escape(fmt_pct_n(row["respondent_pct"], row["respondent_count"])),
                html.escape(fmt_num(row["weighted_score"])),
            ]
            for row in rows
        ]
        headers = ["응답 옵션", "응답자 수", "비율", "가중 점수"]
    else:
        table_rows = [
            [
                html.escape(row["label"]),
                html.escape(fmt_num(row["count"])),
                html.escape(fmt_pct_n(row["pct"], row["count"])),
            ]
            for row in rows
        ]
        headers = ["응답 옵션", "응답 수", "비율"]

    segment_blocks = []
    segment_rows = block.get("segment_rows", {})
    if isinstance(segment_rows, dict):
        items = segment_rows.items()
    else:
        items = [(row["segment"], row.get("top_options", [])) for row in segment_rows]

    for segment, values in items:
        bullets = []
        for row in values[:5]:
            label = row.get("label") or row.get("option") or "-"
            count = row.get("count", row.get("respondent_count"))
            pct = row.get("pct", row.get("respondent_pct"))
            weighted = row.get("weighted_score")
            extra = f", W={fmt_num(weighted)}" if weighted is not None else ""
            bullets.append(
                f"<li>{html.escape(label)} ({html.escape(fmt_pct_n(pct, count))}{html.escape(extra)})</li>"
            )
        segment_blocks.append(
            f"""
            <div class="segment-card">
              <div class="segment-title">{html.escape(str(segment))}</div>
              <ul>{''.join(bullets)}</ul>
            </div>
            """
        )

    return f"""
    <div class="question-block">
      <div class="code">{html.escape(block["code"])}</div>
      <h3>{html.escape(block["title"])}</h3>
      <p class="muted">{html.escape(block["question_text"])}</p>
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-label">Base</div><div class="metric-value">{html.escape(fmt_num(block["base_n"]))}</div></div>
      </div>
      {html_table(headers, table_rows)}
      <div class="segment-grid">{''.join(segment_blocks)}</div>
      <div class="layer"><div class="layer-title">Data</div><p>{html.escape(block["data_note"])}</p></div>
      <div class="layer"><div class="layer-title">AI Interpretation</div><p>{html.escape(block["ai_interpretation"])}</p></div>
      <div class="layer"><div class="layer-title">Needs Judgment</div><p>{html.escape(block["needs_judgment"])}</p></div>
    </div>
    """


def render_stakeholder_html(data: dict) -> str:
    blocks = block_by_code(data)
    friction = top_friction(data)
    reinforce_name, reinforce_info = top_reinforcement(data)
    rank_total = len(data["survey1"]["app_overall"])
    workflow_cards = """
    <div class="workflow">
      <div class="workflow-step done"><span>1</span><strong>Dashboard</strong><p>validated stats를 질문 단위로 점검</p></div>
      <div class="workflow-step current"><span>2</span><strong>Insight Review</strong><p>협업부서와 핵심 메시지와 caveat를 정렬</p></div>
      <div class="workflow-step"><span>3</span><strong>Interim Report</strong><p><a href="09_report_writer_handoff.md">report-writer handoff</a>를 바탕으로 문서화</p></div>
    </div>
    """
    bridge_rows = [
        [
            html.escape(item["theme"]),
            html.escape(item["survey1"]),
            html.escape(item["survey2"]),
            html.escape(item["implication"]),
        ]
        for item in data["bridges"]
    ]

    key_claims = [
        (
            "하나원큐는 benchmark 상 열위가 분명하지만, 모든 영역이 무너진 상태는 아닙니다.",
            f"survey1 종합 UX Index는 {data['survey1']['hana_rank']}위/{rank_total}개 앱이며, 선두와 격차는 {data['survey1']['leader_gap']}점입니다.",
        ),
        (
            "리뉴얼 체감은 있었지만, 다수는 '더 좋아졌다'보다 '비슷하다'에 머물렀습니다.",
            "P2B1에서 '비슷함'은 "
            f"{fmt_pct_n(52.1, 146)}이며, 개선 응답 합계는 {fmt_pct(36.8)}입니다.",
        ),
        (
            "혜택/이벤트와 상품·서비스 다양성이 보고서 전 단계에서 가장 먼저 합의해야 할 개선 축입니다.",
            f"survey2에서 혜택/이벤트 보강 요구는 {fmt_pct_n(reinforce_info['pct'], reinforce_info['n'])}이고, "
            f"{friction['function']} 기능의 불편 경험률은 {fmt_pct_n(friction['friction_rate_pct'], friction['friction_n'])}입니다.",
        ),
    ]
    claim_cards = "".join(
        f"""
        <div class="card soft-blue">
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(detail)}</p>
        </div>
        """
        for title, detail in key_claims
    )

    report_map_rows = [
        ["study_overview", "조사 범위, 표본, survey1/survey2 역할 분리", "09_report_writer_handoff.md"],
        ["key_findings", "핵심 주장 3개와 bridge theme", "이 페이지의 핵심 메시지 섹션"],
        ["competitive_position", "survey1 benchmark rank, gap driver", "survey1 benchmark snapshot"],
        ["missing_features_or_pain_points", "P18B1, P3B4", "문항 하이라이트"],
        ["next_interview_plan", "정성 확인 질문", "09_report_writer_handoff.md"],
    ]

    question_blocks_html = (
        render_choice_block(blocks["P2B1"])
        + render_scale_block(blocks["P21B2"])
        + render_choice_block(blocks["P18B1"])
        + render_choice_block(blocks["P3B4"])
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UXQ Full Survey Dashboard - Stakeholder Insight Review</title>
  <style>
    :root {{
      --navy: #0f2f73;
      --blue: #2f6dd7;
      --ink: #18212b;
      --slate: #5a6775;
      --mist: #d7dee6;
      --paper: #fbfaf7;
      --sky: #eef4ff;
      --mint: #eef8f2;
      --rose: #fff1f4;
      --amber: #fff5e4;
      --shadow: 0 18px 44px rgba(15, 47, 115, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(47, 109, 215, 0.08), transparent 28%),
        linear-gradient(180deg, #f5f7fb 0%, #ffffff 18%, #fdf9f2 100%);
      font-family: "Aptos", "Malgun Gothic", "Segoe UI", sans-serif;
      line-height: 1.58;
    }}
    a {{ color: var(--navy); }}
    .page {{ max-width: 1360px; margin: 0 auto; padding: 28px 20px 72px; }}
    .hero {{
      position: relative;
      overflow: hidden;
      border-radius: 28px;
      padding: 30px 30px 24px;
      background: linear-gradient(135deg, rgba(15, 47, 115, 0.98), rgba(31, 80, 171, 0.94));
      color: white;
      box-shadow: var(--shadow);
    }}
    .hero::after {{
      content: "";
      position: absolute;
      right: -40px;
      bottom: -40px;
      width: 220px;
      height: 220px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.12);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 0 0 10px; font-size: 34px; line-height: 1.18; }}
    .subtitle {{ max-width: 980px; margin: 0; font-size: 15px; color: rgba(255,255,255,0.92); }}
    .meta {{ margin-top: 12px; font-size: 13px; color: rgba(255,255,255,0.78); }}
    section {{ margin-top: 28px; }}
    h2 {{ margin: 0 0 14px; font-size: 24px; color: var(--navy); }}
    h3 {{ margin: 0 0 10px; font-size: 19px; }}
    p {{ margin: 0 0 10px; }}
    .muted {{ color: var(--slate); }}
    .grid {{ display: grid; gap: 16px; }}
    .cards {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
    .two {{ grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
    .card {{
      border: 1px solid var(--mist);
      border-radius: 22px;
      background: rgba(255, 255, 255, 0.96);
      padding: 18px;
      box-shadow: 0 10px 28px rgba(24, 33, 43, 0.05);
    }}
    .soft-blue {{ background: linear-gradient(180deg, var(--sky), #ffffff 84%); }}
    .soft-mint {{ background: linear-gradient(180deg, var(--mint), #ffffff 84%); }}
    .soft-rose {{ background: linear-gradient(180deg, var(--rose), #ffffff 84%); }}
    .soft-amber {{ background: linear-gradient(180deg, var(--amber), #ffffff 84%); }}
    .label {{ font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; color: var(--slate); }}
    .big {{ margin-top: 6px; font-size: 31px; line-height: 1.05; font-weight: 800; color: var(--navy); }}
    .small {{ margin-top: 8px; font-size: 13px; color: var(--slate); }}
    .workflow {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin-top: 22px;
    }}
    .workflow-step {{
      border-radius: 18px;
      border: 1px solid var(--mist);
      background: rgba(255,255,255,0.96);
      padding: 16px;
    }}
    .workflow-step span {{
      display: inline-flex;
      width: 28px;
      height: 28px;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      background: var(--sky);
      color: var(--navy);
      font-weight: 800;
      margin-bottom: 10px;
    }}
    .workflow-step.done {{ background: linear-gradient(180deg, var(--mint), #ffffff 82%); }}
    .workflow-step.current {{ background: linear-gradient(180deg, var(--amber), #ffffff 82%); border-color: #e8d29d; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: rgba(255,255,255,0.94);
      border-radius: 18px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--mist);
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #eef3fb; color: var(--navy); font-weight: 800; }}
    tr:last-child td {{ border-bottom: none; }}
    .note {{
      border-left: 4px solid #d43d51;
      border-radius: 18px;
      padding: 16px 18px;
      background: var(--rose);
    }}
    .question-block {{
      border: 1px solid var(--mist);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,0.96);
      box-shadow: 0 10px 24px rgba(24, 33, 43, 0.04);
      margin-top: 18px;
    }}
    .code {{
      display: inline-block;
      color: #d43d51;
      font-weight: 800;
      font-size: 13px;
      letter-spacing: 0.03em;
      margin-bottom: 8px;
    }}
    .metric-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      margin: 14px 0;
    }}
    .metric-card {{
      border: 1px solid var(--mist);
      border-radius: 16px;
      background: #fcfdff;
      padding: 12px;
    }}
    .metric-label {{
      font-size: 12px;
      color: var(--slate);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-weight: 800;
    }}
    .metric-value {{
      margin-top: 4px;
      font-size: 24px;
      line-height: 1.05;
      font-weight: 800;
      color: var(--navy);
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
      letter-spacing: 0.04em;
      font-weight: 800;
      color: var(--slate);
      margin-bottom: 6px;
    }}
    .segment-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      margin-top: 14px;
    }}
    .segment-card {{
      border: 1px solid var(--mist);
      border-radius: 16px;
      padding: 14px;
      background: #fcfdff;
    }}
    .segment-title {{
      font-size: 14px;
      font-weight: 800;
      color: var(--navy);
      margin-bottom: 8px;
    }}
    ul {{ margin: 0; padding-left: 18px; }}
    li + li {{ margin-top: 6px; }}
    .footer {{ margin-top: 36px; color: var(--slate); font-size: 13px; }}
    @media (max-width: 760px) {{
      .page {{ padding: 18px 14px 48px; }}
      .hero {{ padding: 24px 18px 20px; }}
      h1 {{ font-size: 28px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <div class="eyebrow">Survey Results Dashboard · Insight Review Layer</div>
      <h1>UXQ Stakeholder Insight Review</h1>
      <p class="subtitle">
        이 파일은 정식 interim report가 아니라, dashboard 이후 협업부서와 핵심 메시지와 caveat를 빠르게 정렬하기 위한
        pre-report review view입니다. 문서형 보고서는 <a href="09_report_writer_handoff.md" style="color:#fff;text-decoration:underline;">report-writer handoff</a>를 거쳐 후속 작성합니다.
      </p>
      <div class="meta">Updated on {TODAY_ISO} · Scope: survey1 benchmark + survey2 validated pack</div>
    </div>

    {workflow_cards}

    <section class="grid cards">
      <div class="card soft-blue">
        <div class="label">Benchmark Position</div>
        <div class="big">{data['survey1']['hana_rank']} / {rank_total}</div>
        <div class="small">survey1 종합 UX Index 기준 하나원큐 순위</div>
      </div>
      <div class="card soft-mint">
        <div class="label">Transition Positive</div>
        <div class="big">{fmt_pct(data['survey2']['transition_positive_pct'])}</div>
        <div class="small">리뉴얼 개선 체감 응답 합계</div>
      </div>
      <div class="card soft-rose">
        <div class="label">Top Friction</div>
        <div class="big">{html.escape(friction['function'])}</div>
        <div class="small">{fmt_pct_n(friction['friction_rate_pct'], friction['friction_n'])} · 경험자 base {friction['experienced_n']}</div>
      </div>
      <div class="card soft-amber">
        <div class="label">Top Reinforcement</div>
        <div class="big">{html.escape(reinforce_name)}</div>
        <div class="small">{fmt_pct_n(reinforce_info['pct'], reinforce_info['n'])} · survey2 전체 base {data['survey2']['N']}</div>
      </div>
    </section>

    <section>
      <h2>이번 파일의 역할</h2>
      <div class="note">
        <p>
          dashboard 단계에서는 질문별 결과와 bridge logic을 안정적으로 보여주고,
          이 insight review 단계에서는 "무슨 메시지를 정식 보고서에 싣기로 합의할지"를 빠르게 결정합니다.
          따라서 여기서는 완결된 서사형 보고서를 쓰지 않고, 핵심 주장과 검토 포인트를 응축해서 보여줍니다.
        </p>
      </div>
    </section>

    <section>
      <h2>보고서 작성 전에 합의할 핵심 메시지</h2>
      <div class="grid two">{claim_cards}</div>
    </section>

    <section>
      <h2>Cross-survey Bridge Snapshot</h2>
      {html_table(["브리지 테마", "survey1 signal", "survey2 signal", "보고서 시사점"], bridge_rows)}
    </section>

    <section>
      <h2>Report Writer Handoff Preview</h2>
      <p class="muted">문서형 interim report는 아래 구조를 기준으로 후속 작성합니다. 이 파일 자체가 최종 보고서 본문을 대체하지는 않습니다.</p>
      {html_table(["보고서 섹션", "이번 대시보드에서 넘길 근거", "후속 산출물"], report_map_rows)}
    </section>

    <section>
      <h2>문항 하이라이트</h2>
      {question_blocks_html}
    </section>

    <section>
      <h2>공유 전 주의사항</h2>
      {html_table(
            ["체크포인트", "설명"],
            [
                ["Low base", "연령 60대는 n=7이므로, 외부 공유 해석에서는 세부 연령 비교를 확장하지 않는 편이 안전합니다."],
                ["Descriptive boundary", "성별 비교와 cross-survey bridge는 설명적 해석입니다. 유의성 검정이나 인과 판단으로 쓰지 않습니다."],
                ["Workflow boundary", "이 파일은 insight review용입니다. 정식 survey interim report는 09_report_writer_handoff.md를 입력으로 survey-interim-report-writer에서 별도 작성합니다."],
            ],
        )}
    </section>

    <div class="footer">
      Created from validated dashboard data on {TODAY_ISO}. Next recommended step: review this view, then draft the formal survey interim report from <a href="09_report_writer_handoff.md">09_report_writer_handoff.md</a>.
    </div>
  </div>
</body>
</html>
"""


def render_handoff_markdown(data: dict, out_dir_label: str) -> str:
    blocks = block_by_code(data)
    reinforce_name, reinforce_info = top_reinforcement(data)
    top_gap = data["survey1"]["gap_drivers"][0]
    benchmark_rows = data["survey1"]["app_overall"]
    benchmark_table = "\n".join(
        f"| {row['app']} | {row['overall_index_100']} | {row['n']} |"
        for row in benchmark_rows
    )
    hana_row = next(row for row in benchmark_rows if row["app"] == "하나원큐")
    leader_row = benchmark_rows[0]
    age_counts = data["overview"]["age_counts"]
    low_base_age, low_base_n = min(age_counts.items(), key=lambda item: item[1])
    top5_gap_bullets = "\n".join(
        f"  - {row['경험 드라이버']}: 선두 대비 `{row['1위 대비 격차']}`"
        for row in data["survey1"]["gap_drivers"][:5]
    )
    p2b1 = blocks["P2B1"]
    p21b2 = blocks["P21B2"]
    p19b4 = blocks["P19B4"]
    p18b1 = blocks["P18B1"]
    p3b4 = blocks["P3B4"]
    similar_row = next(
        (row for row in p2b1.get("overall_rows", []) if row["label"] == "비슷함"),
        None,
    )
    # P2B1 options use "쉬워짐" (became easier) for the improvement side and
    # "불편해짐" (became less convenient) for the regression side — there is
    # no literal "개선"/"좋아" substring in the labels, so matching on those
    # words (as an earlier draft of this function did) silently summed to 0.
    improve_pct = sum(
        float(row["pct"])
        for row in p2b1.get("overall_rows", [])
        if "쉬워짐" in row["label"]
    )
    bridge_bullets = "\n".join(
        f"- **{item['theme']}**: survey1에서는 {item['survey1']}, survey2에서는 {item['survey2']}이 확인되어 {item['implication']}"
        for item in data["bridges"]
    )
    top_p18 = sorted_choice_rows(p18b1)[:5]
    top_p18_bullets = "\n".join(
        f"- {row['option']}: {fmt_pct_n(row['respondent_pct'], row['respondent_count'])}, 가중 점수 {fmt_num(row['weighted_score'])}"
        for row in top_p18
    )
    top_p3 = sorted_choice_rows(p3b4)[:5]
    top_p3_bullets = "\n".join(
        f"- {row['option']}: {fmt_pct_n(row['respondent_pct'], row['respondent_count'])}, 가중 점수 {fmt_num(row['weighted_score'])}"
        for row in top_p3
    )
    top2_friction = sorted(
        data["survey2"]["func_friction"],
        key=lambda row: row["friction_rate_pct"],
        reverse=True,
    )[:2]
    top2_friction_bullets = "\n".join(
        f"- {row['function']}: 경험자 `{row['experienced_n']}`명 중 `{row['friction_n']}`명, `{fmt_pct(row['friction_rate_pct'])}`"
        for row in top2_friction
    )
    return f"""# Dashboard to Report Handoff — {data['validation_date']}

이 문서는 `survey-results-dashboard`의 2차 검증 산출물을 `survey-interim-report-writer`로 넘기기 위한 pre-report handoff 초안입니다.

대상 폴더:
- `{out_dir_label}`

업무 순서:
1. dashboard에서 질문별 수치와 bridge logic 검토
2. insight review에서 핵심 메시지와 caveat 합의
3. 본 handoff를 기반으로 정식 survey interim report 초안 작성

## study_overview

- 프로젝트: `{data['project_name']}`
- 범위: `{data['scope']}`
- survey1 역할: 경쟁 앱 benchmark와 gap driver 확인
- survey2 역할: 하나원큐 사용자 경험, 불편, 보강 요구, 유지/이탈 리스크 확인
- survey2 전체 base: `N={data['survey2']['N']}`
- low-base 주의: 연령 {low_base_age} `n={low_base_n}`

## key_findings

### 하나원큐는 benchmark에서 선두와 분명한 차이를 보이지만, 약점은 특정 경험 축에 더 응집되어 있습니다.

- survey1 종합 UX Index 기준 하나원큐는 `{data['survey1']['hana_rank']}위 / {len(benchmark_rows)}개 앱`이며, 선두와 격차는 `{data['survey1']['leader_gap']}점`입니다.
- 가장 큰 gap driver는 **{top_gap['경험 드라이버']}**로, 선두 대비 `{top_gap['1위 대비 격차']}점` 차이입니다.
- 약점은 전면적 붕괴라기보다 혜택/이벤트, 탐색/개인화, 상품/자산 이해 구간에 더 집중되어 있습니다.

### 리뉴얼은 감지되었지만, 다수는 개선보다 '비슷함'으로 받아들였습니다.

- P2B1에서 `비슷함`은 `{fmt_pct_n(similar_row['pct'], similar_row['count']) if similar_row else '-'}`입니다.
- 개선 응답 합계는 `{fmt_pct(improve_pct)}`로, 변화 체감은 존재하지만 압도적이지는 않습니다.
- 정식 보고서에서는 "리뉴얼 자체는 인지되었으나 차별적 선호를 만들 만큼의 개선으로 일반화되지는 않았다" 수준으로 표현하는 것이 안전합니다.

### 혜택/이벤트와 상품·서비스 다양성은 즉시적인 개선 우선순위입니다.

- survey2의 최상위 보강 요구는 **{reinforce_name}**로 `{fmt_pct_n(reinforce_info['pct'], reinforce_info['n'])}`입니다.
- P3B4에서도 {top_p3[0]['option']}와 {top_p3[1]['option']}이 가장 높은 보강 요구를 보입니다.
- 불편 경험 상위 이슈 역시 혜택/이벤트, 안정성, 고객센터/상담 축으로 모입니다.

## competitive_position

| 앱 | 종합 UX Index | 표본 N |
|---|---:|---:|
{benchmark_table}

- 하나원큐는 `{hana_row['overall_index_100']:.1f}점`으로 최하위권이며, {leader_row['app']}(`{leader_row['overall_index_100']:.1f}점`)와의 격차가 가장 큽니다.
- top gap driver 상위 5개:
{top5_gap_bullets}

## satisfaction_recommendation_retention

### 전반 만족은 방어적 수준이지만, 강한 추천 단계까지는 아직 닿지 못했습니다.

- P21B2 전반 만족도: 평균 `{fmt_num(p21b2['mean'])}`, 표준편차 `{fmt_num(p21b2['std'])}`, Top2 `{fmt_pct(p21b2['top2_pct'])}`, Bottom2 `{fmt_pct(p21b2['bottom2_pct'])}`
- survey2 KPI 평균:
  - 전반 만족도 `{fmt_num(data['survey2']['kpi_mean_7pt']['전반 만족도'])}`
  - 지속 사용 의향 `{fmt_num(data['survey2']['kpi_mean_7pt']['지속 사용 의향'])}`
  - 추천 의향 `{fmt_num(data['survey2']['kpi_mean_7pt']['추천 의향'])}`
  - 서비스 충분성 `{fmt_num(data['survey2']['kpi_mean_7pt']['서비스 충분성'])}`

### 사용 축소·중단 리스크는 다수가 강하게 호소하는 수준은 아니지만, 무시할 수 없는 경고 신호가 있습니다.

- P19B4 평균 `{fmt_num(p19b4['mean'])}`, 표준편차 `{fmt_num(p19b4['std'])}`, Top2 `{fmt_pct(p19b4['top2_pct'])}`, Bottom2 `{fmt_pct(p19b4['bottom2_pct'])}`
- 보고서 서술에서는 "즉시 이탈"보다 "불편 누적 시 사용 약화 가능성" 수준으로 두는 편이 안전합니다.

## missing_features_or_pain_points

### 실사용 불편은 혜택/이벤트, 안정성, 상담/문제 해결 축으로 먼저 모입니다.

{top_p18_bullets}

### 부족하거나 보강이 필요하다고 느끼는 기능은 혜택/이벤트, 상품·서비스 다양성, 문제 해결 축이 우선입니다.

{top_p3_bullets}

### 기능별 friction rate는 일부 기능에서 매우 높게 나타납니다.

{top2_friction_bullets}

## driver_or_correlation_takeaways

이 섹션은 이번 라운드에서 **새 상관분석을 수행한 결과가 아니라**, survey1 gap driver와 survey2 question block을 연결한 보고서용 해석 브리지입니다.
정식 보고서에서는 통계적 driver처럼 과장하지 않고, "정량 근거가 한 방향으로 수렴하는 경험 축"으로 표현하는 것이 적절합니다.

{bridge_bullets}

## next_interview_plan

### 다음 인터뷰는 '왜 추천하지 않는지'와 '왜 체감 개선이 크지 않은지'를 실제 사용 맥락에서 해석하는 단계로 설계합니다.

- 혜택/이벤트가 존재하지만 체감 가치로 전환되지 않는 이유
- 고객센터/챗봇/상담에서 문제 해결 흐름이 끊기는 지점
- 홈 탐색과 개인화가 "보여주기"를 넘어 실제 사용 시작점이 되는지
- 상품/서비스 다양성 부족 인식이 정보 구조 문제인지, 실제 상품 경쟁력 인식 문제인지
- 남성 집단에서 상대적으로 높게 보인 사용 축소·중단 리스크의 맥락

추천 recruiting 조건 초안:
- 최근 1개월 내 NEW 하나원큐 반복 사용 경험자
- 타 금융 앱 1개 이상 병행 사용 경험자
- 혜택/이벤트 또는 고객센터/상담 불편 경험자 우선
- 상품 탐색 또는 자산관리 니즈가 뚜렷한 사용자 포함

## appendix_note

- dashboard source: `01_dashboard_data.json`
- insight review view: `03_stakeholder_report.html`
- researcher workbench: `02_researcher_workbench.html`
- interactive workbench: `07_interactive_research_workbench.html`

## assumptions_and_caveats

- 본 문서는 정식 interim report가 아니라 report-writer 입력용 handoff 초안입니다.
- 연령 60대 `n=7`은 low base로 간주해 세부 연령 비교를 본문 주장에 사용하지 않습니다.
- 성별 차이와 cross-survey bridge는 descriptive 해석이며, 유의성 검정이나 인과 판단을 의미하지 않습니다.
- production 단계에서는 본 handoff를 사람이 검토한 뒤 `survey-interim-report-writer`의 section order와 문체 규칙에 맞춰 문서형 초안으로 전개해야 합니다.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the stakeholder insight-review HTML (03, overwritten) and the "
            "report-writer handoff markdown (09) from an existing 01_dashboard_data.json."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"path to 01_dashboard_data.json (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--stakeholder-html",
        type=Path,
        default=DEFAULT_STAKEHOLDER_PATH,
        help=(
            "output path for the stakeholder insight-review HTML — this "
            f"overwrites the plainer 03_stakeholder_report.html from "
            f"build_full_dashboard.py by design (default: {DEFAULT_STAKEHOLDER_PATH})"
        ),
    )
    parser.add_argument(
        "--out-handoff",
        type=Path,
        default=DEFAULT_HANDOFF_PATH,
        help=f"output path for the report-writer handoff markdown (default: {DEFAULT_HANDOFF_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = read_data(args.data)
    args.stakeholder_html.parent.mkdir(parents=True, exist_ok=True)
    args.stakeholder_html.write_text(render_stakeholder_html(data), encoding="utf-8")
    args.out_handoff.parent.mkdir(parents=True, exist_ok=True)
    out_dir_label = args.out_handoff.resolve().parent.name
    args.out_handoff.write_text(
        render_handoff_markdown(data, out_dir_label), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
