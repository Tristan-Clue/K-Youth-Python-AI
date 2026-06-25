from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Week 2 modules
from week2.find_skill_gap import find_skill_gaps

app = FastAPI(title="Resume Helper Backend")


class ChatRequest(BaseModel):
    message: str
    resume_text: Optional[str] = None

DB_NAME = os.getenv("DATABASE", "jobs_d3_eval.db")
DB_PATH = str(Path(__file__).resolve().parent / "data" / DB_NAME)


@app.post("/chat")
def chat(req: ChatRequest):
    """Process a user message with an optional resume and return skill gaps."""
    resume = req.resume_text or req.message
    gaps = find_skill_gaps(resume, DB_PATH)
    return {"reply": ", ".join(gaps.gaps)}



