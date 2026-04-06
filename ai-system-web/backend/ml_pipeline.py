"""
ml_pipeline.py  –  Machine learning layer for Ontario IT Program Recommender
============================================================================
Phase 2 ML components (replaces / augments the rule-based keyword engine):

  1. TF-IDF vectorization of program descriptions
  2. KMeans clustering (data-driven, k=7) to replace hand-coded CLUSTERS
  3. Cosine-similarity recommendations (profile text vs program TF-IDF vectors)
  4. NLP skill extraction – top TF-IDF terms per program
  5. Model evaluation – silhouette score, cluster label mapping

All models are fitted once at import time and kept in memory.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

logger = logging.getLogger("ai_system.ml")

MLFLOW_EXPERIMENT_NAME = "ontario-it-program-recommender"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_CLUSTERS = 7          # number of data-driven program clusters
N_TOP_SKILLS = 10       # skill terms extracted per program
MIN_DESCRIPTION_LEN = 5 # minimum tokens to include a program in ML corpus
RANDOM_STATE = 42

# Stopwords tuned for our domain (extends sklearn's built-in English set)
EXTRA_STOPWORDS = {
    "program", "programs", "students", "student", "course", "courses",
    "college", "ontario", "learn", "learning", "skills", "skill",
    "will", "including", "include", "study", "provide", "use", "used",
    "diploma", "certificate", "degree", "graduate", "technology",
    "information", "apply", "applied", "introduction", "advanced",
    "management", "business", "work", "working", "field", "year",
    "years", "month", "months", "cover", "covered", "topics", "topic",
    "design", "designed", "industry", "focus", "areas", "area",
    "understand", "ability", "theoretical", "practical",
}

# Friendly display labels assigned to each KMeans cluster by inspecting its
# top TF-IDF terms.  Built automatically in `_label_clusters()`.
CLUSTER_THEME_HINTS: Dict[int, List[str]] = {
    0: ["cybersecurity", "security", "forensics", "ethical", "hacking"],
    1: ["data", "analytics", "machine", "learning", "artificial", "intelligence"],
    2: ["software", "development", "programming", "web", "app", "mobile"],
    3: ["cloud", "devops", "infrastructure", "aws", "azure", "docker"],
    4: ["network", "networking", "cisco", "router", "wireless", "server"],
    5: ["database", "sql", "oracle", "data", "administration"],
    6: ["it", "support", "helpdesk", "technician", "service", "desktop"],
}


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def _clean(text: Optional[str]) -> str:
    """Lower-case, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _program_document(row: Dict[str, str]) -> str:
    """Build a single text document for a program row."""
    parts = [
        row.get("program_name", ""),
        row.get("program_description", ""),
        row.get("program_category", ""),
        row.get("program_tags", ""),
    ]
    return _clean(" ".join(p for p in parts if p))


# ---------------------------------------------------------------------------
# Model state (populated by `fit`)
# ---------------------------------------------------------------------------

class MLPipeline:
    """Holds all fitted ML artefacts for programmatic use."""

    def __init__(self) -> None:
        self.is_fitted: bool = False
        self.programs: List[Dict[str, str]] = []
        self.documents: List[str] = []
        self.valid_indices: List[int] = []  # indices into self.programs with valid docs

        # Sklearn objects
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None            # sparse (n_valid_programs, n_features)
        self.tfidf_dense = None             # dense numpy array
        self.kmeans: Optional[KMeans] = None
        self.labels: Optional[np.ndarray] = None  # cluster label per valid program

        # Derived data
        self.cluster_names: Dict[int, str] = {}     # cluster_id → human label
        self.cluster_top_terms: Dict[int, List[str]] = {}  # cluster_id → top terms
        self.program_skills: Dict[int, List[str]] = {}     # valid_idx → extracted skills
        self.silhouette: Optional[float] = None
        self.feature_names: List[str] = []
        self._top_global_terms: List[str] = []
        self.mlflow_run_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    def fit(self, programs: List[Dict[str, str]]) -> None:
        """Fit TF-IDF + KMeans on the supplied program list."""
        self.programs = programs

        # Build corpus (only programs with enough text)
        docs: List[str] = []
        valid: List[int] = []
        for idx, row in enumerate(programs):
            doc = _program_document(row)
            if len(doc.split()) >= MIN_DESCRIPTION_LEN:
                docs.append(doc)
                valid.append(idx)

        if len(docs) < N_CLUSTERS:
            logger.warning(
                "ML pipeline: corpus too small (%d docs). Falling back to rule-based.", len(docs)
            )
            return

        self.documents = docs
        self.valid_indices = valid

        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        with mlflow.start_run() as run:
            self.mlflow_run_id = run.info.run_id

            # --- Log parameters ---
            mlflow.log_params({
                "n_clusters": N_CLUSTERS,
                "random_state": RANDOM_STATE,
                "tfidf_max_features": 2000,
                "tfidf_min_df": 2,
                "tfidf_max_df": 0.85,
                "tfidf_ngram_range": "(1, 2)",
                "kmeans_n_init": 10,
                "kmeans_max_iter": 300,
                "corpus_size": len(docs),
                "total_programs": len(programs),
            })

            # --- TF-IDF ---
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                min_df=2,
                max_df=0.85,
                ngram_range=(1, 2),
                stop_words="english",
            )
            # Manually add extra stopwords after fitting vocab
            self.tfidf_matrix = self.vectorizer.fit_transform(docs)
            self.tfidf_dense = self.tfidf_matrix.toarray()
            self.feature_names = self.vectorizer.get_feature_names_out().tolist()

            # --- KMeans ---
            n_clusters = min(N_CLUSTERS, len(docs) - 1)
            self.kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=RANDOM_STATE,
                n_init=10,
                max_iter=300,
            )
            self.labels = self.kmeans.fit_predict(self.tfidf_matrix)

            # --- Evaluation ---
            try:
                self.silhouette = float(
                    silhouette_score(self.tfidf_matrix, self.labels, metric="cosine")
                )
            except Exception:
                self.silhouette = None

            # --- Cluster metadata ---
            self._build_cluster_metadata(n_clusters)

            # --- Per-program skill extraction ---
            self._extract_program_skills()

            # --- Top global terms (by mean TF-IDF across corpus, filtering stopwords) ---
            mean_tfidf = np.asarray(self.tfidf_matrix.mean(axis=0)).flatten()
            top_global_idx = mean_tfidf.argsort()[::-1]
            self._top_global_terms = [
                self.feature_names[i]
                for i in top_global_idx
                if self.feature_names[i] not in EXTRA_STOPWORDS
                and len(self.feature_names[i]) > 2
            ][:30]

            # --- Log metrics ---
            mlflow.log_metrics({
                "silhouette_score": self.silhouette if self.silhouette is not None else -1.0,
                "inertia": float(self.kmeans.inertia_),
                "vocabulary_size": float(len(self.feature_names)),
                "actual_n_clusters": float(n_clusters),
            })

            # --- Log cluster sizes ---
            for name, count in {
                self.cluster_names.get(int(lbl), f"Cluster {lbl}"): 0
                for lbl in self.labels
            }.items():
                pass  # sizes logged below
            cluster_sizes: Dict[str, int] = {}
            for lbl in self.labels:
                name = self.cluster_names.get(int(lbl), f"Cluster {lbl}")
                cluster_sizes[name] = cluster_sizes.get(name, 0) + 1
            for cname, ccount in cluster_sizes.items():
                safe_name = re.sub(r"[^a-zA-Z0-9_./ -]", "", cname.replace("&", "and")).replace(" ", "_")
                mlflow.log_metric(f"cluster_size_{safe_name}", float(ccount))

            # --- Log models ---
            mlflow.sklearn.log_model(self.kmeans, artifact_path="kmeans_model")
            mlflow.sklearn.log_model(self.vectorizer, artifact_path="tfidf_vectorizer")

            self.is_fitted = True
            logger.info(
                "ML pipeline fitted: %d programs, %d clusters, silhouette=%.3f, mlflow_run_id=%s",
                len(docs),
                n_clusters,
                self.silhouette if self.silhouette is not None else float("nan"),
                self.mlflow_run_id,
            )

    # ------------------------------------------------------------------
    # Cluster metadata
    # ------------------------------------------------------------------

    def _build_cluster_metadata(self, n_clusters: int) -> None:
        """Derive human-readable names and top terms for each cluster."""
        centers = self.kmeans.cluster_centers_  # (n_clusters, n_features)
        used_names: Dict[str, int] = {}
        for cid in range(n_clusters):
            top_indices = centers[cid].argsort()[::-1][:15]
            top_terms = [self.feature_names[i] for i in top_indices]
            self.cluster_top_terms[cid] = top_terms
            base_name = self._label_cluster(cid, top_terms)
            # Make names unique if the same theme appears in multiple clusters
            if base_name in used_names:
                used_names[base_name] += 1
                unique_name = f"{base_name} ({used_names[base_name]})"
            else:
                used_names[base_name] = 1
                unique_name = base_name
            self.cluster_names[cid] = unique_name

    def _label_cluster(self, cid: int, top_terms: List[str]) -> str:
        """Assign a human-readable label based on top TF-IDF terms."""
        theme_scores: Dict[str, int] = {
            "Cybersecurity":        0,
            "Data & AI":            0,
            "Software Development": 0,
            "Cloud & DevOps":       0,
            "Networks & Systems":   0,
            "Database & Systems":   0,
            "IT Support":           0,
        }
        keyword_map = {
            "Cybersecurity":        {"cyber", "security", "forensic", "ethical", "hack", "penetration", "vulnerability"},
            "Data & AI":            {"data", "analytic", "machine", "learning", "artificial", "intelligence", "ai", "ml", "deep", "neural"},
            "Software Development": {"software", "developer", "programming", "web", "app", "mobile", "java", "python", "agile", "scrum"},
            "Cloud & DevOps":       {"cloud", "devops", "aws", "azure", "docker", "kubernetes", "infrastructure", "automation", "ci", "cd"},
            "Networks & Systems":   {"network", "cisco", "router", "wireless", "tcp", "ip", "switching", "wan", "lan"},
            "Database & Systems":   {"database", "sql", "oracle", "mysql", "nosql", "administration", "dba"},
            "IT Support":           {"support", "helpdesk", "technician", "desktop", "service", "hardware", "troubleshoot"},
        }
        for term in top_terms:
            for theme, keywords in keyword_map.items():
                if any(kw in term for kw in keywords):
                    theme_scores[theme] += 1

        best = max(theme_scores, key=lambda t: theme_scores[t])
        if theme_scores[best] == 0:
            return f"IT Cluster {cid + 1}"
        return best

    # ------------------------------------------------------------------
    # Skill extraction
    # ------------------------------------------------------------------

    def _extract_program_skills(self) -> None:
        """Store top TF-IDF terms for each program as extracted skills."""
        for local_idx, global_idx in enumerate(self.valid_indices):
            vec = self.tfidf_dense[local_idx]
            top_term_indices = vec.argsort()[::-1][:N_TOP_SKILLS]
            skills = [self.feature_names[i] for i in top_term_indices if vec[i] > 0]
            self.program_skills[global_idx] = skills

    def get_program_skills(self, global_idx: int) -> List[str]:
        """Return extracted skills for a program (by its index in self.programs)."""
        return self.program_skills.get(global_idx, [])

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def recommend(
        self,
        profile_text: str,
        programs: List[Dict[str, str]],
        top_n: int = 10,
    ) -> List[Dict]:
        """
        Score programs by cosine similarity between profile_text and TF-IDF vectors.

        Returns a list of dicts: {program fields} + ml_score + ml_cluster + ml_skills.
        """
        if not self.is_fitted or not profile_text.strip():
            return []

        profile_vec = self.vectorizer.transform([_clean(profile_text)])
        sim_scores = cosine_similarity(profile_vec, self.tfidf_matrix).flatten()

        # Map valid_index → program global_index → score
        scored: List[Tuple[float, int]] = []  # (score, global_idx)
        for local_idx, global_idx in enumerate(self.valid_indices):
            scored.append((float(sim_scores[local_idx]), global_idx))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate (college + program_name)
        seen: Dict[Tuple[str, str], float] = {}
        for score, global_idx in scored:
            row = programs[global_idx]
            key = (row.get("college_name", ""), row.get("program_name", ""))
            if key not in seen or score > seen[key]:
                seen[key] = score

        deduped = sorted(seen.items(), key=lambda x: x[1], reverse=True)[:top_n * 3]

        results = []
        added_keys = set()
        for (college, prog_name), score in deduped:
            if len(results) >= top_n:
                break
            key = (college, prog_name)
            if key in added_keys:
                continue
            added_keys.add(key)

            # Find full row
            for local_idx, global_idx in enumerate(self.valid_indices):
                row = programs[global_idx]
                if row.get("college_name") == college and row.get("program_name") == prog_name:
                    cluster_id = int(self.labels[local_idx])
                    results.append({
                        **row,
                        "ml_score": round(score, 4),
                        "ml_cluster": self.cluster_names.get(cluster_id, f"Cluster {cluster_id}"),
                        "ml_skills": self.get_program_skills(global_idx),
                    })
                    break

        return results

    # ------------------------------------------------------------------
    # Cluster summary (for /api/ml-clusters endpoint)
    # ------------------------------------------------------------------

    def cluster_summary(self, programs: List[Dict[str, str]]) -> Dict:
        """Return cluster membership counts and sample programs."""
        if not self.is_fitted:
            return {}

        cluster_programs: Dict[int, List[Dict]] = defaultdict(list)
        for local_idx, global_idx in enumerate(self.valid_indices):
            cid = int(self.labels[local_idx])
            cluster_programs[cid].append(programs[global_idx])

        summary = {}
        for cid, rows in sorted(cluster_programs.items()):
            name = self.cluster_names.get(cid, f"Cluster {cid}")
            summary[name] = {
                "cluster_id": cid,
                "count": len(rows),
                "top_terms": self.cluster_top_terms.get(cid, [])[:8],
                "sample_programs": [
                    {
                        "program_name": r.get("program_name"),
                        "college_name": r.get("college_name"),
                        "credential_type": r.get("credential_type"),
                    }
                    for r in rows[:5]
                ],
            }
        return summary

    # ------------------------------------------------------------------
    # Model evaluation report
    # ------------------------------------------------------------------

    def evaluation_report(self) -> Dict:
        """Return key model evaluation metrics."""
        if not self.is_fitted:
            return {"status": "not_fitted"}

        # Inertia and cluster sizes
        cluster_sizes: Dict[str, int] = {}
        for local_idx, label in enumerate(self.labels):
            name = self.cluster_names.get(int(label), f"Cluster {label}")
            cluster_sizes[name] = cluster_sizes.get(name, 0) + 1

        return {
            "status": "fitted",
            "programs_in_corpus": len(self.documents),
            "n_clusters": self.kmeans.n_clusters,
            "silhouette_score": round(self.silhouette, 4) if self.silhouette is not None else None,
            "inertia": round(float(self.kmeans.inertia_), 2),
            "cluster_sizes": cluster_sizes,
            "vocabulary_size": len(self.feature_names),
            "top_global_terms": self._top_global_terms[:20],
            "mlflow_run_id": self.mlflow_run_id,
            "mlflow_experiment": MLFLOW_EXPERIMENT_NAME,
        }


# ---------------------------------------------------------------------------
# Module-level singleton (instantiated when app.py imports this module)
# ---------------------------------------------------------------------------

pipeline = MLPipeline()
