---
name: transcript-pipeline-skill
description: "Wrap transcript cleanup and anonymization into one safe workflow. Use when Codex needs to process transcript-like .xlsx, .xls, or .csv files end-to-end by running transcript-verification-enhancer first, then transcript-anonymizer-skill, while preserving the source file and producing both _cleaned and _pipeline_completed outputs."
---

# Transcript Processing Pipeline Skill

## Overview

Use this skill as a wrapper around the two existing child skills:
- `../transcript-verification-enhancer/SKILL.md`
- `../transcript-anonymizer-skill/SKILL.md`

Do not duplicate their detailed rules. Run cleanup first, then follow the anonymization approval checkpoint before writing the final output.

## Use this skill for

- `.xlsx`, `.xls`, or `.csv` files that contain transcripts, interview logs, or text-heavy research responses
- Requests such as "clean this transcript and anonymize it end-to-end" or "create both an intermediate cleaned file and a final anonymized file"

Do not use this skill when the user wants only cleanup or only anonymization. In those cases, use the child skill directly.

## Required preflight checks

1. Read `../transcript-verification-enhancer/SKILL.md` before step 1.
2. Read `../transcript-anonymizer-skill/SKILL.md` before step 2.
3. Never overwrite the source file.

## Workflow

### 1. Plan output paths

- Confirm the input file path and extension.
- Plan the intermediate output as `<base>_cleaned<ext>`.
- Plan the final output as `<base>_pipeline_completed<ext>`.
- Warn the user that an open workbook may force a timestamped fallback filename.

### 2. Run cleanup first

Always run the verification script with anonymization disabled:

```bash
python .agents/skills/transcript-verification-enhancer/scripts/batch_processor.py <input-file> --skip-anonymize [--model ...]
```

Why this matters:
- The child script can apply anonymization rules by default.
- This wrapper must preserve the explicit approval checkpoint required by the anonymizer skill.

If the script writes a fallback file such as `_cleaned_<epoch>`, carry that real path forward.

### 3. Prepare the anonymization plan

- Inspect the cleaned output for PII.
- Draft a PID mapping proposal for participant names, labels, and aliases.
- Report any moderator names, school names, company names, phone numbers, or addresses that need masking.
- Do not write the final anonymized file before the user approves the mapping.
- Preserve service names, brand names, and company names that are part of the research subject.

### 4. Apply anonymization after approval

- Apply only the approved PID mapping and anonymization rules.
- Keep the cleaned file as an intermediate artifact.
- Save the final result to `<base>_pipeline_completed<ext>`.
- Do not overwrite the source file or the cleaned file.
- Do not add extra rewriting, summarization, or paraphrasing beyond cleanup and anonymization.

### 5. Report completion

Return:
- the source path
- the actual cleaned output path
- the actual pipeline-completed output path
- a short cleanup summary
- a short anonymization summary
- any ambiguous items that still require human review

## Guardrails

- Never run the cleanup script without `--skip-anonymize`.
- Never finalize PID substitutions without user approval.
- Never anonymize service names, brand names, or company names that must stay literal.
- Never overwrite the source file.
- Always keep `_cleaned` and `_pipeline_completed` as separate files.
