# MCP 어댑터

이 starter는 도구 3개를 제공한다.

- `resolve_skill`
- `read_skill`
- `execute_skill`

필요 패키지 설치:

```bash
pip install mcp
```

실행:

```bash
python adapters/mcp/uxr_mcp_server.py
```

MCP server config를 받는 agent에서는 `mcp_config.example.json`을 시작점으로 사용한다.

기본값으로 `execute_skill`은 dry-run 모드다. 팀에서 안전 실행 규칙을 합의한 뒤 자주 쓰는 스킬부터 실제 runner를 붙인다.
