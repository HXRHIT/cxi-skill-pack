# Codex 어댑터

clone 또는 압축 해제한 `cxi-skill-pack` 폴더에서 실행한다.

```bat
adapters\codex\install_to_codex.bat
```

기본값은 짧은 alias wrapper를 `%CODEX_HOME%\skills` 또는 `~/.codex/skills`에 만든다.

예: `/app-review`, `/survey-stats`, `/transcript-pii`

다른 위치에 설치하려면:

```bash
python adapters/codex/install_to_codex.py --target C:/path/to/skills
```

기존처럼 긴 canonical skill 폴더를 그대로 복사하려면:

```bash
python adapters/codex/install_to_codex.py --mode copy
```

이전 설치로 긴 skill 폴더가 남아 있다면 먼저 결과의 `legacySkillDirsStillPresent`를 확인한다. 삭제까지 하려면 명시적으로 `--remove-legacy`를 붙인다.
