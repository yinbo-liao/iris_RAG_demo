# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Iris RAG is a full-stack application demonstrating two AI query-processing architectures using the Iris flower dataset: **Function Call** (single deterministic tool) vs **Combined Tools** (multi-tool + RAG + synthesis).

**Stack:** FastAPI + PostgreSQL + React 18 + Vite + Tailwind CSS + Docker
**Database:** PostgreSQL (production), SQLite in-memory (tests)
**ML:** scikit-learn RandomForest + TF-IDF vector store

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest app/tests/ -v                          # Run all tests
pytest app/tests/test_services.py -v          # Service-specific tests
```

### Frontend
```bash
cd frontend
npm install
npm run dev                                   # Dev server at localhost:5173
npm test                                      # vitest (33 tests)
```

### Docker (full stack)
```bash
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Architecture

```
Frontend (React + Vite)
  ├── QueryPage    — single query, one approach at a time
  ├── ComparePage  — side-by-side Function Call vs Combined Tools
  ├── KnowledgePage — dataset stats, feature ranges, RAG documents
  └── HistoryPage  — past queries with expandable details

Backend (FastAPI)
  ├── main.py              — lifespan, CORS, health check
  ├── config.py            — pydantic-settings (DATABASE_URL)
  ├── models/__init__.py   — lazy engine (get_engine/override_engine)
  ├── models/models.py     — PredictionLog, KnowledgeDoc, IrisSample
  ├── routers/api.py       — 7 endpoints under /api prefix
  ├── services/iris_service.py  — ML model, VectorStore, 6 tools, 2 processors
  └── schemas/schemas.py   — Pydantic request/response models
```

### Key architectural patterns

- **Lazy engine creation** in `models/__init__.py` — `get_engine()` creates the engine on first call; `override_engine()` injects SQLite for tests
- **TF-IDF VectorStore** — in-memory, cosine similarity, `search(query, top_k)` returns ranked docs with scores; filters results below 0.01 threshold
- **6 Tools** with JSON schemas in `TOOL_SCHEMAS` (predict_species, get_species_stats, filter_flowers, compare_species, retrieve_knowledge, get_all_species)
- **2 Processors**: `FunctionCallProcessor` (single tool via regex matching) and `CombinedToolsProcessor` (RAG → multi-tool → synthesize)
- **Test DB**: Uses `StaticPool` with `sqlite://` (not `:memory:`) so all sessions share one connection — critical for test isolation

### Frontend patterns

- `useQuery()` hook manages query state, approach selection, loading, error, and result — shared by QueryPage and ComparePage
- `useStats()` hook fetches `/api/stats` with caching
- `ResultCard` renders differently for Function Call (single JSON, yellow border) vs Combined Tools (multi-result, knowledge + synthesis, green border)
- Color system: Function=amber, Combined=emerald, RAG=violet
- Keyboard shortcuts: Enter=submit, Ctrl+Enter=compare
