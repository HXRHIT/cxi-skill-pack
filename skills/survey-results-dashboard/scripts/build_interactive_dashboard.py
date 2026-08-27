from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT / "01_dashboard_data.json"
DEFAULT_OUT_HTML = ROOT / "07_interactive_research_workbench.html"
DEFAULT_OUT_NOTE = ROOT / "08_interactive_notes.md"
TODAY_ISO = date.today().isoformat()


HTML_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UXQ Interactive Researcher Workbench</title>
  <style>
    :root {
      --navy: #003087;
      --red: #E8003D;
      --ink: #15202B;
      --slate: #5D6975;
      --mist: #D9E1EA;
      --panel: rgba(255,255,255,.94);
      --sky: #EDF4FF;
      --rose: #FFF1F4;
      --mint: #EEF9F3;
      --amber: #FFF7E8;
      --bg:
        radial-gradient(circle at 0% 0%, rgba(232,0,61,.07), transparent 26%),
        radial-gradient(circle at 100% 0%, rgba(0,48,135,.08), transparent 24%),
        linear-gradient(180deg, #F6F8FC 0%, #FFFDFC 100%);
      --shadow: 0 22px 44px rgba(0, 48, 135, .08);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: "Aptos", "Malgun Gothic", "Segoe UI", sans-serif;
      line-height: 1.56;
    }
    button, input, select {
      font: inherit;
    }
    a {
      color: var(--navy);
      text-decoration: none;
    }
    .page {
      max-width: 1580px;
      margin: 0 auto;
      padding: 24px 18px 72px;
    }
    .hero {
      position: relative;
      overflow: hidden;
      padding: 28px;
      border-radius: 30px;
      background:
        linear-gradient(135deg, rgba(0,48,135,.98), rgba(12,65,159,.92)),
        linear-gradient(180deg, #003087, #1040A0);
      color: white;
      box-shadow: var(--shadow);
    }
    .hero::after {
      content: "";
      position: absolute;
      right: -40px;
      bottom: -60px;
      width: 240px;
      height: 240px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
    }
    .eyebrow {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.12);
      font-size: 12px;
      letter-spacing: .05em;
      text-transform: uppercase;
      font-weight: 800;
    }
    h1 {
      margin: 12px 0 10px;
      font-size: 36px;
      line-height: 1.14;
    }
    .hero p {
      margin: 0;
      max-width: 1020px;
      color: rgba(255,255,255,.92);
    }
    .hero-meta {
      margin-top: 12px;
      font-size: 13px;
      color: rgba(255,255,255,.78);
    }
    .toolbar {
      position: sticky;
      top: 0;
      z-index: 20;
      margin-top: 20px;
      padding: 14px;
      border-radius: 24px;
      border: 1px solid var(--mist);
      background: rgba(250,252,255,.88);
      backdrop-filter: blur(18px);
      box-shadow: 0 12px 26px rgba(21, 32, 43, .06);
    }
    .toolbar-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: minmax(180px, 1.8fr) repeat(4, minmax(150px, .95fr)) minmax(160px, 1.2fr);
      align-items: end;
    }
    .field label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .04em;
      text-transform: uppercase;
      color: var(--slate);
    }
    .field input,
    .field select {
      width: 100%;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid var(--mist);
      background: white;
      color: var(--ink);
    }
    .range-row {
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .range-row output {
      min-width: 38px;
      text-align: right;
      font-weight: 800;
      color: var(--navy);
    }
    .theme-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }
    .pill-btn {
      border: 1px solid var(--mist);
      background: white;
      color: var(--slate);
      border-radius: 999px;
      padding: 7px 12px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 700;
    }
    .pill-btn.active {
      border-color: rgba(0,48,135,.35);
      background: var(--sky);
      color: var(--navy);
    }
    .workspace {
      margin-top: 18px;
      display: grid;
      gap: 18px;
      grid-template-columns: 360px 1fr;
    }
    .stack {
      display: grid;
      gap: 18px;
    }
    .panel {
      border: 1px solid var(--mist);
      border-radius: 26px;
      background: var(--panel);
      box-shadow: 0 14px 28px rgba(21, 32, 43, .05);
      overflow: hidden;
    }
    .panel-head {
      padding: 18px 18px 0;
    }
    .panel-body {
      padding: 18px;
    }
    h2 {
      margin: 0;
      color: var(--navy);
      font-size: 24px;
    }
    h3 {
      margin: 0 0 10px;
      color: var(--ink);
      font-size: 18px;
    }
    .subtle {
      color: var(--slate);
      font-size: 14px;
      margin-top: 8px;
    }
    .cards {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 14px;
    }
    .metric-card {
      padding: 14px;
      border-radius: 18px;
      border: 1px solid var(--mist);
      background: white;
    }
    .metric-card.sky { background: linear-gradient(180deg, var(--sky), white 84%); }
    .metric-card.rose { background: linear-gradient(180deg, var(--rose), white 84%); }
    .metric-card.mint { background: linear-gradient(180deg, var(--mint), white 84%); }
    .metric-card.amber { background: linear-gradient(180deg, var(--amber), white 84%); }
    .metric-label {
      color: var(--slate);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    .metric-value {
      margin-top: 6px;
      font-size: 28px;
      line-height: 1.04;
      color: var(--navy);
      font-weight: 900;
    }
    .metric-detail {
      margin-top: 6px;
      font-size: 13px;
      color: var(--slate);
    }
    .app-rank-list,
    .flag-list,
    .bridge-list,
    .source-list,
    .navigator-list {
      display: grid;
      gap: 10px;
    }
    .rank-row,
    .flag-card,
    .bridge-card,
    .source-link,
    .nav-item {
      border: 1px solid var(--mist);
      border-radius: 18px;
      background: white;
      padding: 12px 14px;
    }
    .rank-row.highlight {
      background: var(--sky);
      border-color: rgba(0,48,135,.28);
    }
    .rank-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-weight: 800;
    }
    .bar {
      margin-top: 8px;
      height: 10px;
      border-radius: 999px;
      overflow: hidden;
      background: #EDF1F7;
    }
    .bar > span {
      display: block;
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #0D4BB8, #2C7BE5);
    }
    .bar.red > span {
      background: linear-gradient(90deg, #C2164C, var(--red));
    }
    .bar.gold > span {
      background: linear-gradient(90deg, #BA8414, #F0BA41);
    }
    .flag-card.ok { background: linear-gradient(180deg, var(--mint), white 80%); }
    .flag-card.warn { background: linear-gradient(180deg, var(--amber), white 80%); }
    .flag-card.info { background: linear-gradient(180deg, var(--sky), white 80%); }
    .badge {
      display: inline-block;
      margin-bottom: 8px;
      padding: 5px 8px;
      border-radius: 999px;
      background: rgba(0,48,135,.08);
      color: var(--navy);
      font-size: 12px;
      font-weight: 900;
    }
    .bridge-card {
      cursor: pointer;
      transition: transform .12s ease, box-shadow .12s ease;
      background: linear-gradient(180deg, white, #FBF6EE);
    }
    .bridge-card:hover,
    .nav-item:hover {
      transform: translateY(-1px);
      box-shadow: 0 12px 22px rgba(21, 32, 43, .07);
    }
    .bridge-card.active {
      border-color: rgba(0,48,135,.34);
      background: linear-gradient(180deg, var(--sky), white 86%);
    }
    .board {
      display: grid;
      gap: 18px;
      grid-template-columns: 320px minmax(0, 1fr);
      align-items: start;
    }
    .nav-item {
      cursor: pointer;
      transition: transform .12s ease, box-shadow .12s ease;
    }
    .nav-item.active {
      border-color: rgba(0,48,135,.34);
      background: linear-gradient(180deg, var(--sky), white 84%);
    }
    .nav-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
    }
    .nav-code {
      color: var(--red);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .04em;
    }
    .tag-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }
    .tag {
      border-radius: 999px;
      padding: 4px 8px;
      background: #F2F5FA;
      color: var(--slate);
      font-size: 12px;
      font-weight: 700;
    }
    .detail-shell {
      padding: 22px;
    }
    .detail-head {
      display: flex;
      flex-wrap: wrap;
      gap: 10px 12px;
      align-items: center;
      margin-bottom: 14px;
    }
    .detail-code {
      color: var(--red);
      font-size: 13px;
      font-weight: 900;
      letter-spacing: .04em;
    }
    .detail-type {
      color: var(--navy);
      background: var(--sky);
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 800;
    }
    .detail-theme {
      color: #7A5300;
      background: var(--amber);
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 800;
    }
    .mini-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      margin: 16px 0 20px;
    }
    .mini-card {
      border: 1px solid var(--mist);
      border-radius: 16px;
      padding: 12px;
      background: #FCFDFF;
    }
    .mini-card .label {
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--slate);
      letter-spacing: .04em;
    }
    .mini-card .value {
      margin-top: 6px;
      font-size: 24px;
      color: var(--navy);
      font-weight: 900;
    }
    .mini-card .hint {
      margin-top: 4px;
      color: var(--slate);
      font-size: 12px;
    }
    .detail-grid {
      display: grid;
      gap: 18px;
      grid-template-columns: 1.05fr .95fr;
    }
    .section-card {
      border: 1px solid var(--mist);
      border-radius: 20px;
      background: white;
      padding: 16px;
    }
    .section-card h4 {
      margin: 0 0 10px;
      font-size: 16px;
      color: var(--ink);
    }
    .table-wrap {
      overflow: auto;
      border-radius: 14px;
      border: 1px solid var(--mist);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      padding: 9px 10px;
      text-align: left;
      border-bottom: 1px solid var(--mist);
      vertical-align: top;
    }
    th {
      position: sticky;
      top: 0;
      background: #EEF3FA;
      color: var(--navy);
      font-weight: 900;
      z-index: 1;
    }
    tr:last-child td { border-bottom: none; }
    .distribution-list {
      display: grid;
      gap: 10px;
    }
    .distribution-row {
      display: grid;
      gap: 10px;
      grid-template-columns: minmax(110px, 220px) 1fr 92px;
      align-items: center;
      font-size: 14px;
    }
    .distribution-value {
      text-align: right;
      font-weight: 800;
    }
    .segment-toggle {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }
    .segment-btn {
      border: 1px solid var(--mist);
      background: white;
      border-radius: 999px;
      padding: 6px 11px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 700;
      color: var(--slate);
    }
    .segment-btn.active {
      background: var(--sky);
      color: var(--navy);
      border-color: rgba(0,48,135,.34);
    }
    .layer {
      margin-top: 12px;
      border-radius: 18px;
      border: 1px solid var(--mist);
      background: white;
      padding: 13px 14px;
    }
    .layer-title {
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .04em;
      text-transform: uppercase;
      color: var(--slate);
    }
    .empty-state {
      padding: 38px 20px;
      text-align: center;
      color: var(--slate);
    }
    .footer {
      margin-top: 20px;
      color: var(--slate);
      font-size: 13px;
    }
    @media (max-width: 1260px) {
      .toolbar-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .workspace {
        grid-template-columns: 1fr;
      }
    }
    @media (max-width: 980px) {
      .board,
      .detail-grid {
        grid-template-columns: 1fr;
      }
      .toolbar {
        position: static;
      }
    }
    @media (max-width: 740px) {
      .cards {
        grid-template-columns: 1fr 1fr;
      }
      .distribution-row {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="eyebrow">Interactive Researcher Workbench</div>
      <h1>UXQ Full Survey Dashboard — Interactive Explorer</h1>
      <p>survey1 benchmark와 survey2 deep dive를 한 화면에서 탐색할 수 있도록 만든 researcher용 인터랙티브 버전입니다. 검색, 타입 필터, 테마 필터, benchmark top-N 조절, 질문 drill-down을 모두 지원합니다.</p>
      <div class="hero-meta">Updated on __UPDATED__</div>
    </section>

    <section class="toolbar">
      <div class="toolbar-grid">
        <div class="field">
          <label for="searchInput">Question Search</label>
          <input id="searchInput" type="search" placeholder="코드, 제목, 질문문으로 검색">
        </div>
        <div class="field">
          <label for="typeSelect">Question Type</label>
          <select id="typeSelect">
            <option value="all">전체</option>
            <option value="single-choice">single-choice</option>
            <option value="scale">scale</option>
            <option value="priority">priority / ranking</option>
          </select>
        </div>
        <div class="field">
          <label for="themeSelect">Theme</label>
          <select id="themeSelect">
            <option value="all">전체</option>
            <option value="transition">전환 체감</option>
            <option value="kpi">만족 / KPI</option>
            <option value="risk">리스크 / 해결</option>
            <option value="friction">실사용 마찰</option>
            <option value="reinforcement">보강 우선순위</option>
          </select>
        </div>
        <div class="field">
          <label for="sortSelect">Sort</label>
          <select id="sortSelect">
            <option value="default">기본 순서</option>
            <option value="title">제목 가나다</option>
            <option value="base-desc">Base N 높은 순</option>
            <option value="code">코드순</option>
          </select>
        </div>
        <div class="field">
          <label for="segmentSelect">Segment Lens</label>
          <select id="segmentSelect">
            <option value="all">전체 + 성별 비교</option>
            <option value="여성">여성 focus</option>
            <option value="남성">남성 focus</option>
          </select>
        </div>
        <div class="field">
          <label for="topNRange">Benchmark Top-N</label>
          <div class="range-row">
            <input id="topNRange" type="range" min="3" max="10" value="5">
            <output id="topNOutput">5</output>
          </div>
        </div>
      </div>
      <div class="theme-pills" id="bridgePills"></div>
    </section>

    <div class="workspace">
      <aside class="stack">
        <section class="panel">
          <div class="panel-head">
            <h2>Snapshot</h2>
            <div class="subtle">필터 결과에 따라 matching block 수와 현재 focus를 바로 보여줍니다.</div>
          </div>
          <div class="panel-body">
            <div class="cards" id="summaryCards"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <h2>Survey1 Benchmark</h2>
            <div class="subtle">하나원큐 위치와 top gap driver를 함께 봅니다.</div>
          </div>
          <div class="panel-body">
            <div class="app-rank-list" id="appRanking"></div>
            <div style="height:16px"></div>
            <h3 style="margin-bottom:8px">Gap Drivers</h3>
            <div class="app-rank-list" id="gapDriverList"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <h2>Cross-survey Bridges</h2>
            <div class="subtle">클릭하면 해당 theme로 바로 필터링됩니다.</div>
          </div>
          <div class="panel-body">
            <div class="bridge-list" id="bridgeList"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <h2>QA Flags</h2>
            <div class="subtle">guardrail은 항상 보이도록 researcher sidebar에 고정했습니다.</div>
          </div>
          <div class="panel-body">
            <div class="flag-list" id="flagList"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <h2>Source Links</h2>
          </div>
          <div class="panel-body">
            <div class="source-list" id="sourceList"></div>
          </div>
        </section>
      </aside>

      <section class="board">
        <section class="panel">
          <div class="panel-head">
            <h2>Question Navigator</h2>
            <div class="subtle" id="navigatorMeta"></div>
          </div>
          <div class="panel-body">
            <div class="navigator-list" id="navigatorList"></div>
          </div>
        </section>

        <section class="panel">
          <div class="detail-shell" id="detailPanel"></div>
        </section>
      </section>
    </div>
  </div>

  <script>
    const DASHBOARD_DATA = __DATA__;

    const THEME_LABELS = {
      all: "전체",
      transition: "전환 체감",
      kpi: "만족 / KPI",
      risk: "리스크 / 해결",
      friction: "실사용 마찰",
      reinforcement: "보강 우선순위"
    };

    const TYPE_LABELS = {
      "single-choice": "single-choice",
      scale: "scale",
      priority: "priority / ranking"
    };

    const QUESTION_THEME_MAP = {
      P2B1: "transition",
      P21B2: "kpi",
      P19B3: "risk",
      P19B4: "risk",
      P18B1: "friction",
      P3B4: "reinforcement"
    };

    const DRIVER_THEME_MAP = {
      "이벤트": "reinforcement",
      "홈화면 탐색 구성": "transition",
      "홈 화면 개인화": "transition",
      "쉬운 사용성": "kpi",
      "자산/거래 현황": "friction",
      "계좌/금융정보 연동": "friction",
      "정보 다양성": "reinforcement",
      "상품 다양성": "reinforcement",
      "정보 가독성": "transition",
      "최신 정보": "reinforcement",
      "자주 쓰는 기능/정보 관리": "transition",
      "이해 용이성": "reinforcement"
    };

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function fmtPct(value) {
      if (value === null || value === undefined || value === "") return "-";
      return `${Number(value).toFixed(1)}%`;
    }

    function fmtNum(value, digits = 2) {
      if (value === null || value === undefined || value === "") return "-";
      return Number(value).toFixed(digits);
    }

    function inferType(block) {
      if (block.score_rows) return "scale";
      if ((block.overall_rows || []).some((row) => Object.prototype.hasOwnProperty.call(row, "weighted_score"))) {
        return "priority";
      }
      return "single-choice";
    }

    function sortedOverallRows(block) {
      const rows = [...(block.overall_rows || [])];
      if (!rows.length) return rows;
      if (Object.prototype.hasOwnProperty.call(rows[0], "weighted_score")) {
        return rows.sort((a, b) => (b.weighted_score - a.weighted_score) || (b.respondent_count - a.respondent_count));
      }
      return rows.sort((a, b) => (b.count - a.count) || (b.pct - a.pct));
    }

    const enrichedBlocks = DASHBOARD_DATA.question_blocks.map((block, index) => ({
      ...block,
      order: index,
      blockType: inferType(block),
      theme: QUESTION_THEME_MAP[block.code] || "all",
      searchText: [block.code, block.title, block.question_text].join(" ").toLowerCase()
    }));

    const state = {
      search: "",
      type: "all",
      theme: "all",
      sort: "default",
      segment: "all",
      topN: 5,
      selectedCode: enrichedBlocks[0]?.code || null
    };

    const $ = (id) => document.getElementById(id);

    function filterBlocks() {
      let blocks = [...enrichedBlocks];
      if (state.search) {
        blocks = blocks.filter((block) => block.searchText.includes(state.search));
      }
      if (state.type !== "all") {
        blocks = blocks.filter((block) => block.blockType === state.type);
      }
      if (state.theme !== "all") {
        blocks = blocks.filter((block) => block.theme === state.theme);
      }

      if (state.sort === "title") {
        blocks.sort((a, b) => a.title.localeCompare(b.title, "ko"));
      } else if (state.sort === "base-desc") {
        blocks.sort((a, b) => b.base_n - a.base_n);
      } else if (state.sort === "code") {
        blocks.sort((a, b) => a.code.localeCompare(b.code, "en"));
      } else {
        blocks.sort((a, b) => a.order - b.order);
      }
      return blocks;
    }

    function ensureSelected(filteredBlocks) {
      if (!filteredBlocks.length) {
        state.selectedCode = null;
        return;
      }
      if (!filteredBlocks.some((block) => block.code === state.selectedCode)) {
        state.selectedCode = filteredBlocks[0].code;
      }
    }

    function renderSummary(filteredBlocks) {
      const selected = filteredBlocks.find((block) => block.code === state.selectedCode) || null;
      const topGap = DASHBOARD_DATA.survey1.gap_drivers[0];
      const cards = [
        {
          label: "Matching Blocks",
          value: filteredBlocks.length,
          detail: "현재 필터 결과",
          tone: "sky"
        },
        {
          label: "Selected",
          value: selected ? selected.code : "-",
          detail: selected ? selected.title : "선택된 질문 없음",
          tone: "mint"
        },
        {
          label: "Benchmark Rank",
          value: `${DASHBOARD_DATA.survey1.hana_rank} / ${DASHBOARD_DATA.survey1.app_overall.length}`,
          detail: "하나원큐 종합 UX Index",
          tone: "rose"
        },
        {
          label: "Top Gap",
          value: topGap ? topGap["1위 대비 격차"] : "-",
          detail: topGap ? topGap["경험 드라이버"] : "gap driver 없음",
          tone: "amber"
        }
      ];

      $("summaryCards").innerHTML = cards.map((card) => `
        <div class="metric-card ${card.tone}">
          <div class="metric-label">${escapeHtml(card.label)}</div>
          <div class="metric-value">${escapeHtml(card.value)}</div>
          <div class="metric-detail">${escapeHtml(card.detail)}</div>
        </div>
      `).join("");
    }

    function renderBridgePills() {
      const pills = [
        { value: "all", label: "전체 보기" },
        ...DASHBOARD_DATA.bridges.map((bridge) => ({
          value: Object.keys(THEME_LABELS).find((key) => THEME_LABELS[key].startsWith(bridge.theme.split("·")[0])) || QUESTION_THEME_MAP.P2B1,
          label: bridge.theme
        }))
      ];

      $("bridgePills").innerHTML = pills.map((pill, index) => `
        <button class="pill-btn ${state.theme === pill.value || (index > 0 && DASHBOARD_DATA.bridges[index - 1].theme === pill.label && state.theme !== "all" && THEME_LABELS[state.theme] === THEME_LABELS[pill.value]) ? "active" : ""}" data-pill="${escapeHtml(pill.value)}">
          ${escapeHtml(pill.label)}
        </button>
      `).join("");

      [...document.querySelectorAll("[data-pill]")].forEach((button) => {
        button.addEventListener("click", () => {
          state.theme = button.dataset.pill || "all";
          $("themeSelect").value = state.theme;
          render();
        });
      });
    }

    function renderAppRanking() {
      const rows = [...DASHBOARD_DATA.survey1.app_overall];
      const maxValue = Math.max(...rows.map((row) => Number(row.overall_index_100)));
      $("appRanking").innerHTML = rows.map((row, index) => {
        const width = (Number(row.overall_index_100) / maxValue) * 100;
        const highlight = row.app === "하나원큐" ? "highlight" : "";
        return `
          <div class="rank-row ${highlight}">
            <div class="rank-top">
              <span>${index + 1}. ${escapeHtml(row.app)}</span>
              <span>${escapeHtml(fmtNum(row.overall_index_100, 1))}</span>
            </div>
            <div class="subtle">표본 N ${escapeHtml(row.n)}</div>
            <div class="bar"><span style="width:${width.toFixed(1)}%"></span></div>
          </div>
        `;
      }).join("");
    }

    function renderGapDrivers() {
      let drivers = [...DASHBOARD_DATA.survey1.gap_drivers];
      if (state.theme !== "all") {
        drivers = drivers.filter((row) => (DRIVER_THEME_MAP[row["경험 드라이버"]] || "all") === state.theme);
      }
      if (!drivers.length) {
        drivers = [...DASHBOARD_DATA.survey1.gap_drivers];
      }
      drivers = drivers.slice(0, state.topN);
      const maxGap = Math.max(...drivers.map((row) => Math.abs(Number(row["1위 대비 격차"])))) || 1;
      $("gapDriverList").innerHTML = drivers.map((row) => {
        const width = (Math.abs(Number(row["1위 대비 격차"])) / maxGap) * 100;
        return `
          <div class="rank-row">
            <div class="rank-top">
              <span>${escapeHtml(row["경험 드라이버"])}</span>
              <span>${escapeHtml(row["1위 대비 격차"])}</span>
            </div>
            <div class="subtle">${escapeHtml(row["1위 앱"])} 기준 · 원큐 ${escapeHtml(row["하나원큐"])}점 · ${escapeHtml(row["하나원큐 순위"])}</div>
            <div class="bar red"><span style="width:${width.toFixed(1)}%"></span></div>
          </div>
        `;
      }).join("");
    }

    function renderBridges() {
      $("bridgeList").innerHTML = DASHBOARD_DATA.bridges.map((bridge) => {
        const themeKey = Object.entries(THEME_LABELS).find(([, label]) => bridge.theme.includes(label.split(" ")[0]))?.[0] || "all";
        const active = state.theme !== "all" && themeKey === state.theme;
        return `
          <div class="bridge-card ${active ? "active" : ""}" data-bridge-theme="${escapeHtml(themeKey)}">
            <h3>${escapeHtml(bridge.theme)}</h3>
            <div class="subtle"><b>Survey1</b> ${escapeHtml(bridge.survey1)}</div>
            <div class="subtle"><b>Survey2</b> ${escapeHtml(bridge.survey2)}</div>
            <div style="margin-top:8px">${escapeHtml(bridge.implication)}</div>
          </div>
        `;
      }).join("");

      [...document.querySelectorAll("[data-bridge-theme]")].forEach((card) => {
        card.addEventListener("click", () => {
          state.theme = card.dataset.bridgeTheme || "all";
          $("themeSelect").value = state.theme;
          render();
        });
      });
    }

    function renderFlags() {
      $("flagList").innerHTML = DASHBOARD_DATA.qa_flags.map((flag) => `
        <div class="flag-card ${escapeHtml(flag.level)}">
          <div class="badge">${escapeHtml(flag.badge)}</div>
          <h3>${escapeHtml(flag.title)}</h3>
          <div class="subtle">${escapeHtml(flag.detail)}</div>
        </div>
      `).join("");
    }

    function renderSources() {
      const sources = [
        { label: "Round 2 portal", href: "00_dashboard_portal.html", detail: "현재 폴더 포털" },
        { label: "Researcher Workbench (static)", href: "02_researcher_workbench.html", detail: "정적 researcher version" },
        { label: "Stakeholder Report", href: "03_stakeholder_report.html", detail: "경량 공유용 뷰" },
        { label: "Reference report", href: DASHBOARD_DATA.sources.reference_report, detail: "실사례 published HTML" }
      ];
      $("sourceList").innerHTML = sources.map((source) => `
        <a class="source-link" href="${escapeHtml(source.href)}">
          <div class="rank-top">
            <span>${escapeHtml(source.label)}</span>
            <span>Open</span>
          </div>
          <div class="subtle">${escapeHtml(source.detail)}</div>
        </a>
      `).join("");
    }

    function renderNavigator(filteredBlocks) {
      $("navigatorMeta").textContent = `${filteredBlocks.length}개 block이 현재 필터와 일치합니다.`;
      if (!filteredBlocks.length) {
        $("navigatorList").innerHTML = `<div class="empty-state">현재 필터 조건과 일치하는 질문이 없습니다.</div>`;
        return;
      }

      $("navigatorList").innerHTML = filteredBlocks.map((block) => {
        const active = block.code === state.selectedCode;
        return `
          <div class="nav-item ${active ? "active" : ""}" data-code="${escapeHtml(block.code)}">
            <div class="nav-top">
              <div>
                <div class="nav-code">${escapeHtml(block.code)}</div>
                <div><b>${escapeHtml(block.title)}</b></div>
              </div>
              <div style="text-align:right">
                <div><b>n=${escapeHtml(block.base_n)}</b></div>
              </div>
            </div>
            <div class="subtle">${escapeHtml(block.question_text)}</div>
            <div class="tag-row">
              <span class="tag">${escapeHtml(TYPE_LABELS[block.blockType])}</span>
              <span class="tag">${escapeHtml(THEME_LABELS[block.theme] || block.theme)}</span>
            </div>
          </div>
        `;
      }).join("");

      [...document.querySelectorAll("[data-code]")].forEach((item) => {
        item.addEventListener("click", () => {
          state.selectedCode = item.dataset.code || null;
          render();
        });
      });
    }

    function metricCard(label, value, hint) {
      return `
        <div class="mini-card">
          <div class="label">${escapeHtml(label)}</div>
          <div class="value">${escapeHtml(value)}</div>
          <div class="hint">${escapeHtml(hint)}</div>
        </div>
      `;
    }

    function renderDistributionRows(rows, type) {
      if (!rows.length) {
        return `<div class="empty-state">표시할 분포 데이터가 없습니다.</div>`;
      }

      let max = 1;
      let mapped = [];
      if (type === "scale") {
        mapped = rows.map((row) => ({
          label: `${row.score}점`,
          pct: Number(row.pct),
          note: `N=${row.count}`
        }));
        max = Math.max(...mapped.map((row) => row.pct));
      } else if (type === "single-choice") {
        mapped = rows.map((row) => ({
          label: row.label,
          pct: Number(row.pct),
          note: `N=${row.count}`
        }));
        max = Math.max(...mapped.map((row) => row.pct));
      } else {
        mapped = rows.map((row) => ({
          label: row.option,
          pct: Number(row.respondent_pct),
          note: `N=${row.respondent_count} · W=${row.weighted_score}`
        }));
        max = Math.max(...mapped.map((row) => row.pct));
      }

      return `<div class="distribution-list">` + mapped.map((row) => {
        const width = max ? (row.pct / max) * 100 : 0;
        const fillClass = type === "priority" ? "gold" : "";
        return `
          <div class="distribution-row">
            <div>${escapeHtml(row.label)}</div>
            <div class="bar ${fillClass}"><span style="width:${width.toFixed(1)}%"></span></div>
            <div class="distribution-value">${escapeHtml(fmtPct(row.pct))}<div class="subtle">${escapeHtml(row.note)}</div></div>
          </div>
        `;
      }).join("") + `</div>`;
    }

    function renderScaleSegments(block) {
      const rows = block.segment_rows || [];
      const table = `
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>세그먼트</th>
                <th>Base N</th>
                <th>평균</th>
                <th>Top2</th>
                <th>Bottom2</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map((row) => `
                <tr>
                  <td>${escapeHtml(row.segment)}</td>
                  <td>${escapeHtml(row.base_n)}</td>
                  <td>${escapeHtml(fmtNum(row.mean, 2))}</td>
                  <td>${escapeHtml(fmtPct(row.top2_pct))}</td>
                  <td>${escapeHtml(fmtPct(row.bottom2_pct))}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
      return table;
    }

    function renderChoiceSegments(block) {
      if (Array.isArray(block.segment_rows)) {
        return `
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>세그먼트</th>
                  <th>Base N</th>
                  <th>상위 응답</th>
                </tr>
              </thead>
              <tbody>
                ${block.segment_rows.map((row) => `
                  <tr>
                    <td>${escapeHtml(row.segment)}</td>
                    <td>${escapeHtml(row.base_n)}</td>
                    <td>${escapeHtml((row.top_options || []).map((item) => `${item.label}(${fmtPct(item.pct)}, N=${item.count})`).join(", "))}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        `;
      }

      const chosenSegment = state.segment === "all"
        ? null
        : block.segment_rows?.[state.segment] || null;

      if (chosenSegment) {
        return renderDistributionRows(chosenSegment, "priority");
      }

      return `
        <div class="cards">
          ${Object.entries(block.segment_rows || {}).map(([segment, rows]) => `
            <div class="metric-card sky">
              <div class="metric-label">${escapeHtml(segment)}</div>
              <div class="metric-detail">${escapeHtml(`Base N ${DASHBOARD_DATA.overview.gender_counts[segment] || "-"}`)}</div>
              <div style="margin-top:10px">${renderDistributionRows(rows.slice(0, 5), "priority")}</div>
            </div>
          `).join("")}
        </div>
      `;
    }

    function renderDetail(block) {
      if (!block) {
        $("detailPanel").innerHTML = `<div class="empty-state">왼쪽에서 질문 블록을 선택해 주세요.</div>`;
        return;
      }

      const overallRows = sortedOverallRows(block);
      const metrics = [metricCard("Base N", block.base_n, "응답 기준")];
      if (block.blockType === "scale") {
        metrics.push(metricCard("Mean", fmtNum(block.mean, 2), "평균"));
        metrics.push(metricCard("SD", fmtNum(block.std, 2), "표준편차"));
        metrics.push(metricCard("Top2", fmtPct(block.top2_pct), "6~7점"));
        metrics.push(metricCard("Bottom2", fmtPct(block.bottom2_pct), "1~2점"));
      } else if (block.blockType === "priority") {
        const topItem = overallRows[0];
        metrics.push(metricCard("Top Option", topItem ? topItem.option : "-", "가중 점수 기준"));
        metrics.push(metricCard("Top Share", topItem ? fmtPct(topItem.respondent_pct) : "-", "응답자 기준"));
      } else {
        const topItem = overallRows[0];
        metrics.push(metricCard("Top Answer", topItem ? topItem.label : "-", "전체 응답 최다"));
        metrics.push(metricCard("Top Share", topItem ? fmtPct(topItem.pct) : "-", "응답률"));
      }

      const segmentButtons = block.blockType === "scale"
        ? ""
        : `
          <div class="segment-toggle">
            <button class="segment-btn ${state.segment === "all" ? "active" : ""}" data-segment="all">전체</button>
            <button class="segment-btn ${state.segment === "여성" ? "active" : ""}" data-segment="여성">여성 focus</button>
            <button class="segment-btn ${state.segment === "남성" ? "active" : ""}" data-segment="남성">남성 focus</button>
          </div>
        `;

      $("detailPanel").innerHTML = `
        <div class="detail-head">
          <div class="detail-code">${escapeHtml(block.code)}</div>
          <div class="detail-type">${escapeHtml(TYPE_LABELS[block.blockType])}</div>
          <div class="detail-theme">${escapeHtml(THEME_LABELS[block.theme] || block.theme)}</div>
        </div>
        <h2>${escapeHtml(block.title)}</h2>
        <div class="subtle" style="margin-top:10px">${escapeHtml(block.question_text)}</div>

        <div class="mini-grid">${metrics.join("")}</div>

        <div class="detail-grid">
          <section class="section-card">
            <h4>전체 분포</h4>
            ${renderDistributionRows(
              block.blockType === "scale" ? block.score_rows : overallRows,
              block.blockType
            )}
          </section>
          <section class="section-card">
            <h4>세그먼트 비교</h4>
            ${segmentButtons}
            ${block.blockType === "scale" ? renderScaleSegments(block) : renderChoiceSegments(block)}
          </section>
        </div>

        <div class="layer">
          <div class="layer-title">[Data]</div>
          <div>${escapeHtml(block.data_note)}</div>
        </div>
        <div class="layer">
          <div class="layer-title">[AI Interpretation]</div>
          <div>${escapeHtml(block.ai_interpretation)}</div>
        </div>
        <div class="layer">
          <div class="layer-title">[Needs Judgment]</div>
          <div>${escapeHtml(block.needs_judgment)}</div>
        </div>

        <div class="footer">
          Scope reminder: 이 explorer는 survey-only researcher workbench입니다. low-base(연령 60대 n=7)와 descriptive-only 해석 경계는 그대로 유지합니다.
        </div>
      `;

      [...document.querySelectorAll("[data-segment]")].forEach((button) => {
        button.addEventListener("click", () => {
          state.segment = button.dataset.segment || "all";
          renderDetail(block);
        });
      });
    }

    function render() {
      const filteredBlocks = filterBlocks();
      ensureSelected(filteredBlocks);
      renderSummary(filteredBlocks);
      renderBridgePills();
      renderAppRanking();
      renderGapDrivers();
      renderBridges();
      renderFlags();
      renderSources();
      renderNavigator(filteredBlocks);
      renderDetail(filteredBlocks.find((block) => block.code === state.selectedCode) || null);
    }

    function wireControls() {
      $("searchInput").addEventListener("input", (event) => {
        state.search = event.target.value.trim().toLowerCase();
        render();
      });
      $("typeSelect").addEventListener("change", (event) => {
        state.type = event.target.value;
        render();
      });
      $("themeSelect").addEventListener("change", (event) => {
        state.theme = event.target.value;
        render();
      });
      $("sortSelect").addEventListener("change", (event) => {
        state.sort = event.target.value;
        render();
      });
      $("segmentSelect").addEventListener("change", (event) => {
        state.segment = event.target.value;
        render();
      });
      $("topNRange").addEventListener("input", (event) => {
        state.topN = Number(event.target.value);
        $("topNOutput").value = String(state.topN);
        renderGapDrivers();
      });
    }

    wireControls();
    $("topNOutput").value = String(state.topN);
    render();
  </script>
</body>
</html>
"""


NOTE_TEXT_TEMPLATE = """# Interactive Dashboard Note

Created on {today}

## Output

- `07_interactive_research_workbench.html`

## What This Version Adds

- question search
- question type filter
- theme filter
- benchmark top-N slider
- clickable cross-survey bridge cards
- left-side navigator + right-side drill-down detail
- researcher-safe guardrails kept visible

## Scope

- survey1 benchmark + survey2 validated pack
- local static interactive HTML
- no server dependency
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the interactive researcher workbench (07/08) from an "
            "existing 01_dashboard_data.json produced by build_full_dashboard.py."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"path to 01_dashboard_data.json (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--out-html",
        type=Path,
        default=DEFAULT_OUT_HTML,
        help=f"output path for the interactive HTML (default: {DEFAULT_OUT_HTML})",
    )
    parser.add_argument(
        "--out-note",
        type=Path,
        default=DEFAULT_OUT_NOTE,
        help=f"output path for the notes markdown (default: {DEFAULT_OUT_NOTE})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA__", data_json).replace(
        "__UPDATED__", TODAY_ISO
    )
    args.out_html.parent.mkdir(parents=True, exist_ok=True)
    args.out_html.write_text(html, encoding="utf-8")
    args.out_note.parent.mkdir(parents=True, exist_ok=True)
    args.out_note.write_text(NOTE_TEXT_TEMPLATE.format(today=TODAY_ISO), encoding="utf-8")


if __name__ == "__main__":
    main()
