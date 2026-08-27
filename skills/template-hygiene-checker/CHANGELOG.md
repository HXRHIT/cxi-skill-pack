# Changelog — template-hygiene-checker

이 파일은 스킬의 동작 스키마(Skill.md)와 재사용 실행 코드(scripts/) 변경 이력을 관리한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다.
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`
- `scripts/`에 변경이 생기면 항상 기록한다.

---

## 2026-08-27 — #34 template-hygiene-checker 스킬 초안 작성

- 계기: 팀 공용 템플릿과 skill pack 배포 전 실제 프로젝트 값, 기밀 식별자, unresolved comment, 편집 잔재를 검사하는 report-first 스킬이 필요함
- 변경:
  - `.agents/skills/template-hygiene-checker/SKILL.md` 신규 작성
  - `references/hygiene-taxonomy.md` 신규 작성
  - `scripts/scan_template_hygiene.py` 신규 작성: 텍스트/Office XML 기반 보수적 hygiene scanner
- 검증: 미실행. 사용자가 검증을 요청하면 quick validation과 sample scan을 수행한다.
- 남은 일: 실제 팀 공용 템플릿 후보군으로 rule precision을 검증하고, cleaned copy 생성은 별도 승인 후 추가한다.
