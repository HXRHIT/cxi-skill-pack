# Research QA checklist

## How to apply this checklist

- Always run A, B, and C.
- Pick D-survey or D-interview by instrument type.
- Run E and F once at the full-document level.
- If a document contains both survey and interview sections, branch D by section.

## Severity scale

- Critical: likely to distort responses or create major compliance risk; must fix before fieldwork.
- Moderate: meaningful bias or design risk; fix unless there is a strong reason not to.
- Minor: wording, consistency, or cleanliness issue with lower response distortion risk.

## A. General question bias

- A1 Leading question: wording implies the desired answer.
- A2 Double-barreled question: more than one concept is packed into one item.
- A3 Social desirability bias: wording pushes respondents toward a socially approved answer.
- A4 Order effect: earlier questions or options are likely to frame later responses.
- A5 Response-option bias: options are imbalanced, non-mutually-exclusive, or missing a sensible middle or null case.
- A6 Presumed experience question: the wording assumes the respondent had a specific experience or feeling.
- A7 Ambiguous wording: vague adverbs or fuzzy terms such as often, sometimes, or easy.
- A8 Excessive recall burden: the question depends on memory that is unlikely to be accurate.
- A9 Early sensitive question: sensitive information is placed too early and may increase drop-off.
- A10 Forced naming bias: the instrument names a UI concept or object for the participant and frames the answer space.
- A11 Hypothetical intent question: asks users to predict future behavior instead of grounding in real past behavior.
- A12 UX or research jargon: specialist terms are left unexplained for a general audience.
- A13 Evaluative adjectives in setup text: descriptive text contains positive adjectives such as smart, good, or convenient that steer the next answer.

## B. Research design alignment

- B1a Forward mapping: each RQ or RH has at least one matching question.
- B1b Reverse mapping: each question maps to a real RQ or RH, or is flagged as scope drift.
- B1c Reverse proposal: if RQ or RH is missing, infer likely candidates from the question set.
- B2 Method-question fit: survey instruments overuse open text or interview guides overuse closed yes-no prompts.
- B3 Segment-difficulty fit: the language is too advanced for the target segment or product familiarity level.

## C. Hana finance and compliance risks

- C1 Loss-responsibility framing: wording implies blame or guilt for investment choices or losses.
- C2 Regulatory sensitivity: wording sounds like product recommendation or advice.
- C3 Finance literacy gap: finance terms are used without explanation for a low-literacy segment.
- C4 Excessive asset data request: the instrument asks for specific account or asset details that are not required.
- C5 Tone or honorific failure: internal draft tone leaks into customer-facing language.
- C6 Benefit-first consent framing: a promised AI benefit is stated before asking for sensitive data consent, which can inflate willingness.

## D-survey. Survey-only checks

- D-S1 Scale and option balance: Likert or option sets are skewed or incomplete.
- D-S2 Fixed-order framing risk: the order cannot be corrected live, so priming risk is higher.
- D-S3 Length and fatigue risk: the instrument is likely to cause late-stage fatigue or drop-off.
- D-S4 Option-order priming: an option list, especially the last option, is likely to pull answers in one direction.
- D-S5 Explanation-text bias: an explanatory note nudges interpretation instead of clarifying neutrally.

## D-interview. Interview-only checks

- D-I1 Probe bias: suggested follow-up probes are likely to become leading questions.
- D-I2 Rapport order: sensitive topics arrive before enough rapport or warm-up.
- D-I3 Open versus closed balance: the guide relies too much on closed questions for a qualitative interview.
- D-I4 Rephrasing bias: moderator recap language puts the moderator's interpretation into the participant's mouth.
- D-I5 Pre-framed confirmation prompt: the moderator presents an interpretation first and asks the participant to confirm it.
- D-I7 Cross-source personalization accuracy: the guide references the participant's own prior survey answer (via a merge field or a composed sentence like "you said you had trouble with X"). If the respondent-ID match between the survey and interview roster is wrong, the moderator states something as fact that this participant never actually said — a data-linkage-caused variant of A6 rather than a wording problem. Confirmed independently in two projects (26.GP.UXQ merge-field case; 23.BK.S.233Q.GBIUX case where the project's own stakeholder flagged the exact same risk in review comments).

## E. Whole-design confirmation bias

- E1 Hypothesis-confirming design: the full instrument mainly tries to confirm one preferred answer.
- E2 Single-source dependence: the design relies on one method only when triangulation would matter.
- E3 Lack of independent reviewer: the same author is also the only reviewer.

## F. Editing and consistency defects

- F1 Edit leftovers: old numbering, placeholder text, or stale labels remain in the final instrument.
- F2 Parallel-block inconsistency: repeated blocks use inconsistent gating or structure.
- F5 Moderator-instruction and verbatim-script separation: moderator-only stage directions or lookup notes (e.g. "(open the app)", "check survey answer X") sit in the same cell or column as the text meant to be read verbatim to the participant, distinguishable only by a separate method-type tag if at all — risking a rushed moderator reading an internal instruction aloud. Confirmed independently in two projects (26.GP.UXQ bracketed stage directions inline with dialogue; 23.BK.S.233Q.GBIUX observation checklist text sharing the same column as spoken script, distinguished only by a method column).

## Candidate patterns (single-instance, not yet converged)

Not yet folded into the numbered checklist above — label findings against these explicitly as candidates rather than treating them as confirmed A-F items, per the guardrail in SKILL.md. Promote to a numbered item once a second independent instrument reproduces the pattern. (D-I7 and F5 were promoted out of this list on 2026-08-19 after reproducing in a second project — see history note below.)

- F3 (candidate, 1 instance: 26.GP.UXQ) Merge-field non-substitution risk: the instrument contains merge fields (e.g. `{ A }`, `{{답변}}`) pulled from a linked survey. If the survey linkage fails at fieldwork time, the literal placeholder text can be read aloud to the participant. Distinct from F1 because the failure mode lives outside the document (in the linkage system), not in leftover editing. Checked against two more instruments (23.BK.S.233Q.GBIUX, 25.S.MTSUX) with no literal merge-field syntax present — not reproduced yet, but those documents simply didn't have the mechanism to test, so this is not a refutation.
- F4 (candidate, 1 instance: 26.GP.UXQ) Final-column drift across revision lanes: a working document with parallel revision columns (draft → stakeholder feedback → editor revision → final/production) where the column marked as final does not actually reflect the most recent approved revision. Distinct from F1 because the issue isn't stale content lingering — it's ambiguity about which revision lane was actually approved.
- A14 (candidate, 1 instance: 26.GP.UXQ) Fixed time-budget position bias: per-question time budgets are set in advance, so topics placed later in the guide are structurally more likely to be cut short if earlier ones run over — independent of the topic's actual importance. Distinct from A4 (which is about content priming from earlier answers) because the mechanism here is time allocation, not framing. Not present in 23.BK.S.233Q.GBIUX or 25.S.MTSUX (no time-budget column in either) — untested rather than refuted.
- D-I6 (candidate, 1 instance: 26.GP.UXQ) Think-aloud task framing bias: a think-aloud or observed-task instruction names the target the participant is supposed to discover (e.g. "find [specific menu item]"), which partially solves the navigation problem the task was meant to observe and can mask real findability issues. 23.BK.S.233Q.GBIUX's equivalent task instruction avoided this (generic "share your thoughts freely" framing, no named target) — a clean counter-example showing the risk is real but not universal, not a refutation of the pattern itself.
- F6 (candidate, 1 instance: 23.BK.S.233Q.GBIUX) Spreadsheet auto-format corruption of ID-like fields: a column meant to hold a short ID string (e.g. `1-1`, `6-31`) gets silently auto-converted by the spreadsheet application into a date/datetime value, corrupting the ID. If that ID is used downstream for citation or coding traceability (as `$interview-interim-report-writer` and `$interview-results-dashboard` both do), the corruption breaks traceability without any visible error.

## Candidate promotion history

- 2026-08-19: D-I7 and F5 promoted from candidate to numbered items after reproducing independently in a second project (23.BK.S.233Q.GBIUX) alongside their original instance (26.GP.UXQ). See `validation_runs/research-qa-skill/2026-08-19_round3_gbiux-mtsux/03_checklist_promotion_decisions.md` for the full reasoning.

## Default report reminder

When reporting issues, keep the output in a practical review format:
- lead with the highest-severity findings
- quote the exact problematic text
- tie each issue back to a checklist item
- suggest a focused fix rather than rewriting the whole document by default
