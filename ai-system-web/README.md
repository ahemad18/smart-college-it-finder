# AI System Web (Ontario IT Program Recommendation Platform)

This web app delivers the Milestone 2 scope: AI-powered recommendations, advisor skill clusters, benchmarking, recruiter insights, policy analysis, and a dashboard built on the Ontario colleges dataset.

## Folder Structure
- backend/ - FastAPI backend for data access and recommendations
- frontend/ - Modern UI with charts and interactive filters
- data/raw/ - Dataset (already in the project root)

## Backend Setup
1. Create a virtual environment and install requirements:
   - `pip install -r ai-system-web/backend/requirements.txt`
2. Start the API server:
   - `uvicorn ai-system-web.backend.app:app --reload --port 8000`

## Frontend Setup
Open the HTML file directly in the browser:
- `ai-system-web/frontend/index.html`

If you want to use a local web server:
- `python -m http.server 5500` (run inside the frontend folder)

## API Endpoints
- `GET /api/health`
- `GET /api/colleges`
- `GET /api/programs`
- `POST /api/recommendations`
- `GET /api/skill-clusters`
- `GET /api/stats`
- `GET /api/benchmark`
- `GET /api/policy`

## Notes
- The backend filters only IT-related programs by default.
- The frontend assumes the backend runs on `http://localhost:8000`.
