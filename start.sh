#!/bin/bash
set -e

echo "==> Building React frontend..."
cd college-comparison-app
npm install
npm run build
cd ..

echo "==> Starting FastAPI backend..."
uvicorn ai-system-web.backend.app:app --host 0.0.0.0 --port ${PORT:-8000}
