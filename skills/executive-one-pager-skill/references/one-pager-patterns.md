# One-pager patterns for executive-one-pager-skill

## 1. Evidence base — read this before treating any skeleton as fixed

**2026-08-19 team confirmation (two-part)**: a researcher confirmed that executive summaries are *generally* written after the full report, as a compression of it. In the same conversation, the researcher also confirmed this skill needs to work directly from analysis content or project-related files when needed — the report-first pattern describes common practice, not a precondition this skill enforces (see SKILL.md §1). Both native examples below happen to be the common, report-first case:

- **Timeline narrative** — `25.S.MTSUX_주식 및 자산관리 모바일 사용자 경험 개선/05_synthesize__executive-summary__최종보고_인트로_250327.pdf` (7p). The only artifact in native explicitly tagged `executive-summary`. Its filename literally reads "최종보고_인트로" (**final report intro**) — it is the intro/summary companion to an already-completed final report, not a pre-report preview. Structure: cover (project period, team) → `진행 과정` timeline (desk research → focus workshop → 1st survey → 2nd interview, each step labeled with method + purpose + output) → per-step result examples. Read this as a **retrospective retelling** of a finished process, not a forward-looking plan.
- **Conclusion-first + RQ-organized hybrid** — `25.S.1QAI_하나원큐 AI Agent 사용자 기대 및 인식 조사/05_synthesize__final-report__최종보고서_260203.pdf` (21p). Not tagged `executive-summary`, but its opening section literally is one, embedded as the front matter of an already-drafted `final-report`: page 1 is headed `Executive Summary` and leads with four claim-sentence bullets (`맞춤형 시뮬레이션에서의 가치 발견`, `신뢰의 핵심 조건으로서의 설명 가능성`, `자동화에 대한 거부감과 사용자 주도권 선호`, `Phase 1 Quick-Win 전략: '신뢰 구축 및 핵심 가치 경험'`) before any methodology appears. The report body that follows is then organized by numbered RQ-adjacent sections (`1. 연구 개요` with `1.1 참여자 특성`, `1.2 연구 질문`; `3. 주요 인사이트` with `3.1`, `3.2`, `3.3` each headed by a claim sentence). This is the more literal, unambiguous case of "compress the finished report."

Both examples are compressions of already-finished work — they differ in narrative style (chronological retelling vs. conclusion-first), not in when they were produced relative to the underlying report.

No native example of a pure Minto pyramid (headline recommendation first, then a strict evidence pyramid beneath it, no narrative or RQ framing at all) has been found yet. The Minto skeleton below is included because Q9 in `리서처_결정대기_목록.md` explicitly decided to keep it available as an option, not because it has been observed in native.

Do not claim more convergence than this. When handing off a draft, say which of the two observed patterns (or the unobserved Minto option) was used, and state what kind of material was actually compressed — an existing report, a dashboard, or analysis/project files directly (see SKILL.md §1).

## 2. Structure-mode skeletons

### 2A. Timeline narrative (default)

Use when the source material already reads as a step-by-step process, or when no mode was specified.

1. **Cover / framing** — project period, owning team, one-line project name
2. **진행 과정 (process timeline)** — one block per phase, each with:
   - phase label and date range
   - method used
   - purpose of that phase
   - what it produced (feeds the next phase)
3. **Per-phase result highlights** — for each phase, 1-2 headline findings with minimal supporting evidence (one stat, one quote, or one comparison)
4. **What this means going forward** — brief bridge into the next phase or into recommendations (see §3 in SKILL.md workflow)

Keep phase count matched to the actual project timeline; do not pad with phases that did not happen.

### 2B. Conclusion-first (Minto pyramid)

Use when the audience needs the answer before the method, or when explicitly requested.

1. **Headline answer / recommendation** — the single most important conclusion, stated as a complete sentence
2. **Supporting claims** — 3-5 claim-sentence headings, each one level below the headline
3. **Evidence per claim** — one to two lines of the strongest supporting evidence under each claim, not the full backing analysis
4. **Implication or next action** — what the audience should do or decide based on the headline

This skeleton is not yet backed by a native example (see §1). Flag this explicitly in the hand-off when this mode is chosen.

### 2C. RQ-first

Use when the source study was already framed around 3-5 named research questions, or when the audience is used to reading findings against explicit questions.

1. **Executive Summary block** — a short list of claim-sentence bullets stated before any methodology, one per major insight (see the 1QAI example in §1) — this block alone can double as a compressed one-pager even when the rest of the report follows in RQ order
2. **연구 개요 (research overview)** — purpose, participant/sample characteristics, and the named RQs, kept to a compact table or short list
3. **RQ-mapped insight sections** — one section per RQ (or per major insight cluster), each headed by a claim sentence, not the RQ text itself
4. **Segment or targeting notes when relevant** — if the study produced user segments, a short segment characterization block can sit between the overview and the RQ sections (as in the 1QAI example's `사용자 세그먼트 특성 및 우선 타겟팅 전략`)

## 3. Output layer rendering notes

- **One-pager copy**: draft as continuous markdown first, then render as docx (§4) — docx is the deliverable, not the markdown draft. Headings stay as claim sentences; keep paragraph length short per section.
- **Intro summary slide outline**: convert each skeleton section into one slide entry — title (the claim sentence), one key visual or data point, one supporting line. Do not write slide prose as full paragraphs.
- **Executive-summary section draft**: draft as markdown, then render as docx (§4). Skip cover/framing elements meant for a standalone one-pager so the section can sit at the front of a larger report docx and still read coherently on its own.

## 4. Docx generation — the required final format

The one-pager copy and executive-summary section layers must end as a `.docx`, not stop at a markdown draft. This was confirmed by opening a real native artifact directly: `26.S.PAYAI_하나페이 UX 개선/05_synthesize__insight-summary__Phase1_260121_퀵서머리공유.docx` (the same PAYAI quick-summary already used as the row-compressed exemplar in `$interview-results-dashboard`).

What that inspection showed:
- the document uses **`Heading 1`** for its title paragraph and **`Table Grid`** for its table — both are Word's built-in default styles, not custom styles
- run-level font/size/color are unset (`None`) throughout — meaning the document inherits the **theme default fonts** (`docDefaults` in `styles.xml` point to `minorHAnsi`/`minorEastAsia` theme fonts, 11pt) rather than a hardcoded custom font
- `Heading 1`'s color is `365F91` — Word's own default Heading 1 theme color, not a team brand color
- conclusion: **native's real report artifacts do not carry custom branding**. Do not invent one when generating a docx here.

Build the docx with `python-docx`, using only:
- `doc.add_heading(text, level=1/2/3)` for section headings
- default `Normal` style paragraphs for body text (`doc.add_paragraph(text)`)
- `style="List Bullet"` / `style="List Number"` for lists
- `table.style = "Table Grid"` for any tables
- a simple left-indented, italicized paragraph pair (quote text, then an `— attribution` line) for representative quotes — there is no native "block quote" style to match, so keep this minimal rather than inventing box/shading formatting

Do not add custom `RGBColor` branding, custom font names, or shaded table headers unless the user supplies an actual team template file to match — none of that is present in the real native artifact this convention is based on.

See `validation_runs/executive-one-pager-skill/2026-08-19_23.BK.S.233Q.GBIUX/build_docx.py` for a worked example that follows this convention end to end.

## 5. Boundary with nearby skills

- **`$report-type-splitter`'s child skills (survey/interview/heuristic interim writers, integrated final report writer) are the most common upstream source, but not a hard prerequisite.** When a finished or stable-draft report already exists, compress that. When it doesn't, this skill can still build an executive summary directly from analysis content, dashboard output, or project files — that is a normal use case, not a workaround.
- Route to `$report-type-splitter` instead of continuing here only when the user's actual need is the full report body itself, or when a draft built here keeps growing past a tight, skimmable length (that growth is the signal to hand off).
- Use `$action-matrix-generator-skill` for the recommendation or next-action block's prioritization logic. This skill renders that output into the narrative; it does not re-derive priority.
- Use `$survey-results-dashboard` or `$interview-results-dashboard` output as a source on equal footing with a report draft or raw analysis/project files — pick whichever material the task actually has available.
- Do not confuse this skill's "one-pager" with a literal single physical page — team precedent (both native examples) runs several pages/slides while still functioning as an executive compression layer.
