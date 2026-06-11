# K-Youth Week_1

# Objective
1. build a robust, local data engineering pipeline that successfully extracts raw data from the 0_source
2. processes and cleans it into a structured format
3. stores it in a relational database (jobs.db)

# Project Setup

## Prerequisites
- Python `3.14.x`
- `uv`
- Internet access to install dependencies

## 1) Verify Python 3.14
Use Python 3.14 for this project.

```bash
python3 --version
```

Expected output starts with `Python 3.14`.

If your default `python3` is not 3.14, install Python 3.14

## 2) Install uv
Install/upgrade `uv`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Expected output starts with `uv <version>`.

## 3) Create environment and install dependencies
From the `week_1` directory:

```bash
cd week_1
uv sync
```

This will create/update the project environment and install dependencies from `pyproject.toml`.

## 4) Verify tool versions
The project requires:
- Python `3.14.*`
- `uv`
- `ruff` `0.15.*`

Run:

```bash
python3 --version
uv --version
uv run ruff --version
```

## 5) Format all Python code with ruff 0.15

```bash
uv run ruff format .
uv run ruff check . --fix
```

## 6) Run the pipeline
Run the full flow (ingest -> process -> load -> profile):

```bash
uv run main.py all
```

Or run only profiling:

```bash
uv run main.py profile
```

# Usage

## Required inputs
- Place raw source files in `data/0_source`
- Keep the expected folder structure under `data/`

## Command syntax

```bash
uv run main.py <command>
```

Available commands:
- `ingest`
- `process`
- `load`
- `profile`
- `all`

## Examples

Run full pipeline end-to-end:

```bash
uv run main.py all
```

Run only a single stage:

```bash
uv run main.py ingest
uv run main.py process
uv run main.py load
uv run main.py profile
```

## Expected outputs

After `ingest`:
- HTML files are created in `data/1_bronze`

After `process`:
- JSON files are created in `data/2_silver`

After `load`:
- SQLite DB is created/updated at `data/3_gold/jobs.db`
- Terminal prints a gold summary like:

```text
📊 Gold Summary:
Total: 84 | Inserted: 84 | Skipped: 0
```

After `profile`:
- Terminal prints data quality statistics like:

```text
--- 🔍 DATA QUALITY REPORT ---
📈 Total Records: 84
❓ Missing Values -> job_title: 0, company: 0, description: 0
```

## If command fails
- `Unknown argument`: command argument is missing or not one of `ingest/process/load/profile/all`
- `Database not found`: run `uv run main.py load` first, then `uv run main.py profile`

# Technical Reflection

#### Day 1: The Extractor (Medallion & Lakehouses)

```
- **What We Did:** Setup folder-based Medallion Architecture `(0_source to 3_gold)`. Extracted raw `.mhtml` files to `1_bronze/`.
- **Industry Context:** Modern data platforms often use ***Data Lakes*** to store raw files before transforming them into structured, query-ready data in a ***Data Warehouse**.*
- **Reflection:** Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
```

The original raw HTML files will retain as the source of the data we extracted. If the parsing logic changes or a bug is discovered during the processing operations, the raw files can be used instead of recollecting the data.

The raw html files can also be compared with the raw mhtml files to identify lost or corrupted data, if needed. Recovery is also safer since corrupted database or bad processing won't remove the original data permanently

#### Day 2: Treatment Plant (ETL vs ELT & Scale)

```
- **What We Did:** Clean HTML `(transform into 2_silver/)` before database load `(load into 3_gold/)` (ETL).
- **Industry Context:** Cloud platforms ***(Snowflake/BigQuery)*** often store raw data first then transform later ***(ELT)***. Enterprise systems use ***Apache Spark*** to process large amounts of data in parallel instead of one file at a time.
- **Reflection:** Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
```

Cloud systems prefer ELT because storage in modern cloud platforms is considered cheap, while compute resources are scalable on demand. By loading raw data first, organizations retain all original information and can apply different transformations later depending on their needs. This makes pipelines more flexible and avoids losing potentially useful data during early cleaning steps.

Sequential processing becomes slow as data volume grows because files are handled one at a time on a single machine or CPU core. A failure midway may also waste significant processing time. Distributed systems like Apache Spark split workloads across many machines so multiple files can be processed in parallel, greatly improving speed, scalability, and fault tolerance.

#### Day 3: The Blueprint & The Vault (Storage & Contracts)

```
- **What We Did:** Used SQLite as Gold “warehouse” layer. Enforced basic data integrity via idempotency during load.
- **Industry Context:** Production systems often separate databases used for day-to-day application operations ***(OLTP)*** from databases optimized for analytics and reporting ***(OLAP)***. Strict Data Contracts help ensure incomplete or corrupted data does not break dashboards, analytics, or downstream systems.
- **Reflection:** What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting `nulls` into DB? How does `INSERT OR IGNORE` help prevent duplicate records?
```

Having a NULL in the DB instead of failing validation right away can clump up the DB with invalid records, which is very likely unusable and invalid. This is why it would be a better choice to fail validation early, instead of having to deal with it later on downstream systems and the sort where error detection are more difficult. This also retains the consistency of the data with an expected schema nad required fields.

INSERT OR IGNORE checks to see if the record exist based off the primary key of the data and skipping it if it is. This saves processing in the pipeline by not doing repetitive duplicate work.

#### Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

```
- **What We Did:** `main.py` acts as manual orchestrator, `all` command finalizes sequence
- **Industry Context:** Real-world pipelines usually use orchestration tools like ***Airflow***, which automate execution, retries, scheduling, and dependency management.
- **Reflection:** What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?
```
If processor.py crashes halfway, some files may already be transformed while others remain unfinished, leaving the pipeline in an inconsistent state. Manual retries with Python scripts can lead to duplicated work, missed steps, or human error because engineers must track progress themselves.

Orchestration tools like Airflow are more reliable because they automatically manage task dependencies, retries, logging, scheduling, and recovery. DAG-based systems know which steps succeeded or failed, allowing only failed tasks to rerun instead of restarting the entire pipeline manually.
