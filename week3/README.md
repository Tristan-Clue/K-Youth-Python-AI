# (Week 3) Resume Helper Chatbot

An interactive chatbot that helps users analyze their resume and identify skill gaps for the Malaysian job market. Users upload their resume as a PDF, and the application compares their skills against a database of job market demands, powered by a local LLM.

## Project Overview

This project is a full-stack web application built across three weeks of a workshop:

- **Week 1** — Data engineering pipeline: scraped Malaysian job listings from JobStreet, built an ETL pipeline (bronze → silver → gold layers) with SQLite, and performed data quality checks.
- **Week 2** — LLM-based skill tagging and gap analysis: used Gemini/Ollama to extract technical skills from job descriptions and resumes, then computed skill gaps using deterministic rule-based parsing.
- **Week 3** — Interactive chatbot frontend: built a Bootstrap-powered chat UI with PDF upload, wired it to a FastAPI backend that integrates the Week 2 skill-analysis pipeline.

The goal of Week 3 is to containerize the frontend and backend as separate microservices and deploy them together using Docker Compose, with Ollama running as a third container for local LLM inference.

---

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://docs.astral.sh/uv/) (optional, for local development)
- Python 3.14+
- Ollama model downloaded locally (optional, for local testing)

---

## Setup Instructions

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the `week3` directory:
   ```bash
   cd week3
   ```

2. Create environment files from the examples:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Edit `backend/.env` with your configuration:
   - `GEMINI_API_KEY` — your Gemini API key (if using Gemini; leave blank for Ollama)
   - `MODEL_PROVIDER` — set to `"ollama"` or `"gemini"`
   - `RESUME_MODEL` — the Ollama model to use (e.g., `llama3.2:3b`)
   - `DATABASE` — path to the SQLite database (default: `jobs_d3_eval.db`)

4. **First-time setup — pull an Ollama model:**
   The Ollama container starts with no models. Pull one before using the chatbot:
   ```bash
   docker compose up -d ollama
   docker exec -it ollama ollama pull llama3.2:3b
   ```
   Models are persisted in the `ollama_data` volume, so you only need to do this once.
   You can check with
   ```
   docker exec -it ollama ollama list
   ```

5. Build and run all services:
   ```bash
   docker compose up --build
   ```

6. Open `http://localhost:8000` in your browser.

### Local Development (without Docker)

#### Backend

```bash
cd backend
uv sync
cp .env.example .env
# Edit .env with your settings
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend

```bash
cd frontend
uv sync
cp .env.example .env
# Set BACKEND_URL=http://localhost:8001
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## Usage

### Starting the Application

```bash
cd week3
docker compose up --build
```

This starts three services:
- **Ollama** (port 11435 on host) — hosts the local LLM
- **Backend** (port 8001 on host) — FastAPI server with the `/chat` endpoint
- **Frontend** (port 8000 on host) — serves the chat UI

### Accessing the Application

Open `http://localhost:8000` in your browser.

### Interacting with the Chatbot

The chatbot supports three types of queries, determined by keywords in your message:

| Query Type | Keywords | Behaviour |
|---|---|---|
| **Skill Gaps** | "skill gap", "what am I missing", "skills missing" | Returns only the list of skills missing from the market database |
| **Summary** | "summarize", "summary", "overview" | Briefly summarizes the resume's key skills and experience |
| **Recommendations** | "recommend", "advice", "how to", "tips" | Provides actionable tips based on the skill gaps |
| **General** | Other messages | Polite, concise response; redirects off-topic questions |

### Uploading a Resume

1. Click **"Choose File"** under the PDF upload section
2. Select a PDF file containing your resume
3. You'll see a confirmation message: *"PDF selected: resume.pdf (245.3 KB). Click Send to attach."*
4. Type your message (e.g., "What are my skill gaps?") and click **Send**
5. The resume text is extracted client-side using PDF.js and sent alongside your message
6. The backend analyzes the resume against the job market database and returns results

### Example Conversation Flow

```
User: [uploads resume.pdf]
Bot: PDF selected: resume.pdf (12.4 KB). Click Send to attach.

User: What are my skill gaps?
Bot: Missing skills: docker, kubernetes, aws, sql, power bi

User: How can I improve my resume?
Bot: Based on your resume and the current Malaysian job market, here are some recommendations:
1. Add Docker and Kubernetes experience...
2. Consider obtaining AWS certification...
```

---

## API / Function Reference

### Backend — `POST /chat`

**Endpoint:** `http://localhost:8001/chat`

**Request body (JSON):**

```json
{
  "message": "What are my skill gaps?",
  "resume_text": "John Doe\nSoftware Engineer\nSkills: Python, JavaScript, React..."
}
```

- `message` (required, string) — the user's question or statement
- `resume_text` (optional, string) — the extracted text from the uploaded PDF resume

**Response (JSON):**

```json
{
  "reply": "Missing skills: docker, kubernetes, aws..."
}
```

**Logic flow:**
1. If `resume_text` is provided, calls `find_skill_gaps()` from the Week 2 module to extract skills via LLM, normalize them, compare against the SQLite market database, and compute gaps
2. Detects user intent from keywords in the message (skill gap / summary / recommendation / general)
3. Builds a contextual prompt combining the persona, resume text, skill gaps, and user question
4. Calls `prompt_model()` with the configured model (Ollama or Gemini)
5. Returns the LLM's response in `{"reply": "..."}`
6. All exceptions are caught and return a friendly error message instead of a 500

### Frontend Proxy — `POST /api/chat`

**Endpoint:** `http://localhost:8000/api/chat`

The frontend acts as a reverse proxy to avoid CORS issues. It receives the request from the browser, forwards it to the backend service, and returns the backend's response.

```python
@app.post("/api/chat")
async def proxy_chat(req: ChatRequest):
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{BACKEND_URL}/chat", json=req.model_dump())
    return resp.json()
```

### Frontend JavaScript Functions

**`sendMessage()`** — Main send handler
- Reads the message from the input field
- If a PDF was selected, extracts text using PDF.js and attaches it as `resume_text`
- Includes `storedResumeText` (from previous uploads) so follow-up messages retain context
- Sends a `POST /api/chat` request with `Content-Type: application/json`
- Displays the bot's reply in the chat history
- Guards against duplicate sends with an `isSending` flag and disables the send button during requests

**`extractPdfText(arrayBuffer)`** — PDF text extraction
- Uses PDF.js to parse the PDF file
- Iterates through all pages, extracts text items, and concatenates them
- Returns a single string of all text content

**`addMessage(message, sender)`** — Renders a chat bubble
- Creates a `<div>` with classes `message`, `user-message` (right-aligned, purple), or `bot-message` (left-aligned, indigo)
- Appends to the chat history and scrolls to the bottom

---

## Data Flow

```
Browser ──(PDF upload + message)──▶ Frontend (/api/chat)
                                       │
                                       │  httpx POST (internal network)
                                       ▼
                                  Backend (/chat)
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              find_skill_gaps    prompt_model       SQLite DB
              (Week 2 module)    (Ollama/Gemini)    (jobs_d3_eval.db)
                    │                  │                  │
                    ▼                  ▼                  ▼
              gaps_list        LLM response        market skills
                    │                  │                  │
                    └────────┬─────────┴──────────────────┘
                             │
                             ▼
                    {"reply": "..."}  ←  JSON response
```

1. User uploads a PDF → browser extracts text with PDF.js
2. User types a message and clicks Send → frontend sends `{ message, resume_text }` to `/api/chat`
3. Frontend proxies the request to the backend at `http://backend:8001/chat`
4. Backend runs `find_skill_gaps()` if a resume was provided, computing the skill gap list
5. Backend detects user intent and builds a contextual prompt
6. Backend calls the LLM (Ollama or Gemini) with the prompt
7. Backend returns `{"reply": "..."}` to the frontend
8. Frontend displays the reply in the chat history

---

## Data Format

### Request Payload

```json
{
  "message": "What are my skill gaps?",
  "resume_text": "Raw text extracted from the uploaded PDF..."
}
```

### Response Payload

```json
{
  "reply": "Based on your resume, you are missing the following skills: docker, kubernetes, aws..."
}
```

### Assumptions

- **PDF format:** Only `.pdf` files are accepted. The PDF must contain selectable text (not scanned images).
- **PDF size:** No explicit size limit is enforced. Very large PDFs may cause slow extraction or exceed the LLM's context window.
- **Message length:** No explicit limit. Very long messages may exceed the model's context window.
- **Database:** The SQLite database (`jobs_d3_eval.db`) is assumed to be present at `backend/src/data/`. It contains a `jobs` table with a `tech_stack` column.
- **Model availability:** The Ollama container must have the specified model pulled (e.g., `llama3.2:3b`). If using Gemini, a valid `GEMINI_API_KEY` is required.
- **Keyword-based intent detection:** The backend uses simple substring matching on lowercase message text to determine intent. Edge cases may occur if a user's phrasing doesn't match the expected keywords.

---

## Testing

### Manual Testing Steps

1. **Start the application:**
   ```bash
   cd week3
   docker compose up --build
   ```

2. **Test the frontend loads:**
   Open `http://localhost:8000` — you should see the chat interface with a welcome message.

3. **Test basic messaging (no resume):**
   Type "Hello" and press Send. The bot should respond with a generic career-advice message.

4. **Test PDF upload and skill gap analysis:**
   - Click the PDF upload input and select a resume file
   - Confirm the "PDF selected" message appears
   - Type "What are my skill gaps?" and press Send
   - The bot should return a list of missing skills

5. **Test summary query:**
   Type "Summarize my resume" — the bot should provide a brief summary of the resume's key skills.

6. **Test recommendation query:**
   Type "How can I improve my resume?" — the bot should give specific, actionable tips.

7. **Test off-topic handling:**
   Type "What's the weather?" — the bot should politely redirect to resume-related topics.

### Backend Testing with curl

```bash
# Basic message (no resume)
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my skill gaps?"}'

# With resume text
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my skill gaps?", "resume_text": "Python developer with 3 years experience..."}'
```

### Docker Network Verification

```bash
# Check all containers are on the same network
docker network inspect resume-net

# Verify backend can reach Ollama
docker exec backend curl -s http://ollama:11434/api/tags

# View container logs
docker logs backend
docker logs frontend
```

---

## Limitations

- **Large PDFs:** No file size limit is enforced. Very large PDFs may cause slow text extraction or overwhelm the LLM's context window, resulting in extremely long response times (especially with local CPU inference).
- **Keyword-based intent detection:** The backend uses simple substring matching to detect whether a user wants skill gaps, a summary, or recommendations. Unusual phrasings may not be classified correctly (e.g., "Tell me what I lack" might not match "skill gaps").
- **Local model performance:** Running `llama3.2:3b` on CPU takes 10-20 seconds per response. No GPU acceleration is configured by default.
- **No chat history persistence:** Conversations are stateless — if the page is refreshed, all messages are lost. The resume text is retained in browser memory only while the page is open.
- **No user authentication:** Anyone can access the application without logging in.
- **Single resume per session:** Only one resume can be uploaded per browser session. Switching resumes requires reloading the page.
- **Text-only PDFs:** Scanned PDFs (image-based) are not supported — PDF.js can only extract text that is selectable in the file.

---

## Architecture Reflection

### Design Choices

The application follows a **microservices architecture** with three containers: frontend, backend, and Ollama. Each service has a single responsibility and communicates over a shared Docker network.

**Why microservices?** Separating the frontend and backend allows different developers to work on independent components without stepping on each other's code. In a deployed environment, if one service breaks, it's easier to identify and fix the root cause without affecting the others. Scaling is also more flexible — if the chat endpoint gets heavy traffic, only the backend needs to be scaled.

**Why Docker?** Containerizing each service ensures consistent environments across development, testing, and production. The Docker Compose file defines the entire stack in a single command, making it trivial for anyone to spin up the application.

**Why a reverse proxy on the frontend?** The frontend proxies requests to the backend via `/api/chat` to avoid CORS issues. Since the browser and backend run on different origins (different ports or containers), a direct browser-to-backend request would be blocked by the browser's Same-Origin Policy. The proxy approach keeps the frontend as the single origin point.

### Trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Microservices over monolith | Independent development, easier debugging | More Docker configuration, inter-service communication overhead |
| Vanilla JS over React/Vue | No build step, simple setup | Harder to scale, no component reusability |
| PDF.js in browser over server-side extraction | No server resources wasted on PDF parsing | Slower on the client side, no server-side validation |
| Keyword-based intent detection | Simple, fast, no extra LLM calls | Fragile — misses unconventional phrasing |
| Local LLM (Ollama) over cloud API | No API costs, privacy, works offline | Slow on CPU, model quality depends on local hardware |
| No database for chat history | Simpler architecture, no persistence layer | Conversations are lost on refresh |

### Improvements

If given more time, the following improvements would be made:

- **Refined user interaction:** Replace keyword-based intent detection with a proper classification step (either a lightweight LLM call or a simple ML model). This would handle natural language variations more reliably.
- **Better UI design:** Replace the vanilla JS chat interface with a modern framework (React, Vue, or Svelte) for a polished, responsive experience with animations, markdown rendering, and typing indicators.
- **Chat history persistence:** Add a lightweight database (SQLite or PostgreSQL) to store conversations, enabling users to resume discussions across sessions.
- **Image-based PDF support:** Use OCR (e.g., Tesseract) to extract text from scanned PDFs, expanding the range of supported resume formats.
- **Cloud deployment:** Deploy the application to a cloud provider (AWS, GCP, or Azure) with a managed Ollama instance or cloud LLM API for faster inference.
- **GPU acceleration:** Enable NVIDIA GPU passthrough in the Ollama container to dramatically speed up model inference.
- **Multiple resume support:** Allow users to upload and switch between multiple resumes within a single session.
