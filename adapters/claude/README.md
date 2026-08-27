# Claude 계열 slash command 어댑터

clone 또는 압축 해제한 `cxi-skill-pack` 폴더에서 실행한다.

```bat
adapters\claude\install_slash_commands.bat
```

기본값은 command 파일을 `~/.claude/commands/uxr`에 만든다.

사용하는 agent의 command 위치가 다르면:

```bash
python adapters/claude/install_slash_commands.py --commands-dir C:/path/to/commands/uxr
```

생성된 command 파일은 이 skill pack의 `skills/{skill_id}/SKILL.md`를 읽도록 안내한다.

팀원이 직접 입력할 때는 짧은 명령을 우선 사용한다.

예: `/uxr:app-review`, `/uxr:survey-stats`, `/uxr:transcript-pii`
