# Video RAG — AI-Powered Video Comparator

Compare any YouTube video with an Instagram reel using retrieval-augmented generation. Ingest video metadata and transcripts, embed them in a vector database, and chat with an AI analyst that cites its sources.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│   IngestForm ──→ VideoCards + ChatPanel                  │
│        │              │           │                      │
│        │              │     SSE Stream (EventSource)     │
└────────┼──────────────┼───────────┼─────────────────────┘
         │              │           │
    POST /api/ingest    │    GET /api/chat/stream
         │              │           │
┌────────▼──────────────▼───────────▼─────────────────────┐
│                   BACKEND (FastAPI)                       │
│                                                          │
│  ┌──────────┐  ┌────────────┐  ┌─────────────────────┐  │
│  │ youtube  │  │ instagram  │  │       rag.py        │  │
│  │  .py     │  │   .py      │  │  ConversationMemory │  │
│  │ yt-dlp + │  │  Apify /   │  │  + Gemini 1.5 Flash │  │
│  │ yt-trans │  │  Mock data │  │  + Retriever        │  │
│  └────┬─────┘  └─────┬──────┘  └──────────┬──────────┘  │
│       │              │                     │             │
│       └──────┬───────┘                     │             │
│              ▼                             ▼             │
│       ┌─────────────┐              ┌──────────────┐     │
│       │ embedder.py │──────────────│ Vector Store │     │
│       │ text-emb-004│              │ Pinecone /   │     │
│       │ + splitter  │              │ ChromaDB     │     │
│       └─────────────┘              └──────────────┘     │
└──────────────────────────────────────────────────────────┘
```

---

## Stack Decisions

| Layer         | Choice                        | Why                                                     |
|---------------|-------------------------------|---------------------------------------------------------|
| Frontend      | React + Vite + Tailwind       | Fast dev server, great DX, utility-first CSS            |
| Backend       | FastAPI                       | Async native, auto docs, type-safe with Pydantic        |
| LLM           | Gemini 1.5 Flash              | Fast, cheap, 1M context window, great for analysis      |
| Embeddings    | text-embedding-004            | Google's latest, 768-dim, good multilingual support      |
| Vector DB     | Pinecone → ChromaDB fallback  | Pinecone for prod scale, Chroma for zero-config local    |
| YouTube       | youtube-transcript-api + yt-dlp| No API key needed, reliable transcript + metadata       |
| Instagram     | Apify instagram-reel-scraper  | Handles auth, no scraping infra needed                   |
| Streaming     | SSE (EventSourceResponse)     | Simple, native browser support, no WebSocket overhead    |
| Orchestration | LangChain (LCEL)              | Composable chains, built-in memory + retrieval           |

---

## Cost Estimate (1000 creators/day)

| Resource          | Unit Cost                | Daily Cost   |
|-------------------|--------------------------|--------------|
| Gemini 1.5 Flash  | ~$0.075/1M input tokens  | ~$1.50       |
| text-embedding-004 | ~$0.004/1K tokens       | ~$0.80       |
| Pinecone Starter  | Free tier / $70/mo       | ~$2.33       |
| Apify             | ~$0.25/1K results        | ~$0.25       |
| **Total**         |                          | **~$5/day**  |

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) API keys for Gemini, Pinecone, Apify

### 1. Clone & Setup Backend

```bash
cd video-rag/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env and add your keys (or leave empty for fallbacks)
cp .env.example .env

# Start backend
python main.py
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger UI)
```

### 2. Setup Frontend

```bash
cd video-rag/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# → http://localhost:5173
```

### 3. Add API Keys (Optional)

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_key        # Required for AI chat
PINECONE_API_KEY=your_pinecone_key    # Optional (falls back to ChromaDB)
APIFY_API_TOKEN=your_apify_token      # Optional (falls back to mock data)
```

---

## Fallback Behavior

| Missing Key       | Behavior                                                |
|--------------------|---------------------------------------------------------|
| `GEMINI_API_KEY`   | Chat returns "Please add GEMINI_API_KEY to .env"        |
| `PINECONE_API_KEY` | Uses ChromaDB (local, no key needed)                    |
| `APIFY_API_TOKEN`  | Returns mock Instagram data (app works end-to-end)      |

---

## Known Limitations

1. **No audio transcription** — Instagram uses caption text only (no Whisper)
2. **Session state is in-memory** — restarts lose all sessions
3. **ChromaDB fallback** — local only, not suitable for production scale
4. **YouTube transcripts** — may not be available for all videos (auto-captions vary)
5. **Rate limits** — YouTube/Apify may rate-limit under heavy load
6. **Single comparison** — currently limited to 1 YouTube + 1 Instagram per session
