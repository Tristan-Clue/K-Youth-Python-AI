# Week 3 — Resume Helper Chatbot

An interactive chatbot that lets users upload their resume as a PDF and receive skill-gap analysis and improvement suggestions for the Malaysian job market, powered by LLMs from Week 2.

## Project Structure

```
week3/
├── frontend/                 # FastAPI web server (chat UI)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .python-version
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src/
│       ├── app.py            # FastAPI routes, static file serving
│       ├── templates/
│       │   └── chat_page.html
│       └── static/
│           ├── css/styles.css
│           └── js/chat.js
├── backend/                  # LLM processing service
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .python-version
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src/
│       ├── app.py            # FastAPI POST /chat endpoint
│       └── week2/            # Copy of Week 2 modules (find_skill_gap.py, prompt_model.py, etc.)
├── .env.example
├── .gitignore
└── docker-compose.yml
```

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker & Docker Compose
- Ollama running locally (for local LLM inference), or a Gemini API key

## Setup

```bash
# Install dependencies for each service
cd week3/frontend && uv sync
cd ../backend && uv sync

# Configure environment variables
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and BACKEND_URL
```

---

## Day-by-Day Instructions

### Day 1 — Serve a Page with FastAPI + Docker

**Goal:** Get a working server, then containerize it.

1. Start inside `week3/frontend/`
2. Create a FastAPI app (`src/app.py`) with a `GET /` route that serves `chat_page.html` via Jinja2 templates.
3. Run it locally with Uvicorn:
   ```bash
   uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
4. Verify `http://localhost:8000` renders the page.
5. Write a `Dockerfile` for the frontend service:
   - Use `python:3.14.4-bookworm` as the base image.
   - Install `uv`, copy `pyproject.toml` and `uv.lock` first (for Docker layer caching), then `uv sync`, then copy source.
   - Run `uvicorn` with `--app-dir src --host 0.0.0.0`.
6. Build and run:
   ```bash
   docker build . -t frontend:1.0
   docker run -p 8000:8000 frontend:1.0
   ```

**Deliverables:**
- [ ] `GET /` serves `chat_page.html` via Jinja2 (HTML file must be separate from Python code)
- [ ] Page is accessible at `http://localhost:8000`
- [ ] Dockerfile builds and runs the service successfully

---

### Day 2 — Chat UI + PDF Upload + Environment Variables

**Goal:** Build the chat interface and wire it to a placeholder backend URL.

1. Update `chat_page.html` with a Bootstrap 5 layout containing:
   - A scrollable chat history box (fixed height, `overflow-y: auto`)
   - A file upload input for PDFs (`accept=".pdf"`)
   - A text input field and a "Send" button
2. Create `static/js/chat.js` with vanilla JavaScript that:
   - Listens for clicks on the Send button and Enter key presses on the input
   - Appends the user message to the chat history immediately (optimistic UI)
   - Sends the message as JSON (`POST /api/chat` — the backend route, not yet implemented)
   - Displays the bot's reply in the chat history
3. Create `static/css/styles.css` with custom chat bubble styling (user messages right-aligned in one color, bot messages left-aligned in another).
4. Configure the backend URL as an environment variable:
   - Use `python-dotenv` in `app.py` to load `.env`
   - In `chat.js`, read the backend URL from a global `window.BACKEND_URL` variable set by the Jinja template (pass it via `TemplateResponse` context), **not** hardcoded in JavaScript.
5. For PDF upload:
   - Use [PDF.js](https://mozilla.github.io/pdf.js/) (loaded from CDN) to extract text from the selected PDF file in the browser.
   - Attach the extracted text to the JSON payload sent to the backend alongside the user's message.

**Deliverables:**
- [ ] Chat page with scrollable history, PDF upload, and text input
- [ ] Messages sent as JSON to a backend endpoint (URL from env var, not hardcoded)
- [ ] PDF text extraction via PDF.js attached to the send payload
- [ ] Custom CSS for chat bubbles

---

### Day 3 — Backend: LLM-Powered Chat Endpoint

**Goal:** Implement the backend service that processes user prompts using Week 2's skill-analysis pipeline.

1. Inside `week3/backend/`:
   - Copy the Week 2 modules (`find_skill_gap.py`, `prompt_model.py`, `pyproject.toml`, `uv.lock`) into `src/week2/`.
   - Create a new FastAPI app (`src/app.py`) with a `POST /chat` endpoint.
2. The `/chat` endpoint should:
   - Accept JSON with `message` (str) and optionally `resume_text` (str, from PDF extraction).
   - If a resume is provided, call `find_skill_gap()` from the Week 2 module to compute skill gaps against the market database.
   - Use the LLM (Gemini or Ollama, via `prompt_model()`) to generate conversational responses based on the analysis.
   - Return JSON: `{"reply": "..."}`.
3. Containerize the backend:
   - Write a `Dockerfile` (same pattern as frontend: uv, layer caching, `--app-dir src`).
   - If using Ollama, configure the container to access the host's localhost (where Ollama runs) via Docker networking — see [this guide](https://stackoverflow.com/questions/24319632/access-localhost-inside-a-docker-container) for the top-voted solution.
   - If using Gemini, mount the `.env` file so `GEMINI_API_KEY` is available.

**Deliverables:**
- [ ] `POST /chat` endpoint accepts JSON and returns JSON
- [ ] Backend calls Week 2's skill-analysis functions
- [ ] Dockerfile builds and runs the backend service
- [ ] Ollama access from container (if using local LLM)

---

### Day 4 — Docker Compose: Full Stack

**Goal:** Run frontend and backend together on a shared Docker network.

1. Ensure each service has its own `Dockerfile`:
   - Frontend: `week3/frontend/Dockerfile`
   - Backend: `week3/backend/Dockerfile`
2. Use the latest Python 3.x image tag from Docker Hub as the base.
3. Source files must be placed in `/app` at the root of each container's filesystem.
4. Create `docker-compose.yml` at the `week3/` root:
   - Define two services: `frontend` and `backend`.
   - Each service builds from its respective `Dockerfile`.
   - Put both services on a custom Docker network (do **not** use `network_mode: host`).
   - Frontend communicates with backend via the service name (e.g., `http://backend:8000`).
   - Mount `.env` for environment variables.
   - Expose only the frontend port to the host (e.g., `8000:8000`).
5. Run the full stack:
   ```bash
   docker compose up --build
   ```
6. Verify:
   - `http://localhost:8000` loads the chat UI
   - Sending a message triggers the backend, which calls the LLM and returns a reply
   - Uploading a PDF extracts text and includes it in the request

**Deliverables:**
- [ ] Each service has its own `Dockerfile`
- [ ] `docker-compose.yml` builds and runs both services
- [ ] Services share a custom Docker network (no `host` network driver)
- [ ] Source files are in `/app` inside each container
- [ ] Full stack works end-to-end: UI → backend → LLM → response

---

## Architecture Overview

```
Browser ──(fetch /chat, JSON)──▶ Frontend (FastAPI, port 8000)
                                      │
                                      │  internal network
                                      ▼
                                 Backend (FastAPI, port 8001)
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                      Week 2       Ollama      Gemini
                   skill-gap     (localhost)   (API key)
                   analysis
```

## Key Files

| File | Purpose |
|------|---------|
| `frontend/src/app.py` | FastAPI server, serves HTML, mounts static files |
| `frontend/src/templates/chat_page.html` | Chat UI template (Bootstrap 5) |
| `frontend/src/static/js/chat.js` | Client-side: DOM, fetch, PDF.js integration |
| `frontend/src/static/css/styles.css` | Chat bubble styling |
| `backend/src/app.py` | LLM chat endpoint, calls Week 2 modules |
| `backend/src/week2/` | Copied Week 2: `find_skill_gap.py`, `prompt_model.py` |
| `docker-compose.yml` | Orchestrates both services on a shared network |
