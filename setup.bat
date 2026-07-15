@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo [SETUP] Preparing Panchayat AI for this Windows computer...
where powershell.exe >nul 2>nul || (
  echo [ERROR] Windows PowerShell is required for the one-time setup.
  pause
  exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap-windows.ps1" -RepositoryRoot "%CD%" || goto :failed
if not exist ".tools\runtime.cmd" goto :failed
call ".tools\runtime.cmd"

if not defined PYTHON_EXE goto :failed
if not defined NODE_EXE goto :failed
if not defined NPM_CMD goto :failed
"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" || goto :failed
"%NODE_EXE%" -e "process.exit(Number(process.versions.node.split('.')[0]) >= 20 ? 0 : 1)" || goto :failed

if not exist "backend\.venv\Scripts\python.exe" (
  echo [SETUP] Creating the Python environment...
  "%PYTHON_EXE%" -m venv "backend\.venv" || goto :failed
)

echo [SETUP] Updating Python packaging tools...
"backend\.venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip setuptools wheel || goto :failed

echo [SETUP] Installing backend dependencies...
"backend\.venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r "backend\requirements.txt" || goto :failed

if not exist "backend\.env" copy /y "backend\.env.example" "backend\.env" >nul
if not exist "frontend-web\.env" copy /y "frontend-web\.env.example" "frontend-web\.env" >nul

echo [SETUP] Installing web dependencies...
pushd "frontend-web"
if exist "node_modules" (
  call "%NPM_CMD%" install --no-audit --no-fund || (popd & goto :failed)
) else if exist "package-lock.json" (
  call "%NPM_CMD%" ci --no-audit --no-fund || (popd & goto :failed)
) else (
  call "%NPM_CMD%" install --no-audit --no-fund || (popd & goto :failed)
)
popd

echo [SETUP] Preparing the development database...
pushd "backend"
".venv\Scripts\python.exe" "scripts\migrate.py"
if errorlevel 1 (
  echo.
  echo [RECOVERY] The existing local SQLite database is from a failed or incompatible setup.
  echo [RECOVERY] It will be backed up before a clean development database is created.
  ".venv\Scripts\python.exe" "scripts\rebuild_dev_database.py" || (popd & goto :failed)
  ".venv\Scripts\python.exe" "scripts\migrate.py" || (popd & goto :failed)
)
".venv\Scripts\python.exe" "scripts\seed.py" || (popd & goto :failed)
popd

echo.
echo [READY] One-time setup completed successfully.
echo From now on, use start.bat to launch Panchayat AI quickly.
pause
exit /b 0

:failed
echo.
echo [ERROR] Setup could not be completed. Review the first error above.
echo Existing database files are never discarded without a backup.
pause
exit /b 1
