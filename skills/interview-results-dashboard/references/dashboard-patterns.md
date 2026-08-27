# Dashboard patterns for interview-results-dashboard

## 1. Default output layers

Use a layered package by default:
- quick summary
- participant and theme dashboard view
- optional report-style detail view
- optional issue catalog

If the user wants only one layer, state which layers were omitted.
Do not assume that the reusable issue catalog is always required.

## 1A. Reference dashboard alignment

When the user asks to align with the internal dashboard reference, use the surface logic observed in:
- `C:/Users/hanati/Documents/GitHub/ux_evaluation_hana1q/public/index.html`
- optionally `C:/Users/hanati/Documents/GitHub/hana1q-reserach-analysis/dashboard/index.html`

Reusable patterns from that reference are:
- one artifact with multiple reading depths instead of one flat page
- sticky navigation for long HTML
- summary cards that jump into deeper sections
- theme-first insight blocks
- evidence, quote, and improvement-direction separation
- project overview and source note visibility

Do not copy survey-specific content rules blindly into interview work.
Transfer only the surface patterns that still make sense for qualitative evidence.

## 2. Quick-summary row pattern

One strong observed pattern is a compressed two-column summary table:
- `구분`
- `상세 내용`

Practical row groups usually include:
- study or phase information
- participant mix
- prior behavior or existing experience
- 3 to 5 theme blocks
- trust, expectation, or attitude block when relevant
- recommendations or implications

When mixed-method evidence exists, a theme row can contain:
- qualitative Top 3 bullets
- companion metrics
- short implication note

When the project already uses a compressed quick-summary table, a practical row micro-schema is:
- current behavior or usage split
- Top 3 theme labels
- AI expectation, intention, or trust metric

Treat the Top 3 as editorial theme labels derived from coded evidence, not as mandatory raw frequency order.
It is acceptable to merge or rename low-value buckets when a clearer action theme better represents the pattern, as long as the underlying counts remain traceable.

Keep the row count tight enough that a reader can scan the whole summary quickly.

If the surface is HTML, pair the quick summary with:
- a short hero statement
- 3 to 5 key priority cards
- jump links to deeper theme blocks

## 2A. Quick-summary variants

Do not assume the table shell is universal.
The current native corpus suggests at least three summary variants, plus one frequent lookalike:

- `row-compressed table`
  - strongest example: PAYAI
  - one artifact-level table carries study basics, theme rows, and trust rows
- `bullet insight memo`
  - examples closer to RM, TVBK
  - summary is mainly paragraph or bullet blocks with light supporting tables
- `report-style summary with embedded compact tables`
  - example closer to UXQ interview report
  - executive summary prose appears first, with compact profile or method tables embedded nearby
  - a related sub-case (GBIUX) pairs narrative summary prose with a `대분류 | 소분류 | 내용` compact recommendation table; treat that table with the rule in §6A-2, not as a quick-summary row shell
- `section summary or appendix table inside a larger report`
  - examples closer to BIZWEB interim pdf, PAYAI interim pdf, BIZMOB final report deck
  - `결과 요약` or `구분/상세` can appear inside the report, but the artifact itself is still a large report or deck rather than a standalone quick-summary deliverable

Practical rule:
- if the project already has a stable compressed table, preserve that form
- if the project reads like an executive memo, keep bullets or short paragraphs as the summary spine
- if the project is already report-like, extract a lighter summary layer instead of flattening the whole report into one table
- do not promote appendix `구분/상세` comparison tables into the main summary shell unless the artifact itself is clearly acting as the summary deliverable

## 3. Participant card rule

Each participant card or participant block should usually include:
- PID or anonymized participant label
- segment or context
- top pain point
- notable workaround or behavior clue
- trust, expectation, or attitude signal when relevant
- one representative quote

Do not turn participant cards into transcript retellings.
They should act as grounded snapshots, not full case studies.

If the dashboard is long-form, participant cards may also be rendered as a profile table or appendix-style sheet instead of only mini cards.
The important part is preserving comparison-friendly fields, not the card shell itself.

## 4. Cross-interview theme block rule

Each theme block should usually include:
- theme title
- supporting participants or segments
- qualitative Top 3 pattern
- contradiction or split, if present
- optional companion metric
- implication or design relevance

Order theme blocks by confidence or practical importance, not only by mention count.

For reference-aligned HTML, a practical theme block usually contains:
- theme title
- one-paragraph summary
- participant or segment support note
- representative quotes
- optional companion metric or mixed-method bridge
- improvement direction

Treat `improvement direction` as its own visible sub-block rather than burying it in prose.

## 5. Mixed-method evidence rule

When numeric evidence exists, keep it adjacent to the relevant qualitative theme.
Label the numeric source clearly:
- quantitative coding
- related survey result
- other validated metric

Do not imply formal quantification if the number is only a loose support signal.
If no companion metric exists, leave the qualitative layer standing on its own.
If a mixed-method quick summary already exists, preserve the editorial layer instead of flattening it back into raw frequency output.
The skill should be able to show both:
- count-backed evidence anchors
- the human-readable theme label that was actually chosen for summary circulation

If the project is interview-only, use an explicit note that the current view is qualitative-first.
Do not imply that a survey or heuristic bridge exists when it does not.

## 6. Issue-catalog expansion rule

Use the issue-catalog layer only when downstream reuse matters and a taxonomy exists or can be kept stable.
A practical base schema is:
- related menu or flow
- component
- component detail
- issue summary
- user evidence or quote
- improvement guide
- source section or link

Optional fields include severity, owner, priority, or status.
Treat this output as a reusable workbook or structured table, not necessarily as a visual dashboard.

If a reference dashboard includes screenshot evidence or competitor comparisons, only add those layers when the current interview project actually has them.
Do not fabricate visual evidence blocks to imitate the reference.

### 6A-2. The middle case: compact recommendation table without a taxonomy

Not every "what should we change" table is an issue catalog.
When the project needs improvement suggestions grouped by category, but has no stable menu, feature, or component taxonomy yet, keep a lighter `대분류 | 소분류 | 내용`-style compact recommendation table instead of forcing the full issue-catalog schema.

Signals to use this middle option instead of promoting to the full issue catalog:
- the rows are recommendation text grouped by researcher-defined category, not findings tied to a reusable menu/component taxonomy
- no downstream team has asked to filter or maintain this as a workbook asset
- the source artifact is an insight or interim report section, not a standalone reuse-oriented deliverable

Do not treat this compact recommendation table as a shrunken issue catalog. It serves a different purpose (organizing what to change) than the issue catalog (a reusable, taxonomy-keyed lookup asset). If a stable taxonomy later emerges, migrate the content into the full issue-catalog schema instead of stretching this lighter table.

## 6A. Long-form navigation rule

When the HTML surface exceeds a few sections, add at least one of:
- sticky left navigation
- sticky right table of contents
- summary jump cards
- top-level tabs such as `summary`, `dashboard`, `report`

Use this only when the extra navigation genuinely reduces scanning cost.
Skip it for short markdown summaries.

## 6B. Research-method and open-question sections

The reference dashboard separates:
- topic-based results
- research-method results
- open or not-yet-answered questions

For interview dashboard work, these are optional but useful when:
- the user wants a report-like artifact
- the project has multiple upstream evidence packs
- some questions remain only partially answered

If you include an unresolved-question section, state what is missing and why.

## 7. Renderer selection rule

Prefer markdown or docx-style tables when:
- the quick summary is the main deliverable
- the audience needs a fast circulation draft

Prefer static HTML when:
- the user wants a readable dashboard surface
- participant blocks and theme blocks should be browsable

Prefer workbook packaging when:
- the issue catalog will be filtered, extended, or maintained
- component or menu lookup matters more than visual storytelling

Keep the content model stable across renderers.

## 8. Boundary with nearby skills

Use `$qual-thematic-coding-skill` first when the work is still about extracting grounded qualitative evidence.
Use `$interview-quant-coding-skill` when the missing layer is fixed-tag coding, ranking, or score-based comparison.
Use `$transcript-verification-enhancer` or `$transcript-pipeline-skill` when the transcript itself is not analysis-ready.
Use `$executive-one-pager-skill` when the user wants a condensed executive narrative.

### 8A. Boundary with `$report-type-splitter`

Route to `$report-type-splitter` (or its relevant child report-writer) instead of building a dashboard when the source or the requested deliverable looks like a narrative report body, not a scan-and-share companion.

Signals pointing to `$report-type-splitter`:
- paragraph count dominates over table/block count, and the content reads as connected argument rather than independent rows or cards
- there is a multi-level heading structure (e.g. `1. 개요 → 2. 결과 → 3. 제안`) rather than a flat `구분 | 상세 내용` shape
- the deliverable itself is what gets submitted or presented as the interim/final report, not a companion summary

Signals staying with this skill:
- the material is already table- or block-first (row-compressed table, bullet memo, participant/theme cards)
- the deliverable is meant to be skimmed quickly alongside or before the report, not submitted as the report itself

The trickier case is a compact table embedded inside an otherwise narrative report (for example, a `대분류 | 소분류 | 내용` recommendation table inside a long interim-report PDF). Route by what the user is actually asking for, not by the source artifact's overall genre:
- "pull out just the recommendation table" or "give me a light summary of this" → this skill extracts and re-renders that one compact block (see §6A-2), and leaves the narrative body, research overview, and appendix untouched
- "rewrite/restructure this report" or "improve the report body" → hand off to `$report-type-splitter`'s matching child-skill instead

This works in both directions: if a quick-summary user later asks to expand the output into a full interim or final report, do not stretch the summary into fake narrative sections — hand off to `$report-type-splitter` instead.

A related but currently unclaimed shape: a large multi-source scorecard report that lays survey, interview, and expert-evaluation results side by side per screen or feature (dozens of slides, no compression). This is not a quick-summary shell, but `$report-type-splitter`'s current document-type family does not cover slide-deck reports either (that split is still an open decision on the `$report-type-splitter` side). Do not force this shape into this skill just because `$report-type-splitter` hasn't formally claimed it yet.

### 8B. Boundary with `$heuristic-evidence-linker`

`$heuristic-evidence-linker` is scoped to heuristic-evaluation workbooks (Task-ID-anchored xlsx plus a dedicated capture folder), not interview coding output. The two skills rarely compete over the same source material — the real risk is this skill overreaching into evidence-linking work that belongs to `$heuristic-evidence-linker`.

- Quoting participant text as evidence is a normal part of this skill's participant and theme blocks — keep doing that.
- Only place a screenshot or image next to a theme or participant block when that image is already reliably linked to the issue (through `$heuristic-evidence-linker`'s capture-folder-plus-reference convention, or an equivalent stable reference the project already has).
- Do not attempt to match, locate, or re-link a loose pool of screenshots to issues yourself. That matching logic belongs to `$heuristic-evidence-linker`. If a user asks to "attach the matching screenshots" and no stable link exists yet, say so and point to `$heuristic-evidence-linker` instead of guessing or fabricating a placeholder.
- If the input itself is a heuristic-evaluation workbook (columns like `Task ID` or `평가자N`) rather than interview coding output, it is out of scope for this skill regardless of whether screenshots exist — route to `$heuristic-evidence-linker` or the heuristic-evaluation vision skill instead.
