# Frontend — Resume Helper Chatbot UI

FastAPI server serving the chat interface.

## Quick Start

```bash
# Install dependencies
uv sync

# Run locally
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker build . -t frontend:1.0
docker run -p 8000:8000 frontend:1.0
```

## Structure

```
src/
├── app.py              # FastAPI routes (/, /chat), static file mounting
├── templates/
│   └── chat_page.html  # Jinja2 template for the chat UI
└── static/
    ├── css/styles.css  # Chat bubble styling
    └── js/chat.js      # Client-side: DOM, fetch, PDF.js
```
