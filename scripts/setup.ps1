# PowerShell launcher for the backend on Windows.
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\backend")

if (-not (Test-Path ".\.venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt | Out-Null
if (-not (Test-Path ".\.env")) {
    Copy-Item .\.env.example .\.env
    Write-Host "Created .env from template — edit it with your real secrets."
}

python .\scripts\seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
