from pydantic import BaseModel
import sqlite3

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
	
def extract_technical_skills(resume_text: str) -> list[str]:
	try:
		start = resume_text.find("Technical Skills:")
		if start == -1:
			return []

		start += len("Technical Skills:")
		end = resume_text.find("Languages:", start)

		if end == -1:
			end = resume_text.find("Additional Skills:", start)

		if end == -1:
			end = len(resume_text)

		technical_skills_text = resume_text[start:end]
		skills = technical_skills_text.split(",")
		return skills

	except Exception as error:
		print(f"Error extracting technical skills: {error}")
		return []

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

def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
	resume_text = read_resume(input_file_path)

	if not resume_text:
		return SkillGapResult(gaps=[])
	
	skills = extract_technical_skills(resume_text)
	resume_skills = normalize_skills(skills)
	db_skill = get_market_skills(db_url)

	gaps = (sorted(db_skill - resume_skills))

	return (SkillGapResult(gaps = gaps))