# Template hygiene taxonomy

Use this taxonomy to classify reusable UXR template artifacts before reuse or distribution.

## Scope boundary

Template hygiene checks reusable artifacts such as deck templates, document templates, workbook templates, website catalog files, and skill-pack artifacts.

It does not replace participant-data anonymization. If the primary artifact is a transcript, survey response dataset, recruiting roster, or raw participant table, use `transcript-anonymizer-skill`.

## Categories

| category | severity default | meaning | recommended action |
|---|---:|---|---|
| `direct_pii` | critical | names, phone, email, account-like numbers, resident-ID-like patterns, personal IDs | remove from reusable artifact; escalate if source was intended as public template |
| `secret_or_token` | critical | API keys, access tokens, private keys, passwords, `.env` values | revoke or rotate if real; remove immediately |
| `real_project_identifier` | high | real service/project/org/location/date left in a template | replace with placeholder after owner review |
| `internal_path` | high | local user paths, drive paths, internal repository paths in shared package | replace with portable relative paths |
| `comment_unresolved` | high | comments about N mismatch, quote reliability, verification incomplete, data issue | preserve as evidence and route to responsible researcher |
| `placeholder_conflict` | medium | placeholders and real-looking values coexist in same artifact | clarify whether file is a template or example |
| `editing_residue` | medium | TODO, FIXME, repeated "내용", dummy sections, duplicate headings | clean in copy after review |
| `broken_text` | medium | mojibake, encoding artifacts, unreadable labels | repair from source if possible |
| `weak_dummy_text` | low | obvious harmless filler text | clean opportunistically |

## Detection notes

- Dates alone are not always sensitive. Raise severity when a date appears near a project, service, location, participant, or research-event label.
- Organization names can be legitimate domain context. Raise severity when the file is a generic reusable template but contains a specific past project context.
- Comments are not trash by default. Some comments encode verification warnings and should be preserved until resolved.
- Generated reports should distinguish `evidence_text` from `recommendation`; do not silently rewrite evidence.

## Report fields

Use these fields in CSV/JSON reports:

- `file`
- `location`
- `category`
- `severity`
- `evidence`
- `recommendation`
- `rule_id`

## Release gate

A reusable template or skill-pack artifact should not be distributed while it has unresolved `critical` findings. `high` findings require owner review. `medium` and `low` findings can be bundled only if they are documented and accepted.
