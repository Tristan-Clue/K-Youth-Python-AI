from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/chat")
def chat(request: Request):
    # ...
    pass