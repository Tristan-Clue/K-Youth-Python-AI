from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(base_dir / "templates")

app.mount(
    "/static",
    StaticFiles(directory=base_dir / "static"),
    name="static"
)

class ChatRequest(BaseModel):
    message: str
    resume_text: str | None = None

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8001")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html"
    )


@app.post("/api/chat")
async def proxy_chat(req: ChatRequest):
    """Proxy the chat request to the backend service."""
    import httpx

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{BACKEND_URL}/chat", json=req.model_dump())

    if resp.status_code != 200:
        return JSONResponse(status_code=resp.status_code, content=resp.json())

    return resp.json()
