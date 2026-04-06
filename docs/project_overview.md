# Project Overview (Easy Read)

## What this project does
- Helps users explore Ontario IT programs and get recommendations.
- Uses a FastAPI backend to serve program data and recommendation logic.
- Uses a static frontend (HTML/CSS/JS) to show dashboards, charts, and forms.

## Folder structure (main parts)
- ai-system-web/
  - backend/: FastAPI API server (Python)
  - frontend/: Static web UI (HTML, CSS, JS)
  - docs/: Project docs for the web app
- data/: Raw dataset files (CSV)
- docs/: High-level project docs

## Backend (ai-system-web/backend)
- app.py: Main API server.
- requirements.txt: Python dependencies.
- Key API endpoints:
  - GET /api/health: Health check.
  - GET /api/colleges: List of colleges.
  - GET /api/programs: Search/filter programs.
  - POST /api/recommendations: Recommendations for a student profile.
  - GET /api/skill-clusters: Program clusters.
  - GET /api/stats: Summary statistics.
  - GET /api/benchmark: College benchmark summary.
  - GET /api/policy: Regional supply summary.

## Frontend (ai-system-web/frontend)
- index.html: Page layout and sections.
- styles.css: Dark theme styling and layout.
- app.js: Fetches data from the backend and updates the UI.
- Features on the page:
  - Student recommendations form.
  - Skill clusters (advisor view).
  - College benchmarking.
  - Recruiter insights.
  - Policy analysis.
  - Data explorer.
  - Dashboard charts.
  - Olivia chatbot (simple rule-based assistant).

## Dataset
- Main dataset file is stored at the project root:
  - ontario_college_IT_programs_ONLY_DEDUP_COLLEGE_PROGRAM.csv
- The backend reads this file at startup.

## How it works (simple flow)
1. Backend loads the CSV dataset and prepares filters.
2. Frontend calls API endpoints to fetch lists and stats.
3. User submits the recommendation form.
4. Backend scores programs and returns top matches.
5. Frontend renders results in cards and tables.

## How to run locally
- Start backend (serves API + frontend):
  - URL: http://localhost:8000
- The frontend is served from the same address by the backend.

## Notes
- The current implementation is rule-based (keyword matching + scoring).
- It does not use ML training or embeddings.
