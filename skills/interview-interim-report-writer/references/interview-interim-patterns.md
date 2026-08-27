# Interview interim report patterns for interview-interim-report-writer

## 1. Evidence base

This skeleton is grounded directly in a real native artifact opened and read section-by-section: `26.GP.UXQ_그룹 UX 품질 진단/05_synthesize__interim-report__인터뷰결과보고서.docx` (805 total paragraphs, 679 non-empty, 136 tables, 87 heading paragraphs across the file).

Key structural facts confirmed by opening the file directly (not inferred from filename or metadata alone):
- top-level order: `Executive Summary` → `1. 연구 개요` → `2. 핵심 인사이트` → `3. 개선 방향` → `부록`
- `2. 핵심 인사이트` groups into 8 topic areas as `Heading 2` (홈 화면, 상품 탐색·가입, 자산관리, 혜택·이벤트, 고객센터·문제 해결, 정보 탐색, 로그인·인증 절차, 관계사·슈퍼앱), each containing 1-4 `Heading 3` claim-sentence findings (e.g. `2.1.1. 홈이 '대표 계좌 확인 화면'에 머물러 주사용 기능과 자산 현황 확인의 시작점이 되지 못함`)
- `3. 개선 방향` uses flat `Heading 3` claim-sentence items (3.1-3.4) with **no** `Heading 2` topic grouping — this is a deliberate structural difference from section 2
- the file contains **the entire structure twice** (Executive Summary through 부록 repeats). This matches the same version-stacking behavior already documented for `$survey-interim-report-writer`'s survey interim file (Q24 in `리서처_결정대기_목록.md`: 6 stacked "판" in one docx). Treat this as the normal accumulation pattern this skill must also support (see §5).

Compare against the survey interim (`설문결과보고및인터뷰계획.docx`, 1076 total / 855 non-empty paragraphs, 240 tables, 20 sections) and the integrated final report (`하나원큐UX진단종합보고서.docx`, 200 total / 164 non-empty paragraphs, 39 tables, 2 sections) — the three genres differ enough in table density, table purpose (data tables vs. quote/photo boxes vs. label-content boxes), and image count that `리서처_결정대기_목록.md` Q11 explicitly decided to build them as separate skills rather than one skill with branching. This skill covers only the interview interim genre.

## 2. Full section skeleton

### 2A. Executive Summary

- 2-3 narrative paragraphs synthesizing the overall picture. Native example weaves quantitative context directly into qualitative interpretation in the same paragraph (e.g. "추천 의향은 설문 결과 평균 5점(n=280, 7점 만점)으로... '좋다고 느끼는 점 없음' 응답도 전체 응답자 중 21.1%") rather than keeping stats and interpretation in separate blocks.
- A `주요 강점` (or equivalently named) `Heading 2` subsection: one lead paragraph, then short dash-style bullets in the form `label — one-line explanation` (e.g. "빠른 기본 업무 — 자동 로그인, 잔액 확인, 이체처럼 자주 하는 업무는 별도 학습 없이 시작하고 완료 가능."). Do not render these as a numbered list; the native pattern is an em-dash label-explanation pair.
- Keep this section readable in isolation — it should work as a standalone digest even if the reader stops here (this makes it the natural upstream source for `$executive-one-pager-skill` when a report already exists).

### 2B. 1. 연구 개요 (research overview)

- A compact overview table, typically 4 rows × 2 columns: `목적 | 조사 내용 | 방법 | 기간`. The `조사 내용` cell can itself contain a short numbered sub-structure (e.g. "① 기본 뱅킹, ② 탐색·판단, ③ 확장 경험") rather than a flat sentence.
- `Heading 3` sub-blocks: `인터뷰 대상 구성` (participant count, gender/age breakdown, recruiting criteria in prose) and `인터뷰 현장` (logistics) — some rounds also add `한계` (limitations) as a third `Heading 3` block here. Include `한계` when real constraints exist; do not fabricate one.

### 2C. 2. 핵심 인사이트 (core insights)

- `Heading 2` per topic area (screen/flow area for a usability study, concept area for an open-ended study).
- `Heading 3` per claim within that topic — a complete assertion, not a label.
- Under each claim: 2-4 `Normal` paragraphs of synthesis (observation → where it split or contradicted → implied direction), then 2-3 representative quotes in the exact citation format from SKILL.md §4.
- Order topic areas and claims by practical importance / frequency of mention, not by discovery order.

### 2D. 3. 개선 방향 (improvement direction)

- Flat `Heading 3` claim-sentence items — no topic grouping layer here, unlike section 2.
- Each item: 1-2 `Normal` paragraphs stating a concrete direction. No quotes in this section in the native example; it reads as synthesized recommendation, not raw evidence.
- Every item here should trace back to something already established in section 2 — this section restates and sharpens into direction, it does not introduce new findings.

### 2E. 부록 (appendix)

Native example includes, as `Heading 3` items (부록 A, B, C, D...), with `Heading 4` used for sub-results inside a lettered appendix when needed:
- interview question guide content
- participant screening/recruiting survey responses (with a short caveat sentence when question wording varied across rounds)
- the codebook
- companion survey results, when the study is mixed-method (can nest `Heading 4` sub-results, e.g. "설문 1(경쟁사 비교) 주요 결과")

Only include appendix items the project actually produced. An interview-only study with no screening survey should not have a fabricated survey appendix.

## 3. Quote citation format (differs from `$interview-results-dashboard`)

Native format, confirmed directly in the source file:

```
▍ [하나원큐 · 홈 첫 화면] (개편된 홈 첫 화면을 둘러보며) "일단 밑에 더 메뉴가 있다는 거 자체를 인식 못 했고요..."
— P07  남성, 30대 · 고빈도 조회·자산관리 니즈 사용자
```

Structure: `▍ [screen/context label] (situational clause) "quote"` on one line, then `— PID  gender, age band · segment/persona descriptor` on the next.

This is deliberately different from `$interview-results-dashboard`'s citation convention (`문항 번호 | 문항 출처 | PID | 연령/성별 | 관여도 | 원문`), which optimizes for traceability back to a specific question in a lookup surface. This skill's format optimizes for readability in a document meant to be read start to end. Do not mix the two formats in one artifact.

## 4. Version-stacking behavior

The native interview interim file contains its entire structure twice (see §1) — the same accumulate-in-one-file pattern already established for `$survey-interim-report-writer`. When updating an existing document:
- append rather than overwrite (SKILL.md §7)
- if the file has stacked versions without clear dating, do not guess which is authoritative — ask, the same way `template-example-filler`'s Q24 needed a direct researcher answer to resolve which of six stacked survey-interim versions was current

## 5. Boundary with nearby skills

- **`$interview-results-dashboard`**: different artifact, different citation format, different purpose (circulation/lookup surface vs. formal submitted document). If the user asks for participant cards, a quick summary, or a browsable theme dashboard, that is the other skill, not this one.
- **`$qual-thematic-coding-skill`**: the expected upstream. This skill does not perform coding; it writes the report from already-coded evidence.
- **`$interview-quant-coding-skill`**: use its output as companion quantitative context inside Executive Summary and insight paragraphs when the study is mixed-method, the same way the native example blends survey percentages into interview narrative.
- **`$executive-one-pager-skill`**: downstream, not upstream. Once this skill produces a stable interview interim report, `$executive-one-pager-skill` can compress it — do not build a compressed executive narrative inside this skill's own Executive Summary section beyond what §2A already covers.
- **`$report-type-splitter`**: the umbrella decision under which this skill was split out (Q11 in `리서처_결정대기_목록.md`). Route there when the user is choosing among report families rather than asking specifically for an interview interim.
- **`$survey-interim-report-writer`**: sibling skill, same append/version-marking convention (§4), but a structurally different genre — do not merge the two or borrow the survey interim's table-heavy skeleton here.
