---
name: research-plan-writer-skill
description: "Turn a research brief, business question, or planning notes into a structured UX research plan with optional RQ and RH framing, repeated method blocks, timeline, deliverables, and team-style formal tone. Use when Codex needs to draft or refine a research plan, protocol overview, or planning brief before questionnaire or interview design."
---

# Research Plan Writer Skill

## Overview

Use this skill to write research plans in two stages:
1. a planning brief for direction check
2. a full plan draft for documentation

Keep the core workflow in this file.
Read [references/plan-patterns.md](references/plan-patterns.md) when you need the shared block structure, method template, or tone rules.

## Inputs

Gather these inputs when available:
- business question or decision to support
- target users or segments
- what is already known and still unknown
- timeline or deadline
- constraints, risks, or scope exclusions
- preferred output format if the user already has one

If the research type is not stated, infer whether the work is exploratory or diagnostic and state that assumption.

## Workflow

### 1. Build the stage 1 planning brief

Produce a concise checkpoint draft with:
- background and purpose summary
- research questions, written as a hierarchy (see step 2a)
- optional research hypotheses only when the study is diagnostic or confirmatory
- recommended methods with rationale
- one method block per method
- draft timeline
- success criteria
- risks, constraints, and out-of-scope notes

Pause after this brief unless the user explicitly asks to draft straight through.

### 2a. Write RQ as a hierarchy, not a flat list

Team RQ masters are hierarchical, not a short flat list.
Observed in `24.S.BIZWEB` (`02_establish__rq-list__연구질문_기업뱅킹.xlsx`, 58 valid rows): 12 top-level RQ, each expanded into `ㄴ` sub-questions and sometimes `ㄴㄴ` sub-sub-questions.

Rules:
- Produce top-level RQ as the themes the study must answer. Do not cap this at 3 to 5 when the study scope is broad; 10 or more top-level RQ is normal for a channel-wide diagnostic.
- Under each top-level RQ, write the sub-questions that make it answerable. Mark depth explicitly (`ㄴ`, `ㄴㄴ`) so the level is unambiguous.
- Carry these per-RQ attributes when the user has them: theme label, priority (상/하), target respondent group, author, and source (where the question came from).
- In the plan document itself, show only top-level RQ. The full hierarchy belongs in a separate RQ master, not inside the plan narrative.

If the user asks for a short plan and the hierarchy would overwhelm it, keep the hierarchy in the RQ master and summarize top-level RQ only. Do not flatten the hierarchy away.

### 2b. Recognize that RQ come from a seed list, not from nothing

Teams collect raw seeds first (`01_understand__research-notes__생각리스트.xlsx` in `24.S.BIZWEB`: 120 rows of `사람 · 출처 · 생각`), review them, then triage which seeds get promoted into the RQ master (`사전 리서치` Yes/No column).

When the user provides such a seed list, do not rewrite it into new RQ from scratch. Triage it: mark each seed as promoted or deferred with a reason, and preserve the seed's author and source on the RQ it becomes.

### 2. Decide how much RQ and RH structure to use

Use RQ only when the study is exploratory, generative, or too early for stable hypotheses.
Use RQ plus RH when the study is diagnostic, evaluative, or confirmatory enough to test explicit claims.

Do not force RH into a study that is still framing the problem space.

When RH exists, write it in two layers, and map methods to RH — not RH to methods:

- **상위 RH (general proposition)**: the claim itself, stated once. Example shape observed in `24.S.BIZWEB`: "메뉴명이 기존에 익숙하던 용어와 달라 메뉴를 이해하거나 찾기 어려워할 것이다."
- **세부 RH (instantiated)**: the same proposition re-stated for each concrete target it applies to. In `24.S.BIZWEB` that one 상위 RH was instantiated per menu (상품몰 / 뱅킹관리 / 자금관리 / 금융거래 / 외환·수출입 / B2B전자결제 …), producing 163 rows total. Keep each instance as its own row so it can be tested and reported separately.
- **RH × method matrix**: the RH is the primary key. For every RH row, mark which methods will test it (one column per method — e.g. 경쟁사분석 / Card Sorting / Tree Testing / Survey / UT / IDI). Do not express this only as a `supports: RH1, RH3` line inside a method block.

The matrix direction matters: it makes an RH that no method tests visible as an empty row. The method-block direction hides that gap.

### 3. Draft the full research plan

Read [references/plan-patterns.md](references/plan-patterns.md).
Use the seven-block plan structure there as the default scaffold.

**Carry every stage 1 item forward.** Stage 2 expands the brief; it must never be shorter or thinner than it. Four stage 1 items have no home in the seven default blocks and get dropped unless you place them deliberately:

| Stage 1 item | Where it goes in stage 2 |
|---|---|
| method selection rationale (why this method mix) | into the 방법론 block intro, or a short 리서치 설계 근거 paragraph |
| RH list | into the RQ block (or its own block) — never dropped when the study is diagnostic |
| success criteria | into 기대 산출물, or its own 성과목표 block |
| assumptions / open decisions / dependencies | keep as the closing block (step 6) |

Before returning the stage 2 draft, check it against the stage 1 brief item by item and confirm nothing was lost.

Expand or compress sections based on project maturity:
- newer or riskier concepts need more background, assumptions, and scope notes
- established diagnostic work can move faster into method blocks

Default to markdown unless the user asks for another deliverable format.

### 4. Keep the repeated method blocks consistent

For every method, use the same five-slot pattern:
- target or recruitment condition
- objective
- method
- sample size with rationale
- expected output

If the plan uses multiple methods, keep slot names and level of detail parallel across them.

### 5. Match team tone

Tone in Korean research plans is decided **per section purpose**, not per document. Both registers appear in team documents, and `25.C.FACE_CORE`'s plan contains both in one file — the internal summary in 격식체, the 「연구 제안서」 body in 경어체.

- **Internal / recording sections** (내부 요약, 배경 메모, 진행 기록): 격식체 — `~함`, `~임`, `~목적으로 함`.
- **Proposal / outward-facing sections** (연구 제안서, 대외 공유용 배경·목적·방법): 경어체 — `~합니다`, `~제시합니다`, `~개발합니다`.
- Ask which register applies when the document's audience is not stated. If you must assume, use 격식체 for a 차수 단위 내부 계획서 and 경어체 for a 과제 단위 제안서, and say which you assumed.
- Never mix registers inside one section. Mixing across sections is fine and matches team practice.
- Bullets, labels, and tables: short nominal phrasing in both registers (`핵심 가치 발굴`, `세그먼트 비교`).
- RQ: explicit question form in both registers.

Keep the plan factual and operational rather than promotional.

### 6. Hand off clearly

At the end of the draft, list:
- assumptions you had to make
- decisions still open
- dependencies that could change the plan

If the user later creates instruments from this plan, suggest a follow-up QA pass with `$research-qa-skill`.

## Guardrails

- Do not invent fixed certainty around sample size; present rationale and confidence level.
- Do not duplicate the full plan when the user only asked for the stage 1 brief.
- Do not collapse multiple methods into one mixed block if the outputs or audiences differ.
- Keep exclusions explicit when a plan does not cover production, security, or policy review.
- Preserve traceability from business question to RQ, from RQ to RH when used, and from RQ or RH to methods.

## Expected use cases

Use this skill for prompts such as:
- turn this research brief into a full plan
- draft a UXR plan from these business questions
- structure our RQ, methods, and timeline for this study
- help me write a research planning document before instrument design