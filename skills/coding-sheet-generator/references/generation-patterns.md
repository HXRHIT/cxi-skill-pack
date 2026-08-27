# Generation patterns for coding-sheet-generator

## 1. Observed packaging rule

Two packaging styles commonly appear in interview coding work:
- per-activity workbooks with separate question files and supporting summary sheets
- per-round workbooks with several activity tabs plus participant or note-taking support sheets

Default pattern:
- one workbook per round or guide
- one sheet group per activity
- split-per-activity output only when the existing study already treats each activity as a standalone deliverable or the user explicitly requests it

## 2. Header and row rule

- use PID or participant id as the stable row key
- place segment fields, demographics, or group fields immediately to the left of the coded activity columns
- use human-readable option labels as column headers
- keep question numbers in sheet titles and major headings

## 3. Activity layout patterns

### Binary or multi-select label activity

Common for adjective cards, variant preference reasons, image choices, or feature picks.
Recommended sheet pattern:
- optional raw or source sheet
- matrix sheet with PID rows and label columns
- optional concat helper column
- count or ranking sheet
- optional insight sheet

### Likert or rating activity

- store one record per participant per item, or one participant row with many item columns, depending on the source instrument
- include an explicit score column or one-hot score columns when the team needs formula compatibility
- include summary output for means, ranks, or per-segment comparison

### Ranking activity

- use participant rows and item columns with numeric ranks
- add summary output for average rank, median, top group, or label band
- add optional segment comparison when group fields exist

### Short open-response battery

- use one participant per row
- use one response column per sub-question
- keep question ids in headers
- reserve paired matrix or insight tabs when later coding is expected

## 4. Summary sheet rule

Common summary tabs include:
- insight summary
- count or ranking summary
- segment comparison
- participant roster or note-taking support

Do not create every possible tab by default.
Generate only the sheets supported by the activity type.

## 5. Compatibility with interview-quant-coding-skill

- this skill builds the scaffold
- interview-quant-coding-skill fills matrices, rankings, and scoring outputs
- keep stable sheet names and avoid renaming tabs after coding starts
- prefer workbook names such as `coding-workbook.xlsx` or `round##_coding-workbook.xlsx`
- if split delivery is requested, use names such as `Q##_coding-workbook.xlsx`

## 6. Boundary rule

- use this skill for workbook structure generation
- use `$interview-quant-coding-skill` for filling true-false matrices, frequency rankings, or participant scoring
- use `$qual-thematic-coding-skill` for open theme discovery
- use survey skills for survey exports rather than interview activity scaffolds