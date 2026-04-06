# Milestone 2: Epic Definition, Data Validation, and Technical Planning

**Group:** 3rd  
**Names:** Amit Sharma, Ahemadashraf Pathan, Sahil Varudi, Sahil Jajadiya, Deepesh Dixit

## 1. Purpose of This Milestone
This milestone is aimed at transforming the sanctioned project “AI-Powered Comparison of IT Programs Across Ontario Colleges” into a comprehensive, practicable, and technically verified delivery plan. This milestone guarantees that Ontario colleges will be able to provide a large enough quantity of trustworthy data, the data will be processed and uniformed, and AI and NLP methods will be employed to their fullest extent to recommend the most suitable institutions and IT programs for students. It mitigates the risk of implementation by confirming data is available, clarifying what the system will and won't involve, and designing the technical architecture all before development starts.

## 2. Epic Definition
**Epic Name:** AI Powered Ontario IT Program Recommendation Platform

**Epic Description:**
The goal is to develop an end-to-end AI system that collects, cleans, standardizes, and analyzes IT program data from Ontario colleges and applies machine learning and NLP models to match a student profile with the most suitable colleges and programs.

**Business Problem Solved:**
This Epic solves the current problem of scattered, inconsistent IT program information by creating one intelligent platform that would allow for easy comparisons and data-driven program selection on the part of students, advisors, and policymakers.

## 3. User Stories (8)
- Being a student, I would like to be able to input my educational background to allow the system to give me relevant suggestions for the IT program based on my educational qualifications.
- As an academic advisor, I would like to see program skill clusters so that I can advise students properly.
- As an administrator in a college, I would like to compare my programs with other programs. This will enable me to better my curriculum standards.
- As a data engineer, I would like to gather and clean program data in order to provide the model with accurate information to be trained on.
- As an ML engineer, I want to classify programs into specializations so that recommendations are accurate.
- I, as a recruiter, would like to be able to determine which colleges create given skill sets to simplify the recruitment process.
- As a policy analyst, I want to analyze the supply of skills in the different colleges to ensure that there is improvement in the planning of education.
- As a system user, I would like to see a dashboard for viewing comparisons so that I can understand my findings easily.

## 4. Task Creation (per User Story)
**User Story 1 – Student Recommendations**
- Design student profile input fields (education, skills, goals)
- Build profile-to-program matching logic
- Implement recommendation ranking algorithm
- Test recommendations with sample student profiles

**User Story 2 – Academic Advisor View**
- Create skill cluster labels
- Map programs to skill tracks
- Build advisor view interface
- Validate cluster accuracy

**User Story 3 – College Benchmarking**
- Define comparison metrics (skills, duration, outcomes)
- Create benchmarking dataset
- Build comparison reports
- Validate results with sample colleges

**User Story 4 – Data Engineering**
- Scrape IT program data from college websites
- Clean and standardize fields
- Handle missing and duplicate records
- Store data in structured database

**User Story 5 – ML Classification**
- Preprocess course descriptions (NLP)
- Generate feature embeddings
- Train specialization classification model
- Evaluate model accuracy

**User Story 6 – Policy Analysis**
- Integrate labor market skill demand data
- Compare demand with program supply
- Generate analytics reports
- Validate insights with sample scenarios

**User Story 7 – Recruiter Insights**
- Map programs to industry skill keywords
- Create search/filter functions
- Rank colleges by skill output
- Test recruiters use cases

**User Story 8 – Dashboard Visualization**
- Design dashboard layout
- Build visual comparisons (charts, filters)
- Connect dashboard to model outputs
- Perform usability testing

## 5. Agile Board Setup
The team will create a Jira or Trello board with the following columns:
- Backlog
- To Do
- In Progress
- Code Review
- Done

The board will contain:
- The Epic
- All user stories
- All tasks linked to their stories
- Team member assignments

## 6. Dataset Selection and Description
**Sources:** Ontario college websites

**Attributes:**
- College Name
- Campus Name/Location
- Program Name
- Credential Type
- Credential Group
- Duration in Months
- Duration in Years
- Program Category
- Delivery Format
- Intake Terms
- Region

## 7. Data Understanding and Quality Check
- Missing value analysis
- Duplicate detection
- Text length validation
- Skill coverage checks
- Outlier detection (tuition, duration)

## 8. Technical Plan
- **Data Collection:** Web scraping, CSV/Database
- **Processing:** Python, Pandas, NLP preprocessing
- **Modeling:** Clustering (K-Means), Classification (Random Forest/XGBoost)
- **Recommendation:** Cosine similarity
- **Visualization:** Tableau / Streamlit

## 9. Jira / Trello Board Link
https://myscc-capstone.atlassian.net/jira/software/projects/G3/summary?atlOrigin=eyJpIjoiMTk0YjM5NTY5ZjYyNDc2YWJlMWY2OThlNTYwNDU5MjgiLCJwIjoiaiJ9

## 10. GitHub Repository Link
(Add link after creating the repo)
