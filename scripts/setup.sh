#!/usr/bin/env bash
# POSIX launcher for the backend.
set -euo pipefail
cd "$(dirname "$0")/../backend"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python scripts/seed.py
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
