# Application Documentation (Points)

## Backend: app.py
- FastAPI service exposing recommendation, analytics, and lookup endpoints for Ontario IT programs.
- Loads and de-duplicates the CSV dataset from data/raw/ontario_college_programs.csv.
- Normalizes and tokenizes text for filtering and scoring.
- Detects IT-related programs using keyword matching.
- Ranks programs with a weighted scoring model using skills, goals, education, delivery, region, and duration.
- Provides endpoints for health check, colleges list, programs search, recommendations, clusters, stats, benchmarking, and policy overview.
- Enables CORS for all origins to support the frontend.

## Frontend: app.js
- Handles navigation scroll and section activation for the single-page UI.
- Fetches data from the backend API and renders cards, tables, charts, and summaries.
- Builds recommendation results, clusters, benchmarks, policy insights, and data explorer tables.
- Manages chart rendering with Chart.js and updates existing charts efficiently.
- Implements form handling for recommendations and filters for program search.
- Powers the Olevia chatbot with quick replies and data-backed suggestions.
- Handles error states and user feedback messages.

## Frontend: index.html + styles.css
- Defines the single-page layout with sections for recommendations, advisor view, benchmarking, recruiter insights, policy analysis, explorer, and dashboard.
- Provides accessible UI elements, multi-select controls, and chatbot panel structure.
- Styles a modern, dark-themed interface with cards, grids, charts, and navigation pills.
- Includes responsive layout rules for different screen sizes.
- Applies consistent typography, colors, spacing, and component states.
