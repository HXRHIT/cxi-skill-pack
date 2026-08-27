# CXI Skill Pack 어댑터

이 폴더에는 AI agent별 설치/연결 도구가 들어 있다. 스킬 원본은 항상 `skills/{skill_id}/SKILL.md`이다.

agent가 custom slash command를 지원하면 아래처럼 직접 호출할 수 있다.

```text
/{shortName}
```

예: `/app-review`, `/survey-stats`, `/transcript-pii`

자연어 요청은 `runtime/resolve_skill.py`로 먼저 어떤 스킬이 맞는지 찾은 뒤, resolved된 `SKILL.md`를 읽는다.

긴 canonical skill ID는 내부 추적과 호환성을 위해 유지한다. 팀원이 직접 입력하는 명령은 짧은 `shortName`을 우선 사용한다.
