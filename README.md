# CXI Skill Pack

이 repo는 CXI/UXR 팀이 여러 AI agent에서 같은 UX 리서치 스킬을 사용하기 위한 배포용 skill pack이다.

원본 스킬 개발과 검증은 `UXR-Template` repo에서 진행한다. 이 repo에서는 배포 산출물만 관리하며, 스킬 내용을 직접 수정하지 않는 것을 원칙으로 한다.

## 빠른 시작

```bash
git clone https://github.com/HXRHIT/cxi-skill-pack.git C:\CXI\cxi-skill-pack
cd C:\CXI\cxi-skill-pack
```

Codex에 설치:

```bat
adapters\codex\install_to_codex.bat
```

Claude 계열 slash command 생성:

```bat
adapters\claude\install_slash_commands.bat
```

ChatGPT Project 안내문 생성:

```bat
adapters\chatgpt\generate_project_instructions.bat
```

MCP starter 실행:

```bash
pip install -r adapters/mcp/requirements.txt
python adapters/mcp/uxr_mcp_server.py
```

## 업데이트

```bash
cd C:\CXI\cxi-skill-pack
git pull
```

agent가 별도 폴더로 복사 설치되어 있다면 `git pull` 후 해당 adapter를 한 번 더 실행한다.

## 주요 파일

- `manifest.json`: 배포된 스킬 목록과 fingerprint
- `skills/`: 실제 스킬 진입점 `SKILL.md`와 재사용 코드
- `adapters/`: Codex, Claude, ChatGPT, MCP 연결 도구
- `runtime/`: 자연어 요청을 스킬로 연결하거나 업데이트를 비교하는 공통 도구
- `docs/install-guide-ko.md`: 팀원용 한글 설치 가이드

## 포함 스킬

- `app-review-analysis-pipeline`: Collect Play Store and App Store reviews for a user-specified app and period, then produce a sentiment + theme summary dashboard (pros/cons + opinion themes) in CSV/Excel/HTML for UX review workflows. Use this when Codex user asks for app-store review intelligence and wants consistent, reproducible 분석 결과 instead of 수동 복붙.
- `coding-sheet-generator`: Generate blank or prewired coding workbook skeletons for structured interview activities such as Likert scales, adjective cards, rankings, multiple-choice coding, and short open-response batteries. Use when Codex needs to read an interview guide, protocol, or activity list and build a reusable spreadsheet scaffold before quantitative coding, frequency ranking, or downstream use with interview-quant-coding-skill.
- `discovery-catalog`: Resolve, explain, and maintain the UXR team's template/skill catalog so agents and MCP-like callers can consistently find the right research skill without duplicating work.
- `executive-one-pager-skill`: Compress a report, analysis output, or project-related material into an executive-facing narrative in the team's preferred structure mode (timeline narrative, conclusion-first/Minto, or RQ-first), then render it as one-pager copy, an intro summary slide outline, or an executive-summary section draft. Most commonly this summarizes an already-written report, but it can also work directly from analysis content or project files when no full report exists yet or one isn't needed. Use when Codex needs to produce an executive one-pager or executive-summary section.
- `followup-implementation-tracker`: Track research follow-up and implementation review cycles: read final, survey, and interview reports to extract improvement proposals with source anchors, build a fixed-status review workbook the researcher fills in, and produce companion review summaries. Use when Codex needs to manage post-research follow-up on design or product changes, especially to build a review checklist from reports, send proposal feedback, review whether recommendations were implemented, or summarize what changed after research.
- `interview-interim-report-writer`: Turn qualitative interview coding output into a formal interview interim report — Executive Summary, research overview, topic-grouped claim-sentence insights with representative quotes, an improvement-direction section, and an appendix — matching the team's real interview interim report structure. Use when Codex needs to draft or update a document-style interview interim report from coded interview findings, as distinct from an interview results dashboard or a quick-summary artifact.
- `interview-quant-coding-skill`: Convert interview free responses into fixed-tag quantitative coding workbooks by building per-question true-false matrices, frequency rankings, insight tabs, and optional scoring-based participant segments. Use when Codex needs to transform qualitative interview answers into structured question-level coding sheets or participant scoring outputs for comparison and summary.
- `interview-results-dashboard`: Turn interview coding outputs into dashboard-style synthesis artifacts by combining participant profile views, cross-interview theme summaries, and optional issue-catalog packaging. Use when Codex needs to convert qualitative interview findings, coding workbooks, or quick-summary notes into a shareable interview results dashboard, quick summary table, or reusable component and issue library before executive one-pagers or report writing.
- `persona-generator-skill`: Generate evidence-based persona workbooks by turning synthesized UXR findings into structured persona profiles with core demographics, About, Goals, Frustrations, and optional extended trait fields. Use when Codex needs to create a persona artifact from analyzed survey, interview, app-review, or mixed-method research outputs, especially in the team's workbook format.
- `qual-thematic-coding-skill`: Analyze interview transcripts through qualitative thematic coding by extracting core themes, pain points, workarounds, emotional moments, and surprises; structuring them into the team Context-Content-Group schema; then synthesizing patterns across interviews and clustering them into affinity groups. Use when Codex needs to turn one or more interview transcripts into thematic coding files, cross-interview synthesis, or an affinity mapping report before dashboarding or executive reporting.
- `recruiting-list-legend-generator`: Generate usage and legend sheets for recruiting rosters, participant-profile workbooks, and screener handoff files. Use when Codex needs to inspect a recruiting workbook and explain file purpose, stage, columns, PID conventions, and stage-specific flow before recruiting, screening, or transcript linkage.
- `research-plan-writer-skill`: Turn a research brief, business question, or planning notes into a structured UX research plan with optional RQ and RH framing, repeated method blocks, timeline, deliverables, and team-style formal tone. Use when Codex needs to draft or refine a research plan, protocol overview, or planning brief before questionnaire or interview design.
- `research-qa-skill`: Review research questionnaires, survey forms, and interview guides for bias, mapping gaps, domain-risk issues, and editing defects. Use when Codex needs to quality-check an instrument before fieldwork with a fixed checklist, severity labels, and Hana-finance-specific guardrails.
- `survey-analysis-verification`: Verify survey analysis outputs before reporting by checking N counts, exclusion rules, stale-data risk, AI-generated claims, low-base handling, and the mapping from RQ or RH to findings. Use when Codex needs to compare survey findings against source data, cleaned inputs, basic-stats outputs, or plan-level RH sheets before dashboards, reports, or stakeholder readouts are finalized.
- `survey-basic-stats-analysis`: Analyze cleaned survey datasets by producing question-level descriptive statistics, respondent-versus-response percentages, Likert summary metrics such as mean, standard deviation, and top-box or bottom-box summaries, plus a RH-based hypothesis tracker with methods, decisions, and insights. Use when Codex needs to turn cleaned survey data (.xlsx, .xls, .csv) into analysis-ready stats sheets or a basic survey findings workbook for UXR reporting.
- `survey-data-preprocessing`: Prepare raw survey exports for analysis by detecting survey schema, preserving team missing-value conventions, normalizing wide-format multi-select or ranked questions, generating a cleaned dataset plus codebook or variable ledger, and enforcing a human review gate before downstream analysis. Use when Codex needs to convert raw survey response files (.csv, .xlsx, .xls) into analysis-ready survey data.
- `survey-interim-report-writer`: Turn validated survey analysis outputs into a formal survey interim report that preserves key metrics, base counts, competitive or driver evidence, and a bridge to the next interview phase. Use when Codex needs to draft or refine a document-style survey interim report from verified survey findings, update an existing interim report by appending a new latest version, or generate a polished markdown draft before producing a docx draft.
- `survey-open-ended-coding-skill`: Turn open-ended survey responses into structured coding workbooks by generating draft codebooks, applying 1-3 codes per response, summarizing code frequencies, extracting representative quotes, and flagging surprises or outliers. Use when Codex needs to analyze free-text survey responses from .xlsx, .xls, .csv, or extracted response tables for UXR reporting.
- `survey-results-dashboard`: Turn validated survey analysis outputs into dashboard artifacts by separating a researcher workbench from a stakeholder-facing report, while preserving low-base warnings, segment cross-tabs, and AI insight guardrails. Use when Codex needs to build a survey dashboard or reporting view from cleaned survey stats, RH trackers, or verified analysis workbooks.
- `template-hygiene-checker`: Inspect reusable UXR template files and skill-pack artifacts for leftover real project data, confidential identifiers, unresolved comments, placeholders, and editing residue before team reuse or distribution. Report findings first; do not modify originals by default.
- `transcript-anonymizer-skill`: 리서처가 익명화한 UX 리서치 데이터(전사본, 설문 응답, 리크루팅 명단)를 검사해 익명화되지 않고 남은 개인식별정보(PII)의 위치를 알려주는 스킬입니다. 치환은 하지 않습니다 — 익명화는 리서처가 직접 수행합니다.
- `transcript-pipeline-skill`: Wrap transcript cleanup and anonymization into one safe workflow. Use when Codex needs to process transcript-like .xlsx, .xls, or .csv files end-to-end by running transcript-verification-enhancer first, then transcript-anonymizer-skill, while preserving the source file and producing both _cleaned and _pipeline_completed outputs.
- `transcript-verification-enhancer`: UX 리서치 인터뷰 전사본(STT)의 정확도 검증, 화자 턴 분리, 오타 교정 및 가독성을 향상시키는 스킬입니다.
