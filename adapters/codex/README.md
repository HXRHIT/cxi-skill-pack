# Codex 어댑터

clone 또는 압축 해제한 `cxi-skill-pack` 폴더에서 실행한다.

```bat
adapters\codex\install_to_codex.bat
```

기본값은 모든 `skills/*` 폴더를 `%CODEX_HOME%\skills` 또는 `~/.codex/skills`로 복사한다.

다른 위치에 설치하려면:

```bash
python adapters/codex/install_to_codex.py --target C:/path/to/skills
```
