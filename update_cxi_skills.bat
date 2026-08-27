@echo off
setlocal
if "%~1"=="" (
  echo Usage: update_cxi_skills.bat ^<latest-unpacked-cxi-skill-pack-folder^>
  exit /b 1
)
python "%~dp0runtime\check_updates.py" --remote-pack "%~1" --apply
