from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

# Creates web server object
app = FastAPI()

# __file__ : special variable for path to script file
# path.resolve() : get absolute path
# path.parent : get the directory of the script
base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(base_dir / "templates")


app.mount(
"/static",
StaticFiles(directory=base_dir / "static"),
name="static"
)

class ChatRequest(BaseModel):
    message: str

# Registers route inside app; Creates  GET/ route
# Decorator, attaches behavior to functions. Like events?
# Tells FastAPI: "When someone sents a HTTP GET request to this route, run this function"
# When browser request homepage (localhost:8000/), run home()
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        # Passing context (BACKEND_URL) to HTML
        context={"backend_url": os.getenv("BACKEND_URL", "http://localhost:8001")}
    )

@app.post("/chat")
def chat(request: ChatRequest):
    

    reply = f"You said: {request.message}"

    return {"reply": reply}