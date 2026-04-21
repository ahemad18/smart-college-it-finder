from __future__ import annotations

import csv
import logging
import os
import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "ontario_college_IT_programs_ONLY_DEDUP_COLLEGE_PROGRAM.csv"
)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

IT_KEYWORDS = {
    "computer",
    "information",
    "software",
    "network",
    "cyber",
    "security",
    "data",
    "ai",
    "analytics",
    "cloud",
    "it",
    "programming",
    "web",
    "systems",
    "database",
    "devops",
    "developer",
}

CLUSTERS = {
    "Cybersecurity": {"cyber", "security", "forensics", "risk"},
    "Data & AI": {"data", "analytics", "ai", "machine", "learning", "ml"},
    "Software Development": {"software", "programming", "developer", "web", "app"},
    "Cloud & DevOps": {"cloud", "devops", "infrastructure", "aws", "azure"},
    "Networks & Systems": {"network", "systems", "admin", "server"},
    "IT Support": {"support", "service", "helpdesk", "technician"},
}


class RecommendationRequest(BaseModel):
    education: str = Field(default="")
    skills: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    delivery_preference: Optional[str] = None
    region_preference: Optional[str] = None
    max_duration_years: Optional[float] = None
    limit: int = Field(default=10, ge=1, le=50)

logger = logging.getLogger("ai_system")


def normalize_text(value: Optional[str]) -> str:  # Normalize text for consistent matching.
    # Keeps comparisons case-insensitive and punctuation-agnostic.
    # Returns a trimmed string safe for tokenization.
    if not value:
        return ""
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def tokenize(value: Optional[str]) -> List[str]:  # Tokenize normalized text for matching.
    # Uses whitespace splitting for lightweight tokenization.
    # Ensures empty input results in an empty token list.
    text = normalize_text(value)
    if not text:
        return []
    return text.split()


def load_programs() -> List[Dict[str, str]]:  # Load and deduplicate CSV program records.
    # Verifies dataset presence before reading rows.
    # Deduplicates by composite key to avoid repeats.
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    records: List[Dict[str, str]] = []
    seen = set()
    try:
        with open(DATA_PATH, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = (
                    row.get("college_name"),
                    row.get("campus_name"),
                    row.get("program_name"),
                    row.get("program_code"),
                    row.get("intake_terms"),
                    row.get("start_date"),
                    row.get("delivery_format"),
                )
                if key in seen:
                    continue
                seen.add(key)
                records.append(row)
    except (csv.Error, OSError) as exc:
        raise RuntimeError("Failed to read dataset") from exc
    return records

LOAD_ERROR: Optional[str] = None
try:
    PROGRAMS = load_programs()
except Exception as exc:  # pragma: no cover - startup guard
    logger.exception("Failed to load dataset")
    PROGRAMS = []
    LOAD_ERROR = str(exc)

app = FastAPI(title="Ontario IT Program Recommendation API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_it_program(row: Dict[str, str]) -> bool:  # Detect IT-related programs via keywords.
    # Builds a combined text snapshot of program fields.
    # Checks tokens against a curated IT keyword list.
    combined = " ".join(
        [
            row.get("program_name", ""),
            row.get("program_category", ""),
            row.get("program_description", ""),
            row.get("program_tags", ""),
        ]
    )
    tokens = set(tokenize(combined))
    return any(keyword in tokens for keyword in IT_KEYWORDS)


def program_score(row: Dict[str, str], profile: RecommendationRequest) -> float:  # Score program fit for a profile.
    # Weights skills and goals more heavily than education.
    # Adds bonuses for delivery, region, and duration matches.
    combined = " ".join(
        [
            row.get("program_name", ""),
            row.get("program_description", ""),
            row.get("program_tags", ""),
            row.get("program_category", ""),
        ]
    )
    tokens = set(tokenize(combined))
    skill_tokens = {token for skill in profile.skills for token in tokenize(skill) if token}
    goal_tokens = {token for goal in profile.goals for token in tokenize(goal) if token}
    edu_tokens = set(tokenize(profile.education))

    score = 0.0
    score += sum(1 for token in skill_tokens if token in tokens) * 3
    score += sum(1 for token in goal_tokens if token in tokens) * 2
    score += sum(1 for token in edu_tokens if token in tokens)

    if profile.delivery_preference:
        delivery = normalize_text(row.get("delivery_format", ""))
        if normalize_text(profile.delivery_preference) in delivery:
            score += 2.5

    if profile.region_preference:
        region = normalize_text(row.get("region", ""))
        if normalize_text(profile.region_preference) in region:
            score += 2.0

    if profile.max_duration_years:
        duration_years = row.get("duration_years")
        try:
            duration_value = float(duration_years) if duration_years else None
        except ValueError:
            duration_value = None
        if duration_value is not None and duration_value <= profile.max_duration_years:
            score += 1.5

    return score


def ensure_dataset_loaded() -> None:  # Raise HTTP 500 if dataset failed to load.
    # Centralizes dataset availability checks for handlers.
    # Prevents downstream logic from running on empty data.
    if LOAD_ERROR:
        raise HTTPException(
            status_code=500,
            detail="Dataset failed to load. Check server logs for details.",
        )


@app.get("/api/health")
def health_check() -> Dict[str, str]:  # Report API status and dataset load state.
    # Returns status plus record count for monitoring.
    # Indicates whether the dataset load succeeded.
    return {
        "status": "ok" if not LOAD_ERROR else "error",
        "records": str(len(PROGRAMS)),
        "dataset_loaded": "false" if LOAD_ERROR else "true",
    }




@app.get("/api/colleges")
def list_colleges() -> List[str]:  # Return sorted college names for filters.
    # Ensures dataset availability before processing.
    # Normalizes missing names to "Unknown" for UI.
    try:
        ensure_dataset_loaded()
        colleges = sorted({row.get("college_name", "Unknown") for row in PROGRAMS})
        return colleges
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list colleges")
        raise HTTPException(status_code=500, detail="Unable to list colleges") from exc


@app.get("/api/programs")
def list_programs(
    query: Optional[str] = None,
    college: Optional[str] = None,
    category: Optional[str] = None,
    credential: Optional[str] = None,
    delivery: Optional[str] = None,
    region: Optional[str] = None,
    it_only: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Dict[str, object]:
    try:
        ensure_dataset_loaded()
        results = PROGRAMS

        if it_only:
            results = [row for row in results if is_it_program(row)]

        def match(value: Optional[str], target: str) -> bool:  # Match filters using normalized text.
            # Treats empty filter values as a match.
            # Uses normalized text for case-insensitive matching.
            if not value:
                return True
            return normalize_text(value) in normalize_text(target)

        filtered = []
        for row in results:
            if query:
                combined = " ".join(
                    [
                        row.get("program_name", ""),
                        row.get("program_description", ""),
                        row.get("program_category", ""),
                    ]
                )
                if normalize_text(query) not in normalize_text(combined):
                    continue
            if not match(college, row.get("college_name", "")):
                continue
            if not match(category, row.get("program_category", "")):
                continue
            if not match(credential, row.get("credential_type", "")):
                continue
            if not match(delivery, row.get("delivery_format", "")):
                continue
            if not match(region, row.get("region", "")):
                continue
            filtered.append(row)

        paged = filtered[offset : offset + limit]
        return {
            "total": len(filtered),
            "limit": limit,
            "offset": offset,
            "items": paged,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list programs")
        raise HTTPException(status_code=500, detail="Unable to load programs") from exc


@app.post("/api/recommendations")
def recommend_programs(request: RecommendationRequest) -> Dict[str, object]:  # Rank programs based on profile inputs.
    # Scores and sorts programs, then deduplicates repeats.
    # Falls back to generic IT programs if no match.
    try:
        ensure_dataset_loaded()
        candidates = [row for row in PROGRAMS if is_it_program(row)]
        scored: List[tuple[float, Dict[str, str]]] = []
        for row in candidates:
            score = program_score(row, request)
            if score > 0:
                scored.append((score, row))

        scored.sort(key=lambda item: item[0], reverse=True)

        # Deduplicate by college + program name to avoid repeated intakes
        unique: Dict[tuple[str, str], tuple[float, Dict[str, str]]] = {}
        for score, row in scored:
            key = (row.get("college_name", ""), row.get("program_name", ""))
            if key not in unique or score > unique[key][0]:
                unique[key] = (score, row)

        top = [
            {
                **row,
                "score": round(score, 2),
            }
            for score, row in sorted(
                unique.values(), key=lambda item: item[0], reverse=True
            )[: request.limit]
        ]

        if not top:
            fallback = [row for row in PROGRAMS if is_it_program(row)][: request.limit]
            top = [
                {
                    **row,
                    "score": 0.0,
                }
                for row in fallback
            ]

        return {
            "count": len(top),
            "recommendations": top,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to generate recommendations")
        raise HTTPException(status_code=500, detail="Unable to generate recommendations") from exc


@app.get("/api/search")
def search(query: str, limit: int = Query(default=6, ge=1, le=25)) -> Dict[str, object]:  # Search programs and colleges for the query.
    # Combines token matching with substring boosts.
    # Returns programs plus college summaries.
    try:
        ensure_dataset_loaded()
        normalized_query = normalize_text(query)
        if not normalized_query:
            return {"query": query, "programs": [], "colleges": []}

        query_tokens = set(tokenize(query))

        scored_programs: List[tuple[float, Dict[str, str]]] = []
        for row in PROGRAMS:
            combined = " ".join(
                [
                    row.get("program_name", ""),
                    row.get("program_description", ""),
                    row.get("program_tags", ""),
                    row.get("program_category", ""),
                    row.get("college_name", ""),
                    row.get("credential_type", ""),
                ]
            )
            tokens = set(tokenize(combined))
            score = sum(1 for token in query_tokens if token in tokens)
            if normalized_query in normalize_text(combined):
                score += 3
            if normalized_query in normalize_text(row.get("college_name", "")):
                score += 2
            if score > 0:
                scored_programs.append((float(score), row))

        scored_programs.sort(key=lambda item: item[0], reverse=True)
        unique_programs: Dict[tuple[str, str], tuple[float, Dict[str, str]]] = {}
        for score, row in scored_programs:
            key = (row.get("college_name", ""), row.get("program_name", ""))
            if key not in unique_programs or score > unique_programs[key][0]:
                unique_programs[key] = (score, row)

        programs = [
            {
                **row,
                "score": round(score, 2),
            }
            for score, row in sorted(
                unique_programs.values(), key=lambda item: item[0], reverse=True
            )[:limit]
        ]

        college_matches = []
        for college in sorted({row.get("college_name", "") for row in PROGRAMS}):
            if not college:
                continue
            college_normalized = normalize_text(college)
            if normalized_query in college_normalized or any(
                token in college_normalized for token in query_tokens
            ):
                summary = benchmark(college)
                college_matches.append(summary)

        return {
            "query": query,
            "programs": programs,
            "colleges": college_matches[:limit],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to search programs")
        raise HTTPException(status_code=500, detail="Unable to search programs") from exc


@app.get("/api/skill-clusters")
def skill_clusters() -> Dict[str, object]:  # Group IT programs into skill clusters.
    # Applies keyword sets to assign clusters.
    # Returns counts and sample program names.
    try:
        ensure_dataset_loaded()
        clusters = defaultdict(list)
        for row in PROGRAMS:
            if not is_it_program(row):
                continue
            combined = " ".join(
                [
                    row.get("program_name", ""),
                    row.get("program_description", ""),
                    row.get("program_tags", ""),
                ]
            )
            tokens = set(tokenize(combined))
            matched = False
            for cluster, keywords in CLUSTERS.items():
                if any(keyword in tokens for keyword in keywords):
                    clusters[cluster].append(row)
                    matched = True
            if not matched:
                clusters["General IT"].append(row)

        summary = {
            name: {
                "count": len(rows),
                "sample_programs": [r.get("program_name") for r in rows[:5]],
            }
            for name, rows in clusters.items()
        }
        return {"clusters": summary}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to build skill clusters")
        raise HTTPException(status_code=500, detail="Unable to load skill clusters") from exc


@app.get("/api/stats")
def stats() -> Dict[str, object]:  # Compute aggregate dashboard statistics.
    # Aggregates counts for charts and summaries.
    # Uses IT-only programs for consistency.
    try:
        ensure_dataset_loaded()
        category_counter = Counter()
        credential_counter = Counter()
        delivery_counter = Counter()
        region_counter = Counter()
        college_counter = Counter()
        level_counter = Counter()

        for row in PROGRAMS:
            if not is_it_program(row):
                continue
            category_counter[row.get("program_category", "Unknown") or "Unknown"] += 1
            credential_counter[row.get("credential_type", "Unknown") or "Unknown"] += 1
            delivery_counter[row.get("delivery_format", "Unknown") or "Unknown"] += 1
            region_counter[row.get("region", "Unknown") or "Unknown"] += 1
            college_counter[row.get("college_name", "Unknown") or "Unknown"] += 1
            level_counter[row.get("program_level", "Unknown") or "Unknown"] += 1

        return {
            "categories": category_counter.most_common(10),
            "credentials": credential_counter.most_common(10),
            "delivery": delivery_counter.most_common(10),
            "regions": region_counter.most_common(10),
            "top_colleges": college_counter.most_common(10),
            "levels": level_counter.most_common(10),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to build stats")
        raise HTTPException(status_code=500, detail="Unable to load stats") from exc


@app.get("/api/benchmark")
def benchmark(college: str) -> Dict[str, object]:  # Summarize totals and categories for a college.
    # Computes totals for all and IT-only programs.
    # Returns top IT categories for benchmarking.
    try:
        ensure_dataset_loaded()
        college_programs = [row for row in PROGRAMS if row.get("college_name") == college]
        it_programs = [row for row in college_programs if is_it_program(row)]
        return {
            "college": college,
            "total_programs": len(college_programs),
            "it_programs": len(it_programs),
            "top_categories": Counter(
                row.get("program_category", "Unknown") or "Unknown" for row in it_programs
            ).most_common(5),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to build benchmark")
        raise HTTPException(status_code=500, detail="Unable to load benchmark") from exc


@app.get("/api/compare-colleges")
def compare_colleges(colleges: str = Query(..., description="Comma-separated college names")) -> Dict[str, object]:
    """Return side-by-side comparison data for 2–5 colleges from the live dataset."""
    try:
        ensure_dataset_loaded()
        names = [c.strip() for c in colleges.split(",") if c.strip()]
        if len(names) < 2:
            raise HTTPException(status_code=400, detail="Provide at least 2 college names")

        _flexible = {"Part Time", "Online", "Hybrid", "Distance Education", "Blended"}

        results = []
        all_categories: set = set()
        for name in names:
            progs = [r for r in PROGRAMS if r.get("college_name") == name]
            it_progs = [r for r in progs if is_it_program(r)]
            cat_counts = Counter(r.get("program_category", "Other") or "Other" for r in it_progs)
            cred_counts = Counter(r.get("credential_type", "Other") or "Other" for r in it_progs)
            delivery_counts = Counter(r.get("delivery_format", "Other") or "Other" for r in it_progs)
            all_categories.update(cat_counts.keys())
            flexible_count = sum(
                cnt for fmt, cnt in delivery_counts.items()
                if any(f.lower() in (fmt or "").lower() for f in _flexible)
            )
            flexible_pct = round(flexible_count / len(it_progs) * 100) if it_progs else 0
            durations = [
                float(r["duration_months"])
                for r in it_progs
                if r.get("duration_months") and str(r["duration_months"]).replace(".", "", 1).isdigit()
            ]
            avg_duration = round(sum(durations) / len(durations)) if durations else 0
            total = len(progs)
            results.append({
                "college": name,
                "total_programs": total,
                "it_programs": len(it_progs),
                "it_pct": round(len(it_progs) / total * 100) if total else 0,
                "category_count": len(cat_counts),
                "credential_count": len(cred_counts),
                "flexible_pct": flexible_pct,
                "avg_duration_months": avg_duration,
                "categories": dict(cat_counts.most_common(8)),
                "credentials": dict(cred_counts),
                "delivery": dict(delivery_counts),
            })
        return {"colleges": results, "all_categories": sorted(all_categories)}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to compare colleges")
        raise HTTPException(status_code=500, detail="Unable to compare colleges") from exc


@app.get("/api/policy")
def policy_overview() -> Dict[str, object]:  # Aggregate IT program supply by region.
    # Counts IT programs per region for policy views.
    # Returns a note describing the aggregation logic.
    try:
        ensure_dataset_loaded()
        region_counter = Counter()
        for row in PROGRAMS:
            if not is_it_program(row):
                continue
            region = row.get("region") or "Unknown"
            region_counter[region] += 1

        return {
            "supply_by_region": region_counter.most_common(),
            "note": "Supply counts represent unique IT programs per region.",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to build policy overview")
        raise HTTPException(status_code=500, detail="Unable to load policy overview") from exc


if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

