# ChatGPT 계열 Project 어댑터

ChatGPT 계열 도구는 로컬 coding agent처럼 slash command 설치를 직접 지원하지 않을 수 있다.

먼저 실행:

```bat
adapters\chatgpt\generate_project_instructions.bat
```

생성된 `CHATGPT_PROJECT_INSTRUCTIONS.md`를 project/custom GPT instructions로 사용한다. 로컬 파일을 직접 읽을 수 없는 환경이라면 MCP 서버를 함께 연결한다.
