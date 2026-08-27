# Changelog — qual-thematic-coding-skill

이 파일은 스킬의 **동작(SKILL.md/references)이 실제 검증 세션에서 어떻게 바뀌어왔는지**를 기록한다. 이 스킬은 재사용 코드(scripts/)가 없고 SKILL.md/references 자체가 "코드"이므로, 여기서는 워크플로우·가드레일 변경만 기록한다.

## 기록 규칙

- 새 항목은 파일 맨 위에 추가한다(최신이 위).
- 각 항목: `## YYYY-MM-DD — 한 줄 요약` + `- 계기:` + `- 변경:` + `- 검증:` + `- 남은 일:`

---

## 2026-08-19 — RQ 대조 사후 점검에서 발견한 갭을 SKILL.md 가드레일로 반영

- 계기: 사용자가 "25.S.BIZMOB" 검증 결과에 대해 "RQ에 따라 분석되었는가?"를 질문 — 확인해보니 이 스킬의 상향식(bottom-up) 워크플로우 특성상 공식 RQ 리스트를 애초에 대조하지 않았음을 발견.
- 변경: SKILL.md의 "3. Synthesize across interviews" 단계에 "프로젝트에 RQ 리스트가 있으면 synthesis 완료 후 대조하라"는 가드레일을 추가(아래 SKILL.md diff 참고). 상향식 코딩 자체는 유지하되, 마무리 단계에서 RQ 커버리지를 사후 확인하는 절차를 명시함.
- 검증: `validation_runs/qual-thematic-coding-skill/2026-08-19_25.S.BIZMOB/05_rq_alignment_check.md` — 이 절차를 실제로 적용해 RQ 5개 중 2개(벤치마킹, 동일조직 대표-직원 비교)가 데이터로 메울 수 없는 진짜 갭임을 확인.
- 남은 일: RQ 리스트가 없는 프로젝트(예: GBIUX)에서는 이 가드레일이 적용되지 않음 — RQ 문서 자체가 없는 경우의 대체 절차(연구 목적 요약과 대조)는 아직 정의 안 됨.
