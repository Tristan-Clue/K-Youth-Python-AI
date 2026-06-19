# AI-Powered Job Market Skill Analysis Pipeline

## Project Overview

This repository contains two connected projects that together form an end-to-end job market skill analysis workflow.

### Project 1: Data Tagging Pipeline

The first project processes raw job posting data and transforms it into structured, searchable skill data.

Pipeline flow:

```text
Raw Job Data
    ↓
Extraction
    ↓
LLM Skill Tagging
    ↓
SQLite Storage
```

This pipeline uses a Medallion-style architecture:

```text
0_source → 1_bronze → 2_silver → 3_gold
```

* **0_source**: Original source files
* **1_bronze**: Raw extracted data
* **2_silver**: Cleaned and transformed records
* **3_gold**: Final analytics-ready output

The primary goal is to extract technical skills from unstructured job descriptions and store them in a structured format.

---

### Project 2: Skill Gap Analysis

The second project compares a candidate’s resume against the job market skills database to identify missing skills.

Pipeline flow:

```text
Resume
    ↓
Technical Skill Extraction
    ↓
Skill Normalization
    ↓
Database Skill Comparison
    ↓
Skill Gap Result
```

The goal is to compute:

```text
market_skills - resume_skills
```

This reveals the technical skills currently demanded by the market but missing from the candidate's resume.

---

# Setup Instructions

## Prerequisites

The project requires:

* Python 3.14.x
* uv
* Internet access (for dependency installation)
* Optional:

  * Ollama (for local LLM inference)
  * Gemini API key (for cloud LLM inference)

---

## 1. Verify Python Version

```bash
python3 --version
```

Expected output should begin with:

```text
Python 3.14
```

---

## 2. Install uv

Install or upgrade uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

---

## 3. Install Dependencies

From the project root:

```bash
uv sync
```

Dependencies are managed through `pyproject.toml`.

This installs all required packages and creates the project environment.

---

## 4. Verify Tool Versions

```bash
python3 --version
uv --version
uv run ruff --version
```

Expected:

* Python 3.14.*
* uv
* ruff 0.15.*

---

## 5. Code Formatting

Format and lint the codebase using Ruff:

```bash
uv run ruff format .
uv run ruff check . --fix
```

---

## Environment Variables

Create a `.env` file at the project root.

Example:

```env
GEMINI_API_KEY=your_api_key_here
MODEL=your_model_name
DB_PATH=your_database_path
```

Do not commit secrets to Git.

---

# Usage

## Project 1: Data Tagging Pipeline

Run:

```bash
uv run python main.py
```

Ensure `main.py` is configured to execute the tagging pipeline.

Primary script:

* `tag_data.py`

Expected behavior:

* Read raw job data
* Extract job descriptions
* Send data for LLM-based skill tagging
* Store tagged skills in SQLite database

Example output:

```text
Processed 100 jobs
Tagged 98 successfully
Failed 2 after retries
```

---

## Project 2: Skill Gap Analysis

Run:

```bash
uv run python main.py
```

Ensure `main.py` is configured to execute skill gap analysis.

Primary script:

* `find_skill_gaps.py`

Expected input:

* Resume text file
* SQLite database

Example:

```text
resume.txt
jobs.db
```

Example output:

```python
SkillGapResult(
    gaps=['aws', 'docker', 'kubernetes']
)
```

---

# API / Function Reference

## Project 1 — Data Tagging

### `tag_data()`

**Purpose:**
Reads job records and tags technical skills using LLMs.

**Inputs:**

* Job descriptions from SQLite or extracted source data

**Outputs:**

* Updated SQLite records with tagged technical skills

---

## Project 2 — Skill Gap Analysis

### `find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult`

**Purpose:**
Compares resume skills against market skills.

**Inputs:**

* `input_file_path`: Path to resume text file
* `db_url`: Path to SQLite database

**Output:**

* `SkillGapResult`

Example:

```python
class SkillGapResult(BaseModel):
    gaps: list[str]
```

---

### `read_resume(input_file_path: str) -> str`

**Purpose:**
Reads resume text safely from disk.

**Input:**

* File path

**Output:**

* Cleaned resume text

---

### `extract_technical_skills(resume_text: str) -> list[str]`

**Purpose:**
Extracts technical skills section from resume.

**Input:**

* Resume text

**Output:**

* Raw skill list

---

### `normalize_skills(skills: list[str]) -> set[str]`

**Purpose:**
Normalizes skills into deterministic format.

Processing includes:

* Lowercasing
* Whitespace removal
* Slash splitting
* Special handling for:

  * CI/CD
  * A/B Testing
  * C/C++

**Output:**

* Normalized skill set

---

### `get_market_skills(db_url: str) -> set[str]`

**Purpose:**
Reads technical skills from SQLite database.

**Input:**

* Database path

**Output:**

* Aggregated market skill set

---

# Data / Assumptions

## Database Schema

SQLite database contains a `jobs` table.

Relevant field:

```text
tech_stack
```

Example:

```text
python,docker,aws
```

---

## Resume Assumptions

Expected resume format contains:

```text
SKILLS
Technical Skills:
Languages:
Additional Skills:
```

Example:

```text
Technical Skills: Python, SQL, Docker
```

---

## Skill Parsing Rules

### Slash Splitting

General rule:

```text
AWS/Azure/GCP
→ aws, azure, gcp
```

Special cases:

* CI/CD
* A/B Testing

These are treated as single skills.

Special handling:

* C/C++ → c, c++

---

## Simplifications

The system intentionally ignores:

* Certifications
* Soft skills
* Non-technical skills

Examples ignored:

* Leadership
* Cooking
* Communication

---

# Testing

Testing focused on correctness, determinism, and edge cases.

## Test Cases

### Resume Tests

* Valid resume with technical skills
* Resume with missing technical skills
* Empty resume file
* Invalid file path

---

### Database Tests

* Valid database
* Empty jobs table
* Missing database file
* Null tech_stack entries

---

### Skill Matching Tests

* Exact matches
* Slash-separated skills
* CI/CD handling
* A/B Testing handling
* C/C++ handling

Example:

```text
Resume: C/C++
DB: c,c++
Expected: no gap
```

---

## Determinism Validation

The system was tested with repeated runs using identical inputs.

Expected:

* Same extracted skills
* Same normalized skill sets
* Same final sorted output

Determinism was ensured by:

* Avoiding LLM usage in skill gap computation
* Using rule-based parsing
* Sorting outputs

---

# Limitations

## Data Tagging Pipeline

* LLM tagging quality depends on model capability
* Incorrect tagging can affect downstream analysis
* Large datasets increase processing time

---

## Skill Gap Analysis

* Resume parser expects structured formatting
* Unusual resume layouts may fail extraction
* Skill canonicalization is intentionally lightweight
* Equivalent skills may not always match

Example:

```text
node.js != nodejs
```

without additional canonicalization rules.

---

# Architecture Reflection

## Design Choices

The system was intentionally divided into two separate projects:

* Skill extraction/tagging
* Skill comparison

This separation improves modularity and makes each component easier to test independently.

The skill gap system also uses helper functions for each stage:

* Reading input
* Extraction
* Normalization
* Database access
* Comparison

This creates a clean pipeline architecture with clear separation of concerns.

---

## Trade-offs

A major design decision was prioritizing **determinism over intelligence** in the skill gap analysis.

Although LLMs could improve parsing flexibility, they introduce:

* nondeterminism
* latency
* hallucination risk

For this reason, the final skill gap analysis uses deterministic rule-based parsing instead.

For the tagging pipeline, LLMs were chosen because unstructured job descriptions benefit significantly from semantic understanding.

This creates a balanced architecture:

* LLMs for unstructured extraction
* Rule-based logic for deterministic comparison

---

## Improvements

Given more time, future improvements would include:

* Better skill canonicalization
* Case-insensitive resume parsing
* More robust resume parsing for varied layouts
* Skill weighting by market frequency
* Better analytics on demand trends
* Allow PDF to be used for resume instead of text file provided

Examples:

* Ranking skill gaps by market demand
* Grouping related technologies
* Adding confidence scores for extracted skills
