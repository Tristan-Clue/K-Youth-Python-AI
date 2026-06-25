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

DB = os.getenv("DATABASE")
DB_PATH = str(Path(__file__).resolve().parent / "data" / DB)
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini")


@app.post("/chat")
def chat(req: ChatRequest):
    """Process a user message, optionally with resume text, and return an LLM-generated reply."""

    gaps = find_skill_gaps(req.message, DB_PATH)
    reply = " ".join(gaps)
    return {"reply": reply}
