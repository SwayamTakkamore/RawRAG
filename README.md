# RAG Website Chatbot 🤖

A production-grade system that converts **ANY WEBSITE** into an AI-powered chatbot using RAG (Retrieval-Augmented Generation).

Built for hackathons but designed with production best practices.

---

## 🌟 Features

- **Universal Website Support**: Works with any website (GitHub repos, news sites, documentation, etc.)
- **Smart Crawling**: Focused, ethical crawling with robots.txt respect
- **RAG Pipeline**: Semantic chunking, embeddings, and vector search
- **Anti-Hallucination**: Strict grounding to website content only
- **Conversation Memory**: Supports natural follow-up questions
- **Source Transparency**: Shows exactly which pages were used
- **Professional UI**: Clean Next.js frontend with real-time chat

---

## Optional single-page Markdown prefetch

RawRAG's crawler remains the primary path for discovering and indexing a
website. When a public page cannot be extracted cleanly by the local crawler,
you can fetch a Markdown representation first and then provide that file to
the same ingestion workflow:

```bash
curl https://md.replynodes.com/https://example.com > example.com.md
```

[ReplyNodes](https://replynodes.com/) is complementary to the existing
crawler: this is a direct URL-to-Markdown step for one public webpage, not a
replacement for RawRAG's crawl, chunking, embeddings, or vector search.

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │  (User enters URL)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │
├─────────────────┤
│  1. Crawler     │  → Discovers pages (respects robots.txt)
│  2. Scraper     │  → Extracts clean content
│  3. Chunker     │  → Splits into semantic chunks
│  4. Embeddings  │  → OpenAI text-embedding-3-small
│  5. Vector DB   │  → FAISS for similarity search
│  6. RAG Engine  │  → GPT-4 with strict prompts
└─────────────────┘
```

---

## 📁 Project Structure

```
.
├── backend/                # FastAPI backend
│   ├── main.py            # Entry point
│   ├── config.py          # Configuration (.env loader)
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment template
│   │
│   ├── api/
│   │   └── routes.py      # POST /crawl, POST /chat
│   │
│   ├── services/
│   │   ├── crawler.py     # Web crawler
│   │   ├── scraper.py     # Content extraction
│   │   ├── chunker.py     # Text chunking
│   │   ├── embeddings.py  # OpenAI embeddings
│   │   ├── vector_store.py# FAISS vector database
│   │   └── rag.py         # RAG pipeline
│   │
│   ├── models/
│   │   └── schemas.py     # Pydantic models
│   │
│   ├── utils/
│   │   ├── url_utils.py   # URL validation/filtering
│   │   └── text_utils.py  # Text cleaning
│   │
│   └── storage/           # Vector stores & session data
│
└── frontend/              # Next.js frontend
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx        # URL input page
    │   │   └── chat/page.tsx   # Chat interface
    │   └── lib/
    │       └── api.ts          # Backend API client
    │
    └── package.json
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API Key

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the server:**
   ```bash
   python main.py
   ```

   Server runs at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Default: NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

   Frontend runs at `http://localhost:3000`

---

## 🎯 How It Works

### 1. URL Input
- User enters a website URL
- Frontend sends to `POST /api/crawl`

### 2. Crawling & Indexing
- **Crawler** discovers pages (same-domain only, respects robots.txt)
- **Scraper** extracts clean content (removes ads, nav, footer)
- **Chunker** splits into ~400 token chunks with overlap
- **Embeddings** generated via OpenAI API
- **Vector Store** saves to FAISS index
- Returns `session_id`

### 3. Chat Interface
- User asks questions via `POST /api/chat`
- **Query Embedding** generated
- **Vector Search** finds top-K relevant chunks
- **RAG Prompt** built with strict anti-hallucination instructions
- **GPT-4** generates answer (temperature=0.1 for factuality)
- **Sources** returned for transparency

### 4. Follow-up Questions
- Conversation history stored per session
- Last 3 turns injected into context
- Maintains grounding to website content

---

## 🔧 Key Design Decisions

### Anti-Hallucination Strategy
```python
# System prompt enforces strict grounding
"Answer ONLY using information from the provided context.
If the answer is not in the context, respond with:
'I could not find this information on the website.'"

# Low temperature for factual answers
temperature=0.1

# Explicit source citations required
```

### Smart Website Detection
- **GitHub Repos**: Only index README, /docs, /wiki (skip issues, PRs)
- **News Sites**: Extract article body, skip comments/ads
- **Normal Sites**: Index main content areas

### Crawling Ethics
- Max depth: 2 (configurable)
- Rate limiting: 1s delay between requests
- Robots.txt compliance
- URL filtering (no tracking, external domains, media)

### Scalability Considerations
- Each website gets isolated vector index
- Session-based storage (no cross-contamination)
- Batch embedding generation
- FAISS for efficient similarity search

---

## 🎨 UI/UX Highlights

- **Gradient design** (blue to purple)
- **Real-time loading states**
- **Confidence badges** (high/medium/low)
- **Source citations** with clickable links
- **Markdown rendering** in responses
- **Smooth animations** and transitions

---

## 🛡️ Security

- ✅ All API keys in `.env` (never in frontend)
- ✅ Backend-only LLM calls
- ✅ Input validation (Pydantic models)
- ✅ CORS configured for frontend domain
- ✅ No secrets in code or git

---

## 📊 Configuration

### Backend (.env)
```bash
OPENAI_API_KEY=sk-...          # Required
MAX_CRAWL_DEPTH=2              # Crawl depth limit
MAX_PAGES_PER_SITE=50          # Max pages to index
CHUNK_SIZE=400                 # Token chunk size
TOP_K_RESULTS=5                # Retrieval results
CHAT_MODEL=gpt-4-turbo-preview # LLM model
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🧪 Testing

### Test the Backend API
```bash
# Health check
curl http://localhost:8000/health

# Crawl a website
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "message": "What is this website about?"}'
```

### Test Different Website Types
- **GitHub**: `https://github.com/username/repo`
- **News**: `https://bbc.com` or `https://nytimes.com`
- **Documentation**: `https://docs.python.org`
- **College**: Your college website

---

## 🎓 Hackathon Presentation Tips

### Demo Flow
1. Open frontend at `localhost:3000`
2. Enter a well-known website (e.g., Python docs)
3. Show loading state while crawling
4. Ask factual questions:
   - "What is this website about?"
   - "Explain [specific topic from site]"
5. Ask something NOT on the site
   - Show it responds: "I could not find this information on the website."
6. Show source citations
7. Demonstrate follow-up questions

### Key Talking Points
- **Problem**: Manual website navigation is time-consuming
- **Solution**: AI chatbot that knows entire website
- **Innovation**: RAG prevents hallucinations (only website content)
- **Tech Stack**: Production-grade (FastAPI, Next.js, OpenAI, FAISS)
- **Ethics**: Respects robots.txt, rate limits, same-domain only
- **Scalability**: Isolated indexes, session management, efficient search

### Architecture Highlights
- Clean separation of concerns
- Modular design (easy to extend)
- Professional error handling
- Production-ready code structure

---

## 📈 Future Enhancements

- [ ] Redis for session storage (production)
- [ ] Multi-language support
- [ ] PDF/document upload support
- [ ] Chat history export
- [ ] Admin dashboard
- [ ] Usage analytics
- [ ] Docker deployment
- [ ] Streaming responses (SSE)

---

## 🐛 Troubleshooting

### "No meaningful content found"
- Website might be JavaScript-rendered (use Selenium/Playwright)
- Robots.txt might block crawling

### "Failed to crawl website"
- Check URL format (must include http/https)
- Website might be blocking crawlers
- Check internet connection

### Embeddings API errors
- Verify `OPENAI_API_KEY` in `.env`
- Check API quota/billing

### CORS errors
- Ensure backend CORS allows frontend origin
- Check `main.py` CORS configuration

---

## 📝 License

MIT License - Built for educational purposes.

---

## 👥 Credits

Built with:
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **OpenAI** - Embeddings & Chat API
- **FAISS** - Vector similarity search
- **BeautifulSoup** - HTML parsing
- **Tailwind CSS** - UI styling

---

## 🙌 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy Hacking! 🚀**
