# CXI Skill Pack 어댑터

이 폴더에는 AI agent별 설치/연결 도구가 들어 있다. 스킬 원본은 항상 `skills/{skill_id}/SKILL.md`이다.

agent가 custom slash command를 지원하면 아래처럼 직접 호출할 수 있다.

```text
/{skill_id}
```

자연어 요청은 `runtime/resolve_skill.py`로 먼저 어떤 스킬이 맞는지 찾은 뒤, resolved된 `SKILL.md`를 읽는다.

agent별 adapter 안에 스킬 내용을 복제하지 않는다. 스킬이 바뀌면 UXR-Template에서 package를 다시 만들고 cxi-skill-pack repo를 갱신한다.
