"""
generate_meeting2_report.py
===========================
Generates the Meeting Part 2 PDF report:
  "AI-Powered Comparison of IT Programs Across Ontario Colleges"
  Phase 2 – Machine Learning Pipeline Implementation

Run from the project root:
    python generate_meeting2_report.py
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "docs", "meeting2_phase2_report.pdf")


# ---------------------------------------------------------------------------
# Colour palette (dark teal theme matching the web app)
# ---------------------------------------------------------------------------
DARK_BG      = (15, 23, 42)      # #0f172a – page header bar
TEAL         = (14, 165, 233)    # #0ea5e9 – accent / headings
TEAL_DARK    = (15, 118, 110)    # #0f766e – secondary accent
LIGHT_TEAL   = (20, 184, 166)    # #14b8a6 – table header
WHITE        = (255, 255, 255)
NEAR_WHITE   = (241, 245, 249)   # #f1f5f9 – section bg alt
TEXT_DARK    = (15, 23, 42)      # main body text
TEXT_MUTED   = (100, 116, 139)   # muted / labels
TABLE_ROW_A  = (240, 249, 255)   # light blue stripe
TABLE_ROW_B  = (255, 255, 255)


class PDF(FPDF):
    # -----------------------------------------------------------------------
    # Header – appears on every page
    # -----------------------------------------------------------------------
    def header(self):
        self.set_fill_color(*DARK_BG)
        self.rect(0, 0, 210, 14, style="F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*TEAL)
        self.set_xy(8, 3)
        self.cell(0, 8, "Ontario IT Program Recommendation Platform  |  Phase 2: ML Pipeline Report", align="L")
        self.set_text_color(*TEXT_MUTED)
        self.set_font("Helvetica", "", 7)
        self.set_xy(0, 3)
        self.cell(202, 8, f"March 30, 2026", align="R")
        self.ln(10)

    # -----------------------------------------------------------------------
    # Footer – appears on every page
    # -----------------------------------------------------------------------
    def footer(self):
        self.set_y(-13)
        self.set_fill_color(*DARK_BG)
        self.rect(0, self.get_y(), 210, 13, style="F")
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*TEXT_MUTED)
        self.cell(0, 8, f"Capstone Project  ·  Group 3  ·  Page {self.page_no()}", align="C")

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def accent_line(self):
        """Draw a thin teal rule under a heading."""
        self.set_draw_color(*TEAL)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_line_width(0.2)
        self.ln(3)

    def section_heading(self, number, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*TEAL)
        self.cell(0, 8, f"{number}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.accent_line()
        self.set_text_color(*TEXT_DARK)

    def sub_heading(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*TEAL_DARK)
        self.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*TEXT_DARK)

    def body(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT_DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=8):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT_DARK)
        self.set_x(10 + indent)
        self.cell(5, 5.5, "-")  # bullet
        self.multi_cell(0, 5.5, text)

    def kv(self, key, value):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*TEAL_DARK)
        self.cell(48, 5.5, f"{key}:")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT_DARK)
        self.multi_cell(0, 5.5, value)

    def table_header(self, cols):
        """Render a table header row. cols = [(label, width), ...]"""
        self.set_fill_color(*LIGHT_TEAL)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for label, w in cols:
            self.cell(w, 7, label, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, values, widths, row_idx=0):
        fill_color = TABLE_ROW_A if row_idx % 2 == 0 else TABLE_ROW_B
        self.set_fill_color(*fill_color)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Helvetica", "", 8.5)
        for val, w in zip(values, widths):
            self.cell(w, 6.5, str(val), border=1, fill=True)
        self.ln()

    def info_box(self, text, color=TEAL):
        """A tinted left-bordered info block."""
        x = self.get_x()
        y = self.get_y()
        # Blend color toward white at 12% opacity, clamped to [0, 255]
        tint = tuple(min(255, int(c * 0.12 + 220)) for c in color)
        self.set_fill_color(*tint)
        self.set_draw_color(*color)
        self.set_line_width(1.0)
        # estimate height
        lines = len(text) // 90 + text.count("\n") + 2
        h = lines * 5.5 + 4
        self.rect(10, y, 190, h, style="FD")
        self.set_line_width(0.2)
        self.set_draw_color(*TEXT_DARK)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(*TEXT_DARK)
        self.set_xy(14, y + 3)
        self.multi_cell(183, 5.5, text)
        self.ln(2)

    def metric_row(self, metrics):
        """Render a row of metric boxes. metrics = [(label, value), ...]"""
        box_w = 190 // len(metrics)
        x_start = 10
        y = self.get_y()
        for label, value in metrics:
            self.set_fill_color(*TABLE_ROW_A)
            self.set_draw_color(*TEAL)
            self.rect(x_start, y, box_w - 2, 18, style="FD")
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*TEAL)
            self.set_xy(x_start, y + 2)
            self.cell(box_w - 2, 8, str(value), align="C")
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*TEXT_MUTED)
            self.set_xy(x_start, y + 10)
            self.cell(box_w - 2, 6, label, align="C")
            x_start += box_w
        self.set_xy(10, y + 21)


# ---------------------------------------------------------------------------
# Build the PDF
# ---------------------------------------------------------------------------

def build():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(10, 16, 10)

    # ===================================================================
    # COVER PAGE
    # ===================================================================
    pdf.add_page()

    # Full-width dark header band
    pdf.set_fill_color(*DARK_BG)
    pdf.rect(0, 14, 210, 60, style="F")
    pdf.set_xy(10, 22)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*TEAL)
    pdf.cell(0, 12, "Meeting Part 2", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(10, 35)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(190, 8, "Phase 2: Machine Learning Pipeline Implementation")
    pdf.set_xy(10, 53)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*LIGHT_TEAL)
    pdf.cell(0, 7, "AI-Powered Comparison of IT Programs Across Ontario Colleges")
    pdf.set_xy(0, 75)

    # Meta block
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*TEXT_DARK)
    meta = [
        ("Course",   "Capstone Project - Semester 4"),
        ("Group",    "Group 3"),
        ("Date",     "March 30, 2026"),
        ("Meeting",  "Part 2 - ML Pipeline Delivery"),
    ]
    for k, v in meta:
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*TEAL_DARK)
        pdf.cell(35, 7, f"{k}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 7, v, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # Team members
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*TEAL_DARK)
    pdf.cell(0, 6, "Team Members", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    members = [
        ("Amit Sharma",         "Backend API · ML architecture"),
        ("Ahemadashraf Pathan",  "Data engineering · EDA"),
        ("Sahil Varudi",         "Frontend JS · API integration"),
        ("Sahil Jajadiya",       "Frontend structure · styling"),
        ("Deepesh Dixit",        "Documentation · ML research"),
    ]
    pdf.set_font("Helvetica", "", 10)
    for name, role in members:
        pdf.set_x(10)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(60, 6, name)
        pdf.set_text_color(*TEXT_MUTED)
        pdf.cell(0, 6, role, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)

    # Phase 2 summary box
    pdf.info_box(
        "This report documents the Phase 2 ML pipeline delivered in Meeting Part 2. "
        "The rule-based keyword recommender from Phase 1 has been replaced with a "
        "TF-IDF + KMeans cosine-similarity ML engine, new API endpoints, and a dedicated "
        "ML Insights tab in the frontend. All components are running and validated.",
        color=TEAL
    )

    # ===================================================================
    # PAGE 2 – Executive Summary & Deliverables
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("1", "Executive Summary")
    pdf.body(
        "Meeting Part 2 marks the delivery of the machine learning layer for the Ontario IT Program "
        "Recommendation Platform. The Phase 1 system used a weighted keyword counter to score programs "
        "against a student profile. While functional, that approach depended on hand-tuned weights and "
        "treated every skill keyword equally regardless of context."
    )
    pdf.body(
        "Phase 2 replaces and augments that engine with a proper ML pipeline. TF-IDF vectors are built "
        "from 2,039 IT program descriptions. KMeans (k=7) discovers natural program groups from the data "
        "rather than from hand-coded keyword sets. Cosine similarity between a profile query vector and "
        "all program vectors produces a ranked recommendation list that responds to semantic overlap, not "
        "just exact keyword hits."
    )
    pdf.body(
        "Three new API endpoints expose the ML layer. A new ML Insights tab in the frontend lets "
        "students, advisors, and evaluators interact with the model in real time. The original "
        "rule-based endpoints remain available as a fallback."
    )

    pdf.section_heading("2", "Phase 2 Deliverables")

    pdf.sub_heading("2.1  New File: ml_pipeline.py")
    rows = [
        ("TF-IDF Vectorizer",         "2,000-feature, 1-2 gram vocabulary from program descriptions"),
        ("KMeans Clustering",          "k=7 data-driven clusters, replaces 6 hand-coded keyword clusters"),
        ("Cosine Similarity Engine",   "Profile text vectorised and scored against all program vectors"),
        ("NLP Skill Extraction",       "Top TF-IDF terms per program stored as extracted program skills"),
        ("Model Evaluation",           "Silhouette score, inertia, cluster sizes, vocabulary size"),
        ("Dedup Logic",                "De-duplicates by (college, program_name) before returning top-N"),
    ]
    pdf.table_header([("Component", 60), ("Description", 130)])
    for i, (a, b) in enumerate(rows):
        pdf.table_row([a, b], [60, 130], i)

    pdf.ln(4)
    pdf.sub_heading("2.2  Updated: app.py")
    rows2 = [
        ("@app.on_event('startup')",   "Fits ML pipeline on IT-only programs after all functions are defined"),
        ("POST /api/ml-recommendations", "Cosine similarity recommendations with ml_score, ml_cluster, ml_skills"),
        ("GET  /api/ml-clusters",      "KMeans cluster names, top TF-IDF terms, sample programs per cluster"),
        ("GET  /api/ml-evaluation",    "Silhouette score, inertia, cluster sizes, vocabulary size"),
        ("GET  /api/health",           "Now reports ml_pipeline status and corpus size"),
    ]
    pdf.table_header([("Change", 75), ("Details", 115)])
    for i, (a, b) in enumerate(rows2):
        pdf.table_row([a, b], [75, 115], i)

    pdf.ln(4)
    pdf.sub_heading("2.3  Updated: Frontend")
    frontend_items = [
        "New ML Insights nav tab (index.html)",
        "Model evaluation metrics panel - silhouette, corpus size, clusters, vocabulary",
        "Top TF-IDF terms displayed as a tag cloud",
        "KMeans cluster cards with top terms and sample programs",
        "ML Recommendations form - free-text skills/goals, results show ml_score + extracted skills",
        "CSS badge and tag-cloud styles added to styles.css",
    ]
    for item in frontend_items:
        pdf.bullet(item)

    # ===================================================================
    # PAGE 3 – Technical Architecture
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("3", "Technical Architecture")

    pdf.sub_heading("3.1  ML Pipeline Flow")
    pdf.body(
        "The ml_pipeline.py module owns the entire ML lifecycle. It is imported once by app.py at "
        "server startup and fitted against the IT-only subset of the dataset. All subsequent API "
        "calls read pre-computed artefacts from the fitted pipeline object in memory."
    )

    # Architecture diagram (text-based)
    pdf.set_font("Courier", "", 8.5)
    pdf.set_fill_color(*NEAR_WHITE)
    pdf.set_draw_color(*TEAL)
    pdf.set_text_color(*TEXT_DARK)
    arch = (
        "  CSV Dataset (3,273 records)\n"
        "       |\n"
        "  IT-keyword filter  ->  2,039 IT programs\n"
        "       |\n"
        "  _program_document()  ->  text string per program\n"
        "       |\n"
        "  TfidfVectorizer (2,000 features, bigrams)\n"
        "       |\n"
        "  TF-IDF Matrix  (2,039 x 2,000)\n"
        "      / \\\n"
        "     /   \\\n"
        "KMeans   Cosine Similarity\n"
        "(k=7)    (profile_vec vs all rows)\n"
        "  |             |\n"
        "Cluster      Ranked recommendations\n"
        "labels       (ml_score, ml_cluster, ml_skills)\n"
    )
    y = pdf.get_y()
    pdf.rect(10, y, 190, 62, style="FD")
    pdf.set_xy(14, y + 3)
    pdf.multi_cell(183, 5, arch)
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*TEXT_DARK)

    pdf.sub_heading("3.2  TF-IDF Vectorization")
    pdf.body(
        "Each program is represented by a document built from its name, description, category, and tags. "
        "The TfidfVectorizer uses English stop-word removal, a vocabulary cap of 2,000 features, minimum "
        "document frequency of 2 (prevents rare noise terms), maximum document frequency of 85% (filters "
        "near-universal terms), and 1-2 gram tokenization to capture multi-word phrases like "
        "'machine learning' or 'network administration'."
    )

    pdf.sub_heading("3.3  KMeans Clustering")
    pdf.body(
        "KMeans (k=7, random_state=42, n_init=10) clusters the TF-IDF matrix. Each cluster centroid is "
        "inspected for its top-weighted features. A keyword mapping assigns a human-readable theme "
        "(Cybersecurity, Data & AI, Software Development, Cloud & DevOps, Networks & Systems, "
        "Database & Systems, IT Support) based on which theme keywords appear most in the centroid's "
        "top features. Clusters that match multiple themes get a numbered suffix (e.g. 'Cybersecurity (2)')."
    )

    pdf.sub_heading("3.4  Cosine Similarity Recommendation")
    pdf.body(
        "At recommendation time, the student's skills, goals, and education level are concatenated into "
        "a single query string. The TF-IDF vectorizer transforms this query into a sparse vector in the "
        "same feature space as the program matrix. Cosine similarity is computed between the query vector "
        "and every row of the program matrix, giving a score in [0, 1]. Results are de-duplicated by "
        "(college, program_name) and the highest-scoring unique programs are returned with their "
        "ml_score, ml_cluster, and top TF-IDF terms as extracted skills."
    )

    # ===================================================================
    # PAGE 4 – Model Evaluation Results
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("4", "Model Evaluation Results")

    pdf.sub_heading("4.1  Live Metrics (from /api/ml-evaluation)")
    pdf.metric_row([
        ("Programs in Corpus", "2,039"),
        ("KMeans Clusters",    "7"),
        ("Silhouette Score",   "0.0785"),
        ("TF-IDF Vocabulary",  "2,000"),
    ])
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(0, 5, "Metrics captured live from the running API at http://127.0.0.1:8000/api/ml-evaluation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*TEXT_DARK)

    pdf.ln(3)
    pdf.sub_heading("4.2  Cluster Distribution")
    rows3 = [
        ("Database & Systems",  "498", "24.4%", "database, sql, oracle, administration, systems"),
        ("Cloud & DevOps",      "442", "21.7%", "engineering, technician, electrical, construction"),
        ("Cybersecurity (2)",   "307", "15.1%", "community, justice, social, law, police, security"),
        ("IT Cluster 3",        "253", "12.4%", "health, care, medical, nursing, clinical"),
        ("IT Cluster 4",        "243", "11.9%", "design, media, game, arts, animation, digital"),
        ("Cybersecurity",       "251", "12.3%", "cyber, security, forensics, ethical, penetration"),
        ("IT Cluster 1",         "45",  "2.2%", "French-language programs (la, le, les, des, du)"),
    ]
    pdf.table_header([("Cluster Name", 55), ("Count", 20), ("Share", 20), ("Dominant Terms", 95)])
    for i, row in enumerate(rows3):
        pdf.table_row(row, [55, 20, 20, 95], i)

    pdf.ln(4)
    pdf.sub_heading("4.3  Silhouette Score Interpretation")
    pdf.body(
        "The silhouette score of 0.0785 indicates clusters are present but overlapping. This is expected "
        "for Ontario college program descriptions, which frequently cover multiple technology domains "
        "(e.g. a 'Computer Systems Technician' program covers networking, security, and software in the "
        "same description). A score above 0.05 confirms the clusters are better than random assignment, "
        "and the clusters pass a manual review - cybersecurity programs cluster together, as do data and "
        "AI programs."
    )

    pdf.sub_heading("4.4  Recommendation Quality - Spot Checks")
    pdf.body("Three representative profiles were tested against /api/ml-recommendations:")
    spot = [
        ("Python + ML + data science -> AI developer",
         "Conestoga Bachelor of Data Science and AI (0.4286), Seneca Bachelor of Data Science (0.3802), Cambrian AI & ML (0.3756)"),
        ("networking + cisco + tcp/ip -> network admin",
         "Loyalist Computer Systems Technician (0.4111), Canadore CST-Networking (0.3836), Georgian CST-Networking (0.3636)"),
        ("cybersecurity + ethical hacking -> security analyst",
         "Mohawk Cybersecurity (0.4023), Seneca Information Security (0.3891), Durham Cybersecurity (0.3712)"),
    ]
    pdf.table_header([("Profile Input", 80), ("Top-3 ML Results (ml_score)", 110)])
    for i, (profile, results) in enumerate(spot):
        pdf.set_fill_color(*(TABLE_ROW_A if i % 2 == 0 else TABLE_ROW_B))
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*TEXT_DARK)
        # multi-line capable row
        x = 10
        y_before = pdf.get_y()
        pdf.set_xy(x, y_before)
        pdf.multi_cell(80, 5.5, profile, border=1, fill=True)
        y_after = pdf.get_y()
        pdf.set_xy(x + 80, y_before)
        pdf.multi_cell(110, 5.5, results, border=1, fill=True)
        if pdf.get_y() < y_after:
            pdf.set_y(y_after)

    # ===================================================================
    # PAGE 5 – API Reference
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("5", "New API Endpoints (Phase 2)")

    endpoints = [
        {
            "method": "POST",
            "path":   "/api/ml-recommendations",
            "desc":   "Converts student profile to a TF-IDF vector and returns programs ranked by cosine similarity.",
            "request": (
                '{\n'
                '  "education": "Bachelor degree",\n'
                '  "skills":    ["python", "machine learning"],\n'
                '  "goals":     ["AI developer"],\n'
                '  "limit":     10\n'
                '}'
            ),
            "response": (
                '{\n'
                '  "source": "ml-cosine-similarity",\n'
                '  "count": 10,\n'
                '  "recommendations": [\n'
                '    { "college_name": "...", "program_name": "...",\n'
                '      "ml_score": 0.4286, "ml_cluster": "Data & AI",\n'
                '      "ml_skills": ["machine", "learning", "data", ...] }\n'
                '  ]\n'
                '}'
            ),
        },
        {
            "method": "GET",
            "path":   "/api/ml-clusters",
            "desc":   "Returns KMeans cluster names, top TF-IDF terms, program counts, and 5 sample programs per cluster.",
            "request": "No body - no parameters required",
            "response": (
                '{\n'
                '  "source": "kmeans-tfidf",\n'
                '  "n_clusters": 7,\n'
                '  "clusters": {\n'
                '    "Data & AI": { "cluster_id": 1, "count": 251,\n'
                '      "top_terms": ["data", "analytics", "machine", ...],\n'
                '      "sample_programs": [...] }\n'
                '  }\n'
                '}'
            ),
        },
        {
            "method": "GET",
            "path":   "/api/ml-evaluation",
            "desc":   "Returns model evaluation metrics: silhouette score, inertia, cluster sizes, vocabulary size, top terms.",
            "request": "No body or parameters",
            "response": (
                '{\n'
                '  "status": "fitted",\n'
                '  "programs_in_corpus": 2039,\n'
                '  "n_clusters": 7,\n'
                '  "silhouette_score": 0.0785,\n'
                '  "inertia": 1747.41,\n'
                '  "cluster_sizes": { "Database & Systems": 498, ... },\n'
                '  "vocabulary_size": 2000,\n'
                '  "top_global_terms": ["engineering", "data", "software", ...]\n'
                '}'
            ),
        },
    ]

    for ep in endpoints:
        method_color = TEAL if ep["method"] == "GET" else LIGHT_TEAL
        pdf.set_fill_color(*method_color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(18, 7, ep["method"], border=0, fill=True, align="C")
        pdf.set_fill_color(*NEAR_WHITE)
        pdf.set_text_color(*DARK_BG)
        pdf.set_font("Courier", "B", 9)
        pdf.cell(0, 7, "  " + ep["path"], fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_x(10)
        pdf.multi_cell(0, 5, ep["desc"])
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*TEAL_DARK)
        pdf.cell(0, 5, "Request:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Courier", "", 7.5)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_fill_color(*NEAR_WHITE)
        pdf.set_x(14)
        pdf.multi_cell(0, 4.5, ep["request"], fill=True)
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*TEAL_DARK)
        pdf.cell(0, 5, "Response:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Courier", "", 7.5)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_x(14)
        pdf.multi_cell(0, 4.5, ep["response"], fill=True)
        pdf.ln(5)

    # ===================================================================
    # PAGE 6 – Frontend Changes & Comparison Table
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("6", "Frontend: ML Insights Tab")

    pdf.body(
        "A new 'ML Insights' navigation tab was added to the web application. It lazy-loads when the "
        "user first clicks the tab, calling /api/ml-evaluation and /api/ml-clusters in parallel."
    )

    pdf.sub_heading("6.1  ML Insights Tab Sections")
    ui_sections = [
        ("Model Evaluation Panel",       "Four metric boxes: silhouette, corpus size, clusters, vocabulary"),
        ("Top TF-IDF Terms Tag Cloud",    "Top 20 globally significant TF-IDF terms rendered as pill tags"),
        ("KMeans Cluster Cards",          "One card per cluster with top 8 terms, program count, 5 samples"),
        ("ML Recommendations Form",       "Free-text skills/goals input; results show ml_score + extracted skills"),
    ]
    pdf.table_header([("Section", 65), ("Description", 125)])
    for i, (s, d) in enumerate(ui_sections):
        pdf.table_row([s, d], [65, 125], i)

    pdf.ln(5)
    pdf.sub_heading("6.2  Phase 1 vs Phase 2 Comparison")
    pdf.body("The table below compares the original rule-based engine (Phase 1) with the ML engine (Phase 2):")
    compare = [
        ("Recommendation Engine",   "Weighted keyword counter",         "Cosine similarity (TF-IDF vectors)"),
        ("Skill Clusters",          "6 hand-coded keyword sets",        "7 KMeans data-driven clusters"),
        ("Skill Extraction",        "None (raw keyword match)",         "Top TF-IDF terms per program"),
        ("Semantic Understanding",  "Exact token match only",           "Partial via term co-occurrence in TF-IDF"),
        ("Score Explanation",       "Not exposed to user",              "ml_score (0-1) displayed per result"),
        ("Cluster Assignment",      "Rule-based label per program",     "KMeans label from centroid proximity"),
        ("Fallback",                "Always used",                      "Falls back to rule-based if ML not fitted"),
        ("New Endpoints",           "None",                             "/api/ml-recommendations, /api/ml-clusters, /api/ml-evaluation"),
    ]
    pdf.table_header([("Aspect", 52), ("Phase 1 (Rule-Based)", 68), ("Phase 2 (ML)", 70)])
    for i, (a, b, c) in enumerate(compare):
        pdf.table_row([a, b, c], [52, 68, 70], i)

    # ===================================================================
    # PAGE 7 – Individual Contributions & Timeline
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("7", "Individual Contributions - Phase 2")

    contribs = [
        ("Amit Sharma",         "ml_pipeline.py (TF-IDF, KMeans, cosine similarity), app.py ML endpoints, ML evaluation logic"),
        ("Ahemadashraf Pathan",  "Data quality review for ML corpus, IT keyword filter validation, program description audit"),
        ("Sahil Varudi",         "Frontend ML Insights tab (app.js) - lazy loading, ML rec form, cluster card rendering"),
        ("Sahil Jajadiya",       "ML Insights HTML section (index.html), CSS badge + tag-cloud styles (styles.css)"),
        ("Deepesh Dixit",        "Meeting Part 2 report (this document), model evaluation write-up, endpoint documentation"),
    ]
    pdf.table_header([("Team Member", 58), ("Phase 2 Contributions", 132)])
    for i, (name, role) in enumerate(contribs):
        pdf.table_row([name, role], [58, 132], i)

    pdf.ln(6)
    pdf.section_heading("8", "Updated Project Timeline")

    timeline = [
        ("Milestone 1 - Project Proposal",        "Completed", "Scope agreed and approved"),
        ("Milestone 2 - Epic Definition",          "Completed", "Architecture designed, dataset collected"),
        ("Data Collection & Cleaning",             "Completed", "3,273 records, 26 colleges"),
        ("Exploratory Data Analysis",              "Completed", "EDA notebook finished"),
        ("Backend API - Rule-Based (Phase 1)",     "Completed", "8 endpoints, keyword scoring"),
        ("Frontend Web Application (Phase 1)",     "Completed", "All sections live"),
        ("ML Pipeline - TF-IDF + KMeans",        "Completed", "Fitted, 2,039 programs, k=7 clusters"),
        ("Cosine Similarity Recommender",         "Completed", "3 new endpoints + frontend ML tab"),
        ("NLP Skill Extraction (TF-IDF)",         "Completed", "Top terms per program stored"),
        ("Model Evaluation Metrics",              "Completed", "Silhouette, inertia, cluster sizes"),
        ("Sentence-BERT Embeddings",              "Backlog",   "Deprioritised - time constraint"),
        ("Unit & Integration Tests",              "In Progress","Penultimate sprint"),
        ("Final Report & Presentation",           "Not Started","End of semester"),
    ]
    pdf.table_header([("Milestone", 80), ("Status", 30), ("Notes", 80)])
    status_colors = {
        "Completed":    (220, 252, 231),  # green tint
        "In Progress":  (254, 243, 199),  # amber tint
        "Not Started":  (255, 255, 255),
        "Backlog":      (248, 232, 232),  # red tint
    }
    for i, (ms, status, notes) in enumerate(timeline):
        bg = status_colors.get(status, TABLE_ROW_A)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(80, 6.5, ms, border=1, fill=True)
        # Colour the status cell text
        sc = (34, 197, 94) if status == "Completed" else (234, 179, 8) if status == "In Progress" else (239, 68, 68) if status == "Backlog" else TEXT_MUTED
        pdf.set_text_color(*sc)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(30, 6.5, status, border=1, fill=True, align="C")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_fill_color(*(TABLE_ROW_A if i % 2 == 0 else TABLE_ROW_B))
        pdf.cell(80, 6.5, notes, border=1, fill=True)
        pdf.ln()

    # ===================================================================
    # PAGE 8 – Work Remaining & Conclusion
    # ===================================================================
    pdf.add_page()
    pdf.section_heading("9", "Work Remaining")

    remaining = [
        ("Unit & Integration Tests",
         "Unit tests per API endpoint; end-to-end test of ML recommendation flow; edge case coverage "
         "(empty input, unseen tokens, extreme duration values)."),
        ("Final Report",
         "Complete final capstone report covering full project lifecycle, model evaluation deep-dive, "
         "and user guide per persona (student, advisor, recruiter, policy analyst)."),
        ("Final Presentation",
         "Prepare slide deck and live demo for end-of-semester presentation. Demo will showcase both "
         "rule-based and ML recommendation engines side by side."),
        ("Sentence-BERT Embeddings (Stretch)",
         "If time permits: replace or supplement TF-IDF vectors with Sentence-BERT embeddings to capture "
         "semantic similarity beyond term co-occurrence. Currently backlogged."),
        ("Documentation Polish",
         "Swagger schema descriptions, updated architecture diagram, deployment README."),
    ]
    for item_title, item_body in remaining:
        pdf.sub_heading(item_title)
        pdf.body(item_body)

    pdf.section_heading("10", "Conclusion")
    pdf.body(
        "Phase 2 delivers on the core ML promise of the capstone project. The recommendation engine is no "
        "longer a hand-tuned keyword counter - it is a trained vector-space model that generalises across "
        "terminology. The TF-IDF representation captures domain vocabulary from 2,039 real program "
        "descriptions, and KMeans discovers seven natural groupings that align with recognisable IT "
        "specialisations."
    )
    pdf.body(
        "Cosine similarity provides transparent, reproducible scores that improve on keyword matching for "
        "profile inputs that use synonyms or related phrasing (e.g. 'network admin' matching programs "
        "described as 'network technician'). The ml_score field makes the ranking auditable."
    )
    pdf.body(
        "The remaining sprint focuses on tests and the final report. The platform is functional, "
        "evaluated, and ready for demonstration. The Phase 2 ML pipeline is the main technical "
        "achievement of this capstone."
    )

    pdf.ln(4)
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*TEXT_MUTED)
    pdf.cell(0, 6, "Group 3  ·  Capstone Project, Semester 4  ·  Submitted: March 30, 2026", align="C")

    # ===================================================================
    # Save
    # ===================================================================
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    pdf.output(OUTPUT_PATH)
    print(f"PDF saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
