@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul || (
  echo [ERROR] Python 3.11 or newer is required and was not found in PATH.
  pause
  exit /b 1
)
where npm.cmd >nul 2>nul || (
  echo [ERROR] Node.js and npm are required and were not found in PATH.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [SETUP] Creating the Python environment...
  python -m venv "backend\.venv" || goto :failed
  "backend\.venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt" || goto :failed
)

if not exist "backend\.env" copy /y "backend\.env.example" "backend\.env" >nul
if not exist "frontend-web\.env" copy /y "frontend-web\.env.example" "frontend-web\.env" >nul

if not exist "frontend-web\node_modules" (
  echo [SETUP] Installing web dependencies...
  pushd "frontend-web"
  call npm.cmd ci || (popd & goto :failed)
  popd
)

echo [SETUP] Preparing the development database...
pushd "backend"
".venv\Scripts\python.exe" "scripts\migrate.py" || (popd & goto :failed)
".venv\Scripts\python.exe" "scripts\seed.py" || (popd & goto :failed)
popd

echo [START] Backend: http://localhost:8000/docs
start "Smart Society Backend" cmd /k "cd /d ""%~dp0backend"" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [START] Web app: http://localhost:5173
start "Smart Society Web" cmd /k "cd /d ""%~dp0frontend-web"" && npm.cmd run dev"

timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"
exit /b 0

:failed
echo.
echo [ERROR] Setup failed. Review the message above, then run start.bat again.
pause
exit /b 1
