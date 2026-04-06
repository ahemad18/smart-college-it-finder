#!/bin/bash
set -e

echo "==> Starting FastAPI backend..."
cd "$(dirname "$0")"
uvicorn ai-system-web.backend.app:app --host 0.0.0.0 --port "${PORT:-8000}"
