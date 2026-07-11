#!/usr/bin/env bash
# Dev launcher. Source the venv and start uvicorn.
set -e
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
source .venv/bin/activate 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
