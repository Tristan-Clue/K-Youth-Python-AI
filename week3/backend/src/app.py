from pathlib import Path
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Week 2 modules
from week2.find_skill_gap import find_skill_gaps
from week2.prompt_model import prompt_model

app = FastAPI(title="Resume Helper Backend")


class ChatRequest(BaseModel):
    message: str
    resume_text: Optional[str] = None

DB_NAME = os.getenv("DATABASE", "jobs_d3_eval.db")
DB_PATH = str(Path(__file__).resolve().parent / "data" / DB_NAME)
MODEL = os.getenv("RESUME_MODEL", "llama3.2:3b")


@app.post("/chat")
def chat(req: ChatRequest):
    """Handle resume-related chat or skill gap analysis."""

    try:
        resume = req.resume_text or req.message

        # Only run skill gap analysis when a resume is actually provided
        gaps_list = []
        if req.resume_text:
            gaps_result = find_skill_gaps(resume, DB_PATH)
            gaps_list = gaps_result.gaps if gaps_result else []

        # Determine the user's intent from their message
        msg_lower = req.message.lower()
        is_skill_gap_query = any(kw in msg_lower for kw in ["skill gap", "skill gaps", "skills missing", "what am i missing"])
        is_summary_query = any(kw in msg_lower for kw in ["summarize", "summary", "overview", "give me a summary"])
        is_recommendation_query = any(kw in msg_lower for kw in ["recommend", "advice", "improve", "how to", "tips", "guide"])

        # Build the LLM prompt with context
        prompt_parts = [
            "You are a career advisor specializing in resume improvement for the Malaysian job market.",
            "",
        ]

        if req.resume_text:
            prompt_parts.append(
                "The user has shared their resume text. Here it is:\n"
            )
            prompt_parts.append(f"---RESUME---\n{req.resume_text}\n---END RESUME---\n")

        if is_skill_gap_query and gaps_list:
            prompt_parts.extend([
                "The user asked for their skill gaps. Respond with ONLY the list of missing skills. Do not add extra commentary.",
                f"Missing skills: {', '.join(gaps_list)}.",
                "",
                f"User's question: {req.message}",
            ])
        elif is_summary_query:
            prompt_parts.extend([
                "The user asked for a summary. Briefly summarize the resume's key skills and experience.",
                "",
                f"User's question: {req.message}",
            ])
        elif is_recommendation_query:
            prompt_parts.extend([
                "The user asked for recommendations. Provide a few specific, actionable tips for improving their resume based on the skill gaps and their experience.",
                "",
                f"User's question: {req.message}",
            ])
        else:
            prompt_parts.extend([
                f"User's question: {req.message}",
                "",
                "Guidelines:",
                "- If the user asks about skill gaps, provide the list.",
                "- If the user asks for a summary, briefly summarize the resume.",
                "- If the user asks for advice, give specific tips.",
                "- If the question is unrelated to resumes or careers, politely redirect.",
                "- Keep responses concise.",
            ])

        prompt = "\n".join(prompt_parts)

        reply = prompt_model(MODEL, prompt, temperature=0.7)

        if reply is None:
            logger.error("prompt_model returned None")
            return {"reply": "Sorry, I couldn't get a reply from the AI. Please try again."}

        return {"reply": reply}

    except Exception as e:
        logger.exception(f"Chat endpoint error: {e}")
        return {"reply": "Sorry, I couldn't get a reply from the AI. Please try again."}



