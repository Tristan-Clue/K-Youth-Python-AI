from pydantic import BaseModel
from .prompt_model import prompt_model
from dotenv import load_dotenv
import sqlite3
import time
import json
import os


load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 12
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

class SkillGapResult(BaseModel):
	gaps: list[str]

def read_resume(input_file_path: str) -> str:
	try:
		with open(input_file_path, "r", encoding="utf-8") as file:
			content = file.read()

			# Remove weird formatting characters (like form feed)
			content = content.replace("\x0c", "").strip()
			return content

	except Exception as error:
		print(f"Error reading resume: {error}")
		return ""

def response_validation(response: str) -> list[str]:
	# Step 1: Empty response
	if not response:
		raise ValueError("Empty response from LLM")
	response = response.strip()

	# Step 2: Remove markdown wrappers if model ignores prompt
	response = response.replace("```json", "").replace("```", "").strip()

	# Step 3: Parse JSON
	try:
		parsed = json.loads(response)
	except json.JSONDecodeError:
		raise ValueError("Failed to parse JSON response")

	# Step 4: Validate structure
	if not isinstance(parsed, dict):
		raise ValueError("Response is not a JSON object")

	if "tech_stack" not in parsed:
		raise ValueError("Missing tech_stack field")

	tech_stack = parsed["tech_stack"]

	if not isinstance(tech_stack, str):
		raise ValueError("tech_stack must be a string")

	tech_stack = tech_stack.strip()

	# Step 5: Handle N/A
	if tech_stack.lower() == "n/a":
		return []

	# Step 6: Convert to skill list
	skills = tech_stack.split(",")

	cleaned_skills = []
	for skill in skills:
		skill = skill.strip()

		if skill:
			cleaned_skills.append(skill)

	return cleaned_skills

def llm_results(resume):

	# Build prompt
	prompt = f"""
	Extract only technical skills from this resume.

	Rules:
	- Include only technical skills
	- Exclude certifications
	- Exclude soft skills
	- Exclude spoken languages
	- Lowercase all skills
	- Keep slash-based skills intact (e.g. ci/cd, a/b testing, c/c++)
	- Do not wrap output in markdown.
	- Return raw JSON only.

	If no technical skills are found, return:
	{{"tech_stack": "N/A"}}

	Return output strictly in JSON format:
	{{
	"tech_stack": "skill1, skill2, skill3"
	}}

	Resume:
	{resume}
	"""
	for attempt in range(MAX_RETRIES):
		try:
			result = prompt_model(MODEL, prompt, 0)
			batch = response_validation(result)
			return batch
		except Exception as e:
			print(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
			if attempt < MAX_RETRIES - 1:
				if MODEL.startswith("gemini"):
					print(f"Retrying in {RETRY_DELAY} seconds...")
					time.sleep(RETRY_DELAY)
				else:
					print(f"Retrying...")
	print(f"Failed after {MAX_RETRIES} attempts")
	return None

def normalize_skills(skills: list[str]) -> set[str]:
	normalized_skills = set()

	try:
		for skill in skills:
			skill = skill.strip().lower()
			if not skill:
				continue

			# Special case: CI/CD
			if skill == "ci/cd":
				normalized_skills.add(skill)

			# Special case: A/B Testing
			elif skill == "a/b testing":
				normalized_skills.add(skill)

			# Special case: C/C++
			elif skill == "c/c++":
				normalized_skills.add("c")
				normalized_skills.add("c++")

			# General slash splitting
			elif "/" in skill:
				split_skills = skill.split("/")

				for split_skill in split_skills:
					split_skill = split_skill.strip()

					if split_skill:
						normalized_skills.add(split_skill)

			# Normal skill
			else:
				normalized_skills.add(skill)

		return normalized_skills

	except Exception as error:
		print(f"Error normalizing skills: {error}")
		return set()

def get_market_skills(db_url: str) -> set[str]:
	market_skills = set()

	try:
		with sqlite3.connect(db_url) as conn:
			cursor = conn.cursor()

			cursor.execute("SELECT tech_stack FROM jobs")
			rows = cursor.fetchall()

			for row in rows:
				tech_stack = row[0]

				if not tech_stack:
					continue

				skills = tech_stack.split(",")

				normalized = normalize_skills(skills)

				market_skills.update(normalized)
		return market_skills

	except Exception as error:
		print(f"Error reading database: {error}")
		return set()

def find_skill_gaps(resume: str, db_url: str) -> SkillGapResult:
	resume_text = resume

	if not resume_text:
		return SkillGapResult(gaps=[])
	
	skills = llm_results(resume_text)
	resume_skills = normalize_skills(skills)
	db_skill = get_market_skills(db_url)

	gaps = (sorted(db_skill - resume_skills))
	return (SkillGapResult(gaps = gaps))

