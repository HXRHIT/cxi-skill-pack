# Codex 중복 스킬 표시 정리 가이드

Codex에서 `/스킬명`을 입력했을 때 같은 스킬이 2개씩 보이면, 보통 같은 스킬이 여러 discovery 경로에 동시에 있기 때문이다.

## 가장 흔한 원인

- 현재 작업 repo의 `.agents/skills/*`에 프로젝트 스킬이 있다.
- 동시에 `~/.codex/skills/*`에 개인 설치 스킬이 있다.
- 이전 버전 설치로 긴 canonical skill 폴더가 남아 있고, 새 버전 alias wrapper도 설치되어 있다.

즉 중복은 보통 스킬 내용이 2번 배포된 문제가 아니라, Codex가 같은 스킬을 두 위치에서 발견하는 문제다.

## 권장 운영

개발자는 `cxi-template/.agents/skills/*`를 사용한다.

팀원은 `cxi-skill-pack`을 clone한 뒤, 짧은 alias wrapper만 Codex 개인 스킬 폴더에 설치한다.

짧은 명령 예시:

- `/app-review`
- `/survey-stats`
- `/survey-clean`
- `/transcript-pii`
- `/transcript-clean`
- `/research-plan`
- `/research-qa`
- `/discover`

## 정리 전 확인

PowerShell에서 개인 Codex 스킬 폴더를 확인한다.

```powershell
$skills = Join-Path $HOME ".codex\skills"
Get-ChildItem $skills -Directory | Select-Object Name
```

긴 이름과 짧은 이름이 같이 있으면 긴 이름 쪽이 이전 설치본일 가능성이 높다.

예:

```text
app-review-analysis-pipeline
app-review
survey-basic-stats-analysis
survey-stats
transcript-anonymizer-skill
transcript-pii
```

## 안전한 정리 방법

`cxi-skill-pack` 폴더에서 alias mode로 다시 설치하면서 긴 legacy 폴더를 제거한다.

```powershell
cd C:\Users\hanati\Documents\GitHub\cxi-skill-pack
adapters\codex\install_to_codex.bat --remove-legacy
```

이 명령은 `manifest.json`에 등록된 긴 canonical skill 폴더만 제거하고, 짧은 alias wrapper를 다시 만든다.

## 수동 정리 방법

자동 정리가 불안하면 긴 이름 폴더만 직접 지운다.

```powershell
$skills = Join-Path $HOME ".codex\skills"
Remove-Item -LiteralPath "$skills\app-review-analysis-pipeline" -Recurse
Remove-Item -LiteralPath "$skills\survey-basic-stats-analysis" -Recurse
Remove-Item -LiteralPath "$skills\transcript-anonymizer-skill" -Recurse
```

수동 삭제는 필요한 폴더 이름을 정확히 확인한 뒤 진행한다.

## 주의할 점

- `cxi-template` repo 안에서 작업할 때는 프로젝트 스킬과 개인 스킬이 동시에 보일 수 있다.
- 일반 팀원이 `cxi-template` repo를 열지 않고 자기 프로젝트에서 작업하면 중복 노출 가능성이 낮다.
- 중복이 보이면 짧은 명령을 우선 선택한다.
- 스킬 원본 수정은 `cxi-template`에서 하고, 개인 Codex 스킬 폴더에서는 직접 수정하지 않는다.
