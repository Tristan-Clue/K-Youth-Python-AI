from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

# Creates web server object
app = FastAPI()

# __file__ : special variable for path to script file
# path.resolve() : get absolute path
# path.parent : get the directory of the script
base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(base_dir / "templates")

# Registers route inside app; Creates  GET/ route
# Decorator, attaches behavior to functions. Like events?
# Tells FastAPI: "When someone sents a HTTP GET request to this route, run this function"
# When browser request homepage (localhost:8000/), run home()
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html"
    )