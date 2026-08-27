# Plan patterns for research-plan-writer-skill

## 1. Default seven-block plan structure

Use this as the default full-plan scaffold:

1. Title and meta
2. Background and purpose
3. Research questions
4. Method blocks
5. Target sample and segment notes
6. Timeline
7. Deliverables

Treat section 3 as optional when the plan is better expressed through method-level objectives.

## 1a. Optional blocks (add when the document calls for them)

Two blocks appear in real team plans but are not in the seven-block default. Add them when relevant; do not invent them when there is nothing to put in.

| Optional block | When to add | Observed in |
|---|---|---|
| 연구동향 / 선행연구·시장조사 | 과제 단위 제안서, or any plan whose approval depends on showing the field | `25.C.FACE_CORE` §4 연구동향 — four sub-sections (가상인간 기술 / UX 연구 / 미디어별 UX 설계 / 신흥기술 결합) |
| 성과목표 (정량 / 정성) | the plan must state KPI-level outcomes, not just artifacts | `25.C.FACE_CORE` 성과목표 — 정량(가입·유지율 기여) / 정성(만족도·충성도 제고) |

성과목표 is **not** the same block as 기대 산출물. 산출물 is what the study produces (reports, coding sheets, transcripts); 성과목표 is what the business expects to move. When both exist, keep them separate.

If a 연구동향 block is needed, the output of `$ux-benchmarking-skill` is the natural source for it.

## 1b. Document layer: 과제 단위 vs 차수 단위

The repeated unit changes with the document layer. Decide which layer you are writing before choosing the repeated block.

| | 차수 단위 계획서 | 과제 단위 계획서 |
|---|---|---|
| Scope | one research round | a project or a full year |
| Repeated unit | **method** (one block per method) | **research content area** — methods are collected in a separate 연구 방법 section |
| Timeline granularity | weeks (W1~W5) | months or quarters |
| Example | `24.S.BIZWEB` 1차 사용자 리서치 계획 (UT + 1on1) | `25.C.FACE_CORE` (사용자 분석·페르소나 / 미디엄별 UX 최적화 / 경험 개선 모델 제안 · 1~2월 / 3~6월 / 7~9월 / 10~12월) |

Applying the per-method repeated block to a 과제 단위 plan produces the wrong shape. Ask which layer the user means when the timeline spans more than one round.

## 2. Repeated method block template

Use one block per method.
Keep the same slot order each time.

### Method block slots

1. Target or recruitment condition
2. Objective
3. Method
4. Sample size and rationale
5. Expected output

If RH exists, add a short mapping line such as:
- supports: RH1, RH3

But the mapping line inside the method block is a **convenience, not the record**. The record is the RH × method matrix (RH as primary key, one column per method) — see SKILL.md step 2. Only the matrix makes an untested RH visible.

## 3. RQ and RH decision rule

Use RQ-first planning when the study is exploratory, generative, or defining a new concept.
Use RQ plus RH when the team is evaluating a known proposition, validating assumptions, or comparing alternatives.

Practical rule:
- exploratory study -> RQ required, RH optional
- diagnostic or confirmatory study -> RQ required, RH usually helpful
- if RH feels forced, omit it and keep the plan at the RQ level

Structure, once you have decided to use them:
- RQ is hierarchical (top-level -> `ㄴ` -> `ㄴㄴ`), not a flat list of 3 to 5. `24.S.BIZWEB` ran 12 top-level RQ over 58 rows.
- RH is two-layer (상위 RH proposition -> 세부 RH instantiated per target). `24.S.BIZWEB` ran 163 RH rows off a much smaller set of propositions.
- Do **not** put the full hierarchy in the plan document. Plan shows top-level; the RQ master and RH master are separate spreadsheets. In `24.S.BIZWEB` the shared plan document contains no RQ section at all.

### IF/THEN framing: do not require it

`24.S.BIZWEB`'s RH master has `IF(특정한 액션) · THEN(특정한 결과) · 독립변수 · 종속변수1 · 종속변수2` columns, and every one of them is empty across all 163 rows — the frame was designed and then not used. Write RH as a plain predictive statement (`… 할 것이다`). Do not ask the user to fill an IF/THEN or variable decomposition unless they bring it up.

## 4. Tone rules from team plans

### Narrative sections

Register is chosen per section purpose. Both appear in team plans, and `25.C.FACE_CORE` uses both inside one file.

Internal / recording sections — 격식체 (`~함`, `~임`):
- `... 기반을 마련하는 것을 목표로 함.`
- `... 근거는 부족한 상태임.`

Proposal / outward-facing sections — 경어체 (`~합니다`):
- `... 사용자 중심 가상인간 UX 모델을 개발합니다.`
- `... 금융 환경은 디지털 전환이 가속화되고 있습니다.`

Keep one register per section. Do not mix inside a section.

### Bullets, tables, and labels

Use nominal or telegraphic phrasing rather than long sentences.
Examples of style:
- key value identification
- segment comparison
- output alignment check

### Research questions

Keep RQ in question form.
Examples of shape:
- In what context do users need ...?
- What blocks adoption at ...?

## 5. Stage 1 brief output pattern

The stage 1 brief should usually include:
- background and purpose
- RQ list
- optional RH list
- recommended methods and why
- method blocks
- timeline draft
- success criteria
- risks and exclusions

Use this as a checkpoint artifact, not as a polished final document.

## 6. Stage 2 full-plan output pattern

Expand the stage 1 brief into a document-ready structure.
Typical moves:
- turn short background bullets into a short narrative section
- keep RQ explicit when it helps stakeholder alignment
- convert method blocks into repeated subsections
- convert timing notes into a table
- merge method outputs into a final deliverables section

Stage 2 must not be thinner than stage 1. Method-selection rationale, RH, and success criteria have no default block, so place them deliberately (SKILL.md step 3 table) instead of letting them fall out.

## 7. Common failure modes to avoid

- forcing RH into early exploratory work
- inconsistent slot detail across methods
- sample size with no rationale
- timeline detached from method order
- deliverables that do not match the chosen methods
- background that hides major constraints or scope exclusions
- flattening a hierarchical RQ master into 3 to 5 questions
- writing RH once per RQ when the proposition needs per-target instantiation
- a stage 2 plan that lost stage 1 items (rationale, RH, success criteria)
- forcing 격식체 onto an outward-facing proposal section