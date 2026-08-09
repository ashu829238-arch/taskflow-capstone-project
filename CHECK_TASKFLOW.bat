@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run START_TASKFLOW.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe check_algorithms.py
.venv\Scripts\python.exe benchmark.py
pause
