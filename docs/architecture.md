# Ontario IT Program Recommendation Platform - System Architecture

## Overview
End-to-end AI-powered platform for personalized IT program recommendations for Ontario colleges.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Web Scrapers  →  Raw Data  →  Data Validation  →  Processed    │
│  (Selenium)        (JSONL)      (Pydantic)          (Parquet)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│  NLP Skill Extraction  →  Text Embeddings  →  Feature Store     │
│  (spaCy + Regex)          (TF-IDF/SBERT)      (Pandas/Parquet)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ML MODELING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Clustering         Classification       Recommendation          │
│  (KMeans)          (RandomForest/XGB)    (Cosine Similarity)    │
│  Program Groups    User Preference       Top-N Matches          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  REST API  →  Streamlit Dashboard  →  Tableau Analytics         │
│  (FastAPI)     (User Interface)         (Insights)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       MLOPS LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Model Registry  →  Monitoring  →  Version Control  →  CI/CD    │
│  (MLflow)          (Logs/Metrics)   (DVC/Git)         (GitHub)  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Ingestion Layer
**Purpose**: Collect, validate, and store program data from Ontario colleges

**Components**:
- **Web Scrapers**: Selenium-based scrapers for college websites
- **Raw Storage**: JSONL files for raw scraped data
- **Validation**: Pydantic models for schema enforcement
- **Processed Storage**: Parquet files for efficient storage

**Technologies**: Python, Selenium, Pydantic, Pandas

### 2. Feature Engineering Layer
**Purpose**: Extract meaningful features from raw program descriptions

**Components**:
- **NLP Skill Extraction**: Extract technical skills, tools, and technologies
  - Pattern matching for common IT skills
  - Named Entity Recognition (NER) for technologies
  - Keyword extraction using TF-IDF
  
- **Text Embeddings**: Convert text to numerical vectors
  - TF-IDF for baseline (lightweight)
  - Sentence-BERT for semantic embeddings (optional)
  
- **Feature Store**: Centralized feature storage
  - Program features: skills, difficulty, duration, credentials
  - User features: interests, background, career goals

**Technologies**: spaCy, scikit-learn, sentence-transformers, Pandas

### 3. ML Modeling Layer

#### 3.1 Clustering (Unsupervised)
**Purpose**: Group similar programs for better navigation

**Algorithm**: KMeans (k=5-10 clusters)
**Features**: 
- Skill vectors (TF-IDF)
- Program type (diploma/certificate/degree)
- Duration, credential level

**Output**: Program clusters (e.g., "Web Development", "Data Science", "Cybersecurity")

#### 3.2 Classification (Supervised)
**Purpose**: Predict user fit and success probability

**Algorithms**: 
- RandomForest (interpretable, feature importance)
- XGBoost (higher accuracy, handles imbalanced data)

**Features**:
- User background (education, experience)
- Program requirements
- Skill gap analysis

**Output**: 
- Match score (0-100)
- Success probability
- Feature importance (why this program?)

#### 3.3 Recommendation Engine
**Purpose**: Generate personalized top-N program recommendations

**Approach**: Hybrid Recommender
1. **Content-Based**: Cosine similarity between user profile and program vectors
2. **Collaborative**: Implicit feedback from user interactions (optional)
3. **Ranking**: Combine similarity scores with classification predictions

**Formula**:
```
Final Score = α × Cosine Similarity + β × Classification Score + γ × Popularity
```

**Technologies**: scikit-learn, numpy, scipy

### 4. Application Layer

#### 4.1 REST API (FastAPI)
**Endpoints**:
- `POST /api/v1/recommend` - Get personalized recommendations
- `GET /api/v1/programs` - List all programs with filters
- `GET /api/v1/programs/{id}` - Program details
- `POST /api/v1/feedback` - Capture user feedback
- `GET /api/v1/clusters` - Get program clusters

#### 4.2 Streamlit Dashboard
**Features**:
- User profile input form
- Interactive recommendation results
- Program comparison tool
- Skill gap visualizations
- College/program filters

#### 4.3 Tableau Analytics
**Dashboards**:
- Program distribution by college/type
- Popular skills heatmap
- User engagement metrics
- Model performance tracking

### 5. MLOps Layer

#### 5.1 Model Versioning
**Tool**: MLflow + DVC

**Tracked Artifacts**:
- Model weights (.pkl files)
- Feature engineering pipelines
- Training/test datasets
- Hyperparameters
- Performance metrics

#### 5.2 Monitoring
**Metrics**:
- **Model Performance**: Accuracy, precision, recall, F1, AUC
- **Recommendation Quality**: NDCG, MRR, Hit Rate @ K
- **Data Quality**: Null rates, outliers, distribution shifts
- **System Health**: API latency, error rates, throughput

**Tools**: 
- Python logging
- Custom metrics dashboard (Streamlit)
- MLflow tracking server

#### 5.3 CI/CD Pipeline
**GitHub Actions Workflow**:
1. Lint code (flake8, black)
2. Run unit tests (pytest)
3. Validate data schemas
4. Train models on new data (weekly)
5. Compare model performance
6. Auto-deploy if metrics improve

## Data Flow

```
1. Raw Data Collection
   ontario_college_programs.csv → Raw storage

2. Data Validation & Cleaning
   Validate schema → Remove duplicates → Handle missing values

3. Feature Extraction
   Extract skills → Generate embeddings → Create feature vectors

4. Model Training
   Train clustering → Train classifier → Validate performance

5. Model Serving
   Load models → API endpoint → Return recommendations

6. User Interaction
   User inputs → Feature engineering → Predict → Return results

7. Feedback Loop
   Capture feedback → Retrain models → Update predictions
```

## Deployment Strategy

### Local Development
- Virtual environment (venv)
- SQLite for metadata
- Local Streamlit server

### Production (Future)
- Docker containers
- PostgreSQL database
- Cloud hosting (AWS/Azure)
- Redis for caching
- Load balancer for API

## Security & Privacy
- No PII collection (anonymous usage)
- API rate limiting
- Input validation and sanitization
- Secure model storage

## Scalability Considerations
- Batch prediction for all programs
- Caching frequent queries
- Incremental model updates
- Horizontal scaling for API

## Success Metrics

### Business Metrics
- User engagement rate
- Recommendation click-through rate
- User satisfaction scores
- Program application conversions

### Technical Metrics
- API response time < 200ms (p95)
- Model accuracy > 85%
- Recommendation relevance (NDCG@10 > 0.7)
- Data pipeline success rate > 99%

## Timeline (8-week sprint)

**Week 1-2**: Data ingestion, validation, schema design
**Week 3-4**: Feature engineering, NLP skill extraction
**Week 5-6**: ML models (clustering, classification, recommendation)
**Week 7**: Dashboard and API development
**Week 8**: MLOps setup, testing, deployment

## Team Roles
- **Data Engineer**: Scraping, pipeline, validation
- **ML Engineer**: Feature engineering, model training, MLOps
- **Full-Stack Developer**: API, dashboard, integration
- **Data Analyst**: EDA, visualization, Tableau dashboards
