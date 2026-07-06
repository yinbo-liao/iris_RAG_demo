# Iris RAG — Function Call vs Combined Tools

A full-stack web application demonstrating two AI query-processing architectures using the Iris flower dataset (Fisher, 1936).

```
┌──────────────────────────────────────────────────────────┐
│                    Client (React + Vite)                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │
│  │  Query   │ │ Compare  │ │ Knowledge │ │ History  │  │
│  │  Page    │ │  Page    │ │   Page    │ │  Page    │  │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘  │
└───────┼────────────┼─────────────┼─────────────┼────────┘
        │            │             │             │
   ┌────▼────────────▼─────────────▼─────────────▼────────┐
   │                  API (FastAPI)                        │
   │  POST /api/query  ·  GET /api/compare  ·  GET /api/* │
   │  ┌──────────────┐  ┌───────────────────────────┐     │
   │  │ Function Call │  │  Combined Tools (RAG)     │     │
   │  │ Processor     │  │  Processor                │     │
   │  └──────┬───────┘  └──────┬────────────────────┘     │
   └─────────┼──────────────────┼─────────────────────────┘
             │                  │
   ┌─────────▼──────────────────▼─────────────────────────┐
   │              Data Layer                               │
   │  ┌──────────┐ ┌───────────┐ ┌────────────────────┐   │
   │  │ ML Model │ │ TF-IDF    │ │ PostgreSQL          │   │
   │  │(Random   │ │ Vector    │ │ (prediction_logs,   │   │
   │  │ Forest)  │ │ Store     │ │  knowledge_docs,    │   │
   │  │          │ │           │ │  iris_samples)      │   │
   │  └──────────┘ └───────────┘ └────────────────────┘   │
   └──────────────────────────────────────────────────────┘
```

## Approaches

| | Function Call | Combined Tools |
|---|---|---|
| **Pattern** | Query → Execute one tool → Result | Query → RAG → Multi-tool → Synthesize |
| **Speed** | ~50ms | ~150ms |
| **Tools** | 1 per query | 2-4 per query |
| **RAG** | No | Yes (TF-IDF + cosine) |
| **Best for** | Deterministic, simple tasks | Complex, multi-part, contextual |

## Quick Start

### Prerequisites
- Docker 24.x+ & Docker Compose 2.x+
- 4GB RAM, 2 CPU cores

### Launch

```bash
cd iris-rag-app
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Database | localhost:5432 (postgres/postgres) |

## Development

### Backend (Python 3.11+)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Run tests
pytest app/tests/ -v
```

### Frontend (Node 20+)

```bash
cd frontend
npm install
npm run dev

# Run tests
npm test
```

### E2E Tests (Playwright)

```bash
cd e2e
npx playwright install chromium
npx playwright test
```

## Project Structure

```
iris-rag-app/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── app/
│       ├── main.py              # FastAPI entry, CORS, lifespan
│       ├── config.py            # Settings (pydantic-settings)
│       ├── models/              # SQLAlchemy ORM + engine
│       ├── routers/api.py       # 7 REST endpoints
│       ├── services/iris_service.py  # Core: ML, RAG, tools, processors
│       ├── schemas/schemas.py   # Pydantic request/response models
│       └── tests/               # pytest suite (55 tests)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx / App.jsx   # Entry + React Router
│       ├── index.css            # Design system (Tailwind)
│       ├── api.js               # Axios HTTP client
│       ├── hooks/               # useQuery, useStats
│       ├── components/          # Header, QueryForm, ResultCard, etc.
│       ├── pages/               # Query, Compare, Knowledge, History
│       └── tests/               # vitest suite (33 tests)
└── e2e/
    ├── playwright.config.js
    └── tests/                   # 3 E2E flow specs
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | Process query with chosen approach |
| `GET` | `/api/compare?query=` | Run both approaches side-by-side |
| `GET` | `/api/tools` | List tool schemas |
| `GET` | `/api/knowledge` | List knowledge documents |
| `GET` | `/api/stats` | Dataset statistics |
| `GET` | `/api/history?limit=20` | Query history |
| `POST` | `/api/seed` | Seed knowledge docs |
| `GET` | `/health` | Health check |

## Tools Available

1. **predict_species** — Classify flower from 4 measurements
2. **get_species_stats** — Statistical summary for a species
3. **filter_flowers** — Filter by measurement ranges
4. **compare_species** — Compare two species side-by-side
5. **retrieve_knowledge** — RAG vector search
6. **get_all_species** — Summary of all 3 species

## Testing

```
✅ Backend:  55 tests (pytest + SQLite)
✅ Frontend: 33 tests (vitest + Testing Library)
✅ E2E:       9 tests (Playwright)
```
