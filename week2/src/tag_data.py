import sqlite3 
import json
import time
import math
from pathlib import Path
from src.prompt_model import prompt_model

MAX_RETRIES = 3
RETRY_DELAY = 5

INSTRUCTION_TOKENS = 150
AVG_JOB_TOKENS = 665
AVG_OUTPUT_TOKENS = 30
TOKENS_PER_JOB = AVG_JOB_TOKENS + AVG_OUTPUT_TOKENS

MODEL = "llama3.2:3b"

def extract_rate_limits(filepath: str):
    rate_limits = {}

    with open(filepath, "r") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            model, rpm, tpm, rpd = line.split()
            tpm = int(tpm.replace("k", "")) * 1000
            rate_limits[model] = {"rpm": int(rpm), "tpm": tpm, "rpd": int(rpd)}
    return rate_limits

def calc_from_rate_limits(model_name: str, total_jobs: int, rate_limits: dict):
    if model_name not in rate_limits:
        raise ValueError(f"Model {model_name} not found in rate limits.")

    model_info = rate_limits[model_name]

    rpm = model_info["rpm"]
    tpm = model_info["tpm"]
    rpd = model_info["rpd"]

    max_tokens_per_request = tpm / rpm

    max_batch_by_tpm = math.floor((max_tokens_per_request - INSTRUCTION_TOKENS) / TOKENS_PER_JOB)
    min_batch_by_rpd = math.ceil(total_jobs / rpd)

    if min_batch_by_rpd > max_batch_by_tpm:
        raise ValueError("Cannot satisfy RPD and TPM constraints simultaneously.")

    batch_size = min_batch_by_rpd
    return batch_size

def calc_from_local_limits(model_name: str):

    tokens_per_second = 40
    max_latency_seconds = 30
    max_tokens = tokens_per_second * max_latency_seconds
    batch_size = math.floor((max_tokens - INSTRUCTION_TOKENS) / TOKENS_PER_JOB)

    if batch_size < 3:
        batch_size = 3
    return batch_size

def get_batch_size(model_name: str, total_jobs=None, rate_limits=None):
    if model_name.startswith("gemini"):
        return calc_from_rate_limits(model_name, total_jobs, rate_limits)
    else:
        return calc_from_local_limits(model_name)

def response_validation(rows, response):
	try:
		results = json.loads(response)
	except json.JSONDecodeError:
		raise ValueError("Failed to parse JSON response")
	
	# 2. Root object is a list
	if not isinstance(results, list):
		raise ValueError("Response is not a list")

	# 3. Response count matches batch count
	if len(results) != len(rows):
		raise ValueError(
			f"Mismatch between batch size and response. "
			f"Expected {len(rows)}, got {len(results)}"
		)
	
	# Original source_ids from input batch
	input_ids = {source_id for source_id, description in rows}

	# Track duplicates
	seen_ids = set()

	for item in results:

		# 4. Every item is a dictionary
		if not isinstance(item, dict):
			raise ValueError("Response item is not a dictionary")

		# 5. Required keys exist
		if "source_id" not in item:
			raise ValueError("Missing source_id key")

		if "tech_stack" not in item:
			raise ValueError("Missing tech_stack key")

		source_id = item["source_id"]
		tech_stack = item["tech_stack"]

		# 6. source_id exists in original batch
		if source_id not in input_ids:
			raise ValueError(f"Unexpected source_id returned: {source_id}")

		# 7. Duplicate source_id check
		if source_id in seen_ids:
			raise ValueError(f"Duplicate source_id returned: {source_id}")

		seen_ids.add(source_id)

		# 8. tech_stack must be a string
		if not isinstance(tech_stack, str):
			raise ValueError(f"tech_stack for {source_id} is not a string")

		# 9. Cleanup whitespace
		item["tech_stack"] = tech_stack.strip()

	# Make sure all input IDs were returned
	if seen_ids != input_ids:
		raise ValueError("Returned source_ids do not match input batch")

	# Convert to DB-friendly format
	batch = [
		(item["source_id"], item["tech_stack"])
		for item in results
	]

	return batch

def llm_results(rows):
	# Convert list[tuple] -> list[dict]
	jobs = [
		{
			"source_id": source_id,
			"description": description
		}
		for source_id, description in rows
	]

	# Convert Python object -> JSON text
	jobs_json = json.dumps(jobs, indent=2)

	# Build prompt
	prompt = f"""
	Extract the technical stack from each job description.

	Rules:
	- Return ONLY valid JSON.
	- Preserve source_id exactly.
	- Return one result for every input job.
	- tech_stack must be a comma-separated string.
	- if no tech_stack is found, return N/A for that tech_stack.
	- Do not include explanations or markdown.

	Return format:

	[
	{{
		"source_id": 123,
		"tech_stack": "Python, SQL, Docker"
	}}
	]

	Input jobs:

	{jobs_json}
	"""
	for attempt in range(MAX_RETRIES):
		try:
			result = prompt_model(MODEL, prompt)
			batch = response_validation(rows, result)
			return batch
		except Exception as e:
			print(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
			if attempt < MAX_RETRIES - 1:
				print(f"Retrying in {RETRY_DELAY} seconds...")
				time.sleep(RETRY_DELAY)
	print(f"Failed after {MAX_RETRIES} attempts")
	return None

def tag_data(db_url: str):
	db = Path(db_url)
	if not db.exists():
		print(f"{db.name} does not exist!")
		raise FileNotFoundError("DB does not exist")
	with sqlite3.connect(db) as connection:
		cursor = connection.cursor()
		batchNo = 1
		while True:
			row = cursor.execute("SELECT source_id, description FROM jobs WHERE tech_stack IS NULL or tech_stack = '' ORDER BY source_id LIMIT 3;").fetchall()
			
			if not row:
				print("No more rows")
				break

			batch = llm_results(row) # takes in the LLM prompt, returns a list of tuples containing source_id and tech_stack
			if batch is None:
				print("Not supposed to happen")
				return 
			print(f"Batch update: {batchNo}")
			for source_id, tech_stack in batch:
				print(f"Analyzed Job {source_id}: {tech_stack}")
				cursor.execute("UPDATE jobs SET tech_stack = ? WHERE source_id = ?", (tech_stack, source_id,))
			connection.commit()
			batchNo += 1
