@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".tools\runtime.cmd" goto :not_ready
call ".tools\runtime.cmd"

if not exist "backend\.venv\Scripts\python.exe" goto :not_ready
if not exist "frontend-web\node_modules" goto :not_ready
if not exist "backend\.env" goto :not_ready
if not exist "frontend-web\.env" goto :not_ready

echo [START] Backend: http://localhost:8000/docs
start "Panchayat AI Backend" cmd /k "cd /d ""%~dp0backend"" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [START] Web app: http://localhost:5173
start "Panchayat AI Web" cmd /k "cd /d ""%~dp0frontend-web"" && npm.cmd run dev"

powershell.exe -NoLogo -NoProfile -Command "Start-Sleep -Seconds 2" >nul
start "" "http://localhost:5173"
exit /b 0

:not_ready
echo.
echo [NOT READY] This checkout has not been set up yet.
echo Run setup.bat once, wait for [READY], then run start.bat.
pause
exit /b 1
