@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        TaskFlow - First Time Setup
echo ========================================

where py >nul 2>&1
if errorlevel 1 (
  echo Python is not installed or not available as 'py'.
  echo Please install Python 3.11+ and try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -m venv .venv
  if errorlevel 1 (
    echo Could not create the virtual environment.
    pause
    exit /b 1
  )
)

echo Installing/checking required packages...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package installation failed.
  pause
  exit /b 1
)

echo.
echo Starting backend...
start "TaskFlow Backend" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend...
start "TaskFlow Frontend" cmd /k "cd /d "%~dp0frontend" && ..\.venv\Scripts\python.exe -m http.server 5500"

timeout /t 2 /nobreak >nul

start "" "http://127.0.0.1:5500"

echo.
echo TaskFlow is starting.
echo Keep the two black command windows open while using the app.
echo Dashboard: http://127.0.0.1:5500
 echo Backend:   http://127.0.0.1:8000/docs
pause
