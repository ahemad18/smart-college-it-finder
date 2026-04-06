# Interim Report
## AI-Powered Comparison of IT Programs Across Ontario Colleges

---

**Course:** Capstone Project  
**Group:** 3  
**Date:** March 8, 2026  

**Team Members:**
- Amit Sharma
- Ahemadashraf Pathan
- Sahil Varudi
- Sahil Jajadiya
- Deepesh Dixit

**Supervisor / Faculty Advisor:** *(Insert name)*

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Introduction and Background](#2-introduction-and-background)
3. [Project Objectives](#3-project-objectives)
4. [Work Completed to Date](#4-work-completed-to-date)
5. [Technical Implementation Details](#5-technical-implementation-details)
6. [Challenges and How We Addressed Them](#6-challenges-and-how-we-addressed-them)
7. [Work Remaining](#7-work-remaining)
8. [Timeline and Milestones](#8-timeline-and-milestones)
9. [Individual Contributions](#9-individual-contributions)
10. [Conclusion](#10-conclusion)

---

## 1. Executive Summary

This is the interim report for our Capstone project, "AI-Powered Comparison of IT Programs Across Ontario Colleges." In short — we're building a web platform where students, advisors, recruiters, and policy people can look up, compare, and get recommendations for IT programs at Ontario colleges.

We've made a lot of progress. The dataset is collected and cleaned (3,273 records across 26 colleges), we've done a full EDA, the backend API is up and running with eight endpoints, and the entire frontend is functional. Right now the recommendation engine is rule-based — it scores programs based on keyword matching against a student's input — which honestly works better than we expected as a first version.

What's still left is the machine learning side: replacing the keyword scorer with trained models (KMeans clustering and a Random Forest or XGBoost classifier), adding proper NLP-based skill extraction, writing tests, and finishing all the documentation before the final submission.

---

## 2. Introduction and Background

When we first sat down to pick a project, one thing that frustrated all of us was how hard it is to actually compare IT programs across Ontario colleges. Each college has its own website, its own way of describing programs, and there's no single place to see them side by side. A student who wants to know "what's the difference between Seneca's cybersecurity diploma and George Brown's?" has to open five tabs and still won't get a clean answer.

That's the problem we're trying to fix. Ontario has 24 publicly funded colleges, and between them they offer hundreds of technology-related programs — diplomas, certificates, graduate certificates, even bachelor's degrees. The programs differ in length, credential level, delivery format, the specific skills they focus on, and where they're offered. For a student fresh out of high school or looking to upskill, navigating that is genuinely confusing.

The same problem shows up in a different form for academic advisors. They counsel students every day but don't always have a straightforward way to see how programs are clustered by skill set — so if a student says "I want to go into cloud computing," the advisor has to rely on memory or manual searching to suggest options. Recruiters have their own version of the problem: they want to know which colleges are producing graduates with specific technical skills, and that information just isn't compiled anywhere.

Our project tries to solve all of this in one place. The idea is a platform that doesn't just list programs but actually understands a user's profile and helps them make a decision — whether that user is a student, an advisor, a recruiter, or a policy analyst tracking regional skill supply.

---

## 3. Project Objectives

When we scoped the project in Milestone 1, we landed on seven main things we wanted the platform to do:

1. Build out a proper dataset of Ontario IT programs — not just names and colleges, but credential type, duration, delivery format, region, and especially program descriptions.
2. Build a recommendation engine that takes a student's background and goals and returns a ranked list of programs that actually fit them.
3. Create an advisor-facing view where programs are grouped by skill cluster, so advisors can quickly see what's available in, say, cybersecurity or data analytics.
4. Let colleges benchmark themselves against each other — comparing things like how many programs they offer, what credentials they lead to, and what skills they cover.
5. Give recruiters a way to search by skill keyword and see which colleges produce the most programs tagged with that skill.
6. Show a policy-level view of how IT program supply is distributed across regions, which could be useful for anyone thinking about gaps in Ontario's tech education landscape.
7. Package all of this in a browser-based web app that's straightforward to use, not just a proof-of-concept notebook.

---

## 4. Work Completed to Date

### 4.1 Data Collection and Preparation

Everything in this project starts with the data, so this was the first thing we tackled. We pulled program information from individual Ontario college websites and the Ontario Colleges central listing portal. Getting it all into a consistent shape took more effort than we expected — the raw data had a lot of inconsistencies that needed sorting out (more on that in the Challenges section).

After combining the sources, we deduplicated using a composite key: college name + campus + program name + program code + intake term + start date. The final dataset:

| Attribute | Value |
|---|---|
| Total programs (after dedup) | **3,273** |
| Colleges covered | **26** |
| Credential types | 8 |
| Columns per record | 14 |

The 14 fields we kept for each program: `college_name`, `campus_name`, `program_name`, `credential_type`, `credential_group`, `duration_months`, `duration_years`, `program_category`, `delivery_format`, `source_url`, `details_url`, `program_level`, `program_length`, and `program_description`.

The `program_description` column is the one we're most interested in going forward — it's the raw material for the NLP skill extraction we're planning next.

### 4.2 Exploratory Data Analysis

Once the data was clean, we did a full EDA pass in a Jupyter notebook. A few things stood out:

- Diplomas and Graduate Certificates make up the bulk of IT offerings. Bachelor's degrees exist but are relatively rare.
- Most programs are full-time and in-person, though there's a decent chunk that's online or hybrid — more than we expected.
- Duration is all over the place. Short certificates can be done in under a year; some bachelor's programs run to four years. The median sits around two years.
- Program descriptions are really inconsistent. Some colleges write detailed paragraphs about learning outcomes; others just list course names. That variability will need preprocessing before any NLP model is applied.
- Colleges in the GTA — Seneca, George Brown, Centennial, Humber — offer noticeably more IT programs than colleges in smaller cities. That geographic concentration shows up clearly in the data.
- A lot of rows had "Not Available" in the duration fields, which we had to decide how to handle.

### 4.3 System Architecture Design

We spent time early on thinking about how to structure the project so different pieces could be built in parallel. We landed on four layers:

- **Data Ingestion** — scraping, validation, and cleaning into a structured CSV/Parquet format
- **Feature Engineering** — extracting skills from program descriptions using NLP (spaCy + TF-IDF), generating feature vectors
- **ML Modeling** — KMeans for grouping programs, Random Forest / XGBoost for student-program fit scoring, and a cosine similarity recommender that pulls it together
- **Application** — FastAPI backend with a REST API, browser-based frontend on top

The layering was intentional. It meant the data team could work without blocking the backend developer, and the frontend could be built against a working API before the ML models were ready.

### 4.4 Backend API Development

The backend is a FastAPI app in `app.py`. It reads the CSV at startup, filters to IT-related programs, and exposes these eight endpoints:

| Endpoint | Method | What it does |
|---|---|---|
| `/api/health` | GET | Confirms the server is running |
| `/api/colleges` | GET | List of all colleges in the dataset |
| `/api/programs` | GET | Searchable, filterable program list |
| `/api/recommendations` | POST | Takes a student profile, returns ranked programs |
| `/api/skill-clusters` | GET | Programs grouped by skill area |
| `/api/stats` | GET | Counts, breakdowns, summary numbers |
| `/api/benchmark` | GET | College-level comparison data |
| `/api/policy` | GET | Regional program supply breakdown |

**How recommendations currently work:** The `/api/recommendations` endpoint takes a student's education level, listed skills, career goals, preferred delivery format, preferred region, and maximum duration. For each program it computes a score: skill keyword matches count for 3 points each, goal matches for 2, education fit for 1, with smaller bonuses for delivery, region, and duration preferences. The top-N results come back ranked by that total.

It's not machine learning — it's a weighted keyword counter. But it gives reasonable results for typical inputs and was fast to implement, which let us get the UI working early. Replacing this with proper ML scoring is the main goal of the next phase.

One practical thing: the backend also serves the frontend static files, so the whole application runs from a single `uvicorn` command. No separate web server needed.

### 4.5 Frontend Web Application

The frontend is a single HTML page — no framework, just HTML, CSS, and JavaScript. We kept it simple on purpose. The JS side fetches from the backend and updates the page dynamically.

What's working in the UI right now:

- **Recommendations form** — enter your background and goals, get back a ranked list of programs as cards
- **Skill clusters view** — programs organized by track (Cybersecurity, Data & AI, Software Dev, Cloud & DevOps, Networks, IT Support), useful for advisors
- **Benchmarking table** — colleges compared side by side: program counts, credential mix, skill coverage
- **Recruiter view** — type a skill keyword, see which colleges have the most matching programs
- **Policy charts** — regional breakdown of where programs are concentrated
- **Data explorer** — sortable, filterable table of the full dataset
- **Dashboard** — bar and pie charts via Chart.js covering credentials, top colleges, and delivery formats
- **Olivia chatbot** — a rule-based assistant that helps users navigate the app and answers common questions using live data from the API

The UI runs on a dark theme. It's not flashy, but it loads quickly and handles all the main use cases.

---

## 5. Technical Implementation Details

### Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, FastAPI, Pydantic |
| Data handling | Pandas, Python's built-in CSV module |
| NLP (right now) | Regex and keyword matching |
| NLP (next) | spaCy, TF-IDF via scikit-learn |
| Frontend | Plain HTML5, CSS3, vanilla JavaScript |
| Charts | Chart.js |
| Version control | Git / GitHub |
| Project tracking | Jira |

### Dataset Loading

The CSV sits at the project root. The backend reads it once at startup, runs the IT keyword filter, and holds the filtered records in memory for the life of the process. This keeps response times consistent — there's no database hit per request.

### Scoring Formula

The current formula for each program:

```
Score = (skills_match × 3) + (goals_match × 2) + (education_match × 1)
      + delivery_bonus + region_bonus + duration_bonus
```

Programs scoring zero are excluded entirely, so results always have at least some relevance to the input.

### IT Keyword Filter

We filter to IT programs using 17 domain keywords checked against program names: "computer," "software," "network," "data," "cyber," "cloud," "programming," "web," "systems," and others in that category. The filter runs at load time, so the API only ever works with the relevant subset.

---

## 6. Challenges and How We Addressed Them

### Challenge 1: Colleges Don't Use the Same Vocabulary

This sounds minor, but it caused real headaches early on. One college writes "Full Time," another writes "Full-Time," a third writes "FT." Same issue with credential names, campus names, and program categories — every source had its own conventions.

We fixed it with a normalization function that runs on every string before comparison: lowercase, strip punctuation, collapse whitespace. Not glamorous, but it made matching work reliably across all 26 colleges.

### Challenge 2: Duration Data Was All Over the Place

A lot of records had "Not Available" in the `duration_months` and `duration_years` columns. We couldn't drop those rows — some were otherwise perfectly good programs. But we also couldn't fill in the durations without making things up.

The solution was to give those programs a neutral score on the duration component rather than penalizing them. They still show up in results if they match well on skills and goals, they just don't get the duration bonus.

### Challenge 3: Separating IT Programs from Everything Else

The raw dataset had programs from every faculty — business, health, hospitality, culinary. We needed only IT. Defining "IT" cleanly is harder than it sounds: "Computer Applications" is obviously IT; "Health Informatics" or "Digital Marketing" are borderline.

We iterated a few times on the keyword list and ended up with 17 terms. We validated the filter by manually checking a sample of what it included and excluded. It's not perfectly precise but it's consistent.

### Challenge 4: Frontend Without a Build System

We chose not to use React or any framework — no build pipeline, no node_modules, no bundler config. That paid off in simplicity but meant `app.js` grew pretty long as features were added.

We kept it manageable by splitting the file into sections with comment headers for each feature area. Each section follows the same fetch-then-render pattern. The backend serving static files directly also meant deployment stayed simple.

### Challenge 5: Coordinating Five People Across Multiple Components

Early on there were a couple of moments where API changes broke something on the frontend without anyone realizing until later. Five people working across data, backend, frontend, and docs needs more coordination than it might seem.

We got better at this by being more explicit about task ownership in Jira and communicating before merging anything that touched the API. Short check-ins at the start of each session helped more than we expected.

---

## 7. Work Remaining

### Machine Learning

The main remaining task is replacing the scoring engine with trained models:

- **KMeans clustering** on program feature vectors, to replace the six hand-defined skill clusters we have now. The idea is to let the data decide how programs group naturally.
- **Random Forest or XGBoost classifier** trained on student profile and program attribute pairs to predict fit score. We'll use synthetic or manually labeled profiles since we don't have real user interaction history.
- **Sentence-BERT embeddings** on program descriptions, if there's time — to see whether semantic similarity outperforms TF-IDF for the matching step.

### NLP Skill Extraction

Right now skill matching is just keyword overlap. What we want is spaCy pulling a structured list of skills out of each program description — "Python," "AWS," "network administration," "machine learning" — so the recommender can do a real skill-to-skill comparison.

### Model Evaluation

Once models exist, we need numbers:
- Clustering: silhouette score, manual cluster review
- Classifier: accuracy, precision, recall, F1, AUC on a held-out test set
- Recommendations: NDCG and hit rate at K using hand-crafted "gold standard" profiles

### Testing

Tests haven't been written yet. Before final submission we need unit tests per API endpoint, end-to-end tests for the recommendation flow, and edge case coverage (empty input, unknown region, extreme duration values).

### Final Documentation

The Swagger page auto-generates from FastAPI but needs proper schema descriptions. We also need an updated architecture diagram, a short user guide per persona, and of course the final report.

---

## 8. Timeline and Milestones

| Milestone | Status | Notes |
|---|---|---|
| Milestone 1 – Project Proposal | Completed | Scope agreed and approved |
| Milestone 2 – Epic Definition, Technical Planning | Completed | Architecture done, dataset collected |
| Data Collection and Cleaning | Completed | 3,273 records, 26 colleges |
| Exploratory Data Analysis | Completed | Notebook finished |
| Backend API (rule-based) | Completed | All 8 endpoints working |
| Frontend Web Application | Completed | All sections live |
| ML Model Development | In Progress | KMeans and classifier being built |
| NLP Skill Extraction | Not Started | Next sprint |
| Model Evaluation | Not Started | After model training |
| Testing | Not Started | Penultimate sprint |
| Final Report & Presentation | Not Started | End of semester |

---

## 9. Individual Contributions

| Team Member | Primary Responsibilities |
|---|---|
| Amit Sharma | Backend API, recommendation engine, overall architecture |
| Ahemadashraf Pathan | Data scraping, cleaning, EDA notebook |
| Sahil Varudi | Frontend JS — app.js, Chart.js, API integration |
| Sahil Jajadiya | Frontend structure and styling — index.html, styles.css |
| Deepesh Dixit | Documentation, Jira board management, ML research |

All five of us reviewed and tested each other's work throughout the sprints, so the lines aren't perfectly clean — but the table above captures who led each area.

---

## 10. Conclusion

Honestly, we're in a better place than we expected at this point. Coming into the project, building a full recommendation platform felt ambitious. What we have now — a working web app, a clean dataset, and a functional API — is a solid base to build the ML layer on top of.

That said, the next phase is the harder one. Rule-based scoring is forgiving to build; a properly trained and evaluated ML pipeline is not. We're being realistic about the time we have and have the remaining work tracked and broken down in Jira. If something has to be cut, semantic embeddings are the first thing to deprioritize.

The goal for the final submission is a platform that works well enough for someone to actually use it to make a real program decision. That's the bar we've set.

---

*Group 3 — Capstone Project, Semester 4 | Submitted: March 8, 2026*
