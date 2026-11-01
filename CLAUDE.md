# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Iris RAG is a full-stack demo of a **Multi-Agent** query-processing architecture over the Iris dataset: a 7-agent orchestrator pipeline (EDA, 3 classifiers, evaluation, RAG, synthesis) with least-privilege input scoping. The UI exposes multi-agent analytics, the knowledge base, and query history only.

**Stack:** FastAPI + SQLAlchemy 2 + Pydantic v2 (backend), React 18 + Vite + Tailwind (frontend), PostgreSQL in Docker or SQLite locally, Playwright for E2E.

**Important:** there are no LLM or API-key calls anywhere. Agent reasoning is deterministic Python and the final report is string assembly. Any feature that needs a real model must introduce a provider client and make it injectable/mockable for tests.

## Commands

### Backend (`backend/`)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # API on :8000, docs at /docs
pytest                                        # all tests + coverage (pytest.ini enables --cov)
pytest --no-cov -q                            # fast run without coverage
pytest app/tests/test_services.py::TestVectorStore::test_search_returns_results -v   # single test
```
`ENV` in `backend/.env` selects the database: `development` → `sqlite:///iris_rag.db`, anything else → PostgreSQL at `DATABASE_URL`. Tests never touch either — they inject in-memory SQLite.

### Frontend (`frontend/`)
```bash
npm install
npm run dev                                   # Vite on :5173
npm test                                      # vitest run (setup: src/tests/setup.js)
npm run test:watch
npx vitest run src/tests/components/Header.test.jsx      # single file
npm run build
```

### Full stack / E2E
```bash
docker-compose up --build                     # db :5432, backend :8000, frontend :5173
cd e2e && npm install
npx playwright install chromium               # one-time browser download
npx playwright test                           # backend must already be running at :8000
npx playwright test tests/agent-flow.spec.js  # single spec
npx playwright test --headed                  # watch it run
```
`e2e/` has its own `package.json` (`@playwright/test` only). The Playwright `webServer` starts Vite at :5173 automatically; it does **not** start the backend, so run `uvicorn app.main:app --port 8000` first. The pipeline spec waits up to 60s because each run trains four estimators.

## Architecture

### Backend
```
app/
├── main.py                 # app factory, lifespan create_all, CORS, /health
├── config.py               # pydantic-settings Settings; get_database_url() picks SQLite vs Postgres
├── models/
│   ├── __init__.py         # Base, lazy get_engine()/get_session_factory(), override_engine(), get_db
│   └── models.py           # PredictionLog, KnowledgeDoc, IrisSample
├── routers/api.py          # knowledge/stats/history/seed under /api
├── routers/agents_api.py   # /api/agents/registry and /api/agents/analyze
├── schemas/schemas.py      # Pydantic request/response models
├── services/iris_service.py  # dataset, knowledge base, TF-IDF vector store
├── services/audit.py       # shared PredictionLog writer + numpy→JSON sanitizer
└── agents/
    ├── base.py             # AgentRun audit record, BaseAgent with allowed_inputs scoping
    ├── data_pattern_agent.py  # EDA: stats, correlations, Fisher scores, outliers, separability
    ├── model_agents.py     # RandomForestAgent, SVMAgent, XGBoostAgent (shared metric contract)
    ├── evaluation_agent.py # weighted ranking; reads model_results only
    ├── rag_agent.py        # TF-IDF retrieval + citations; reads query/evaluation/pattern only
    └── orchestrator.py     # MainOrchestratorAgent: plan → parallel agents → eval → RAG → report
```

**Import-time initialization:** `iris_service.py` loads the Iris dataset and fits the `TfidfVectorizer` at module import. Agents import this module at import time too, so any error there breaks every endpoint and test. Keep new heavy work lazy (initialize on first use) rather than adding more module-level side effects.

**DB indirection:** `models/__init__.py` uses module globals `_engine`/`_SessionLocal`. `override_engine()` swaps both; the `client` fixture in `app/tests/conftest.py` calls it and imports `app.main` *inside the fixture* to control import order. Preserve that ordering.

**Multi-agent pipeline:** `MainOrchestratorAgent.analyze()` runs the EDA agent and three model agents concurrently in a `ThreadPoolExecutor`, then evaluation, then RAG, then report synthesis. Each `BaseAgent` declares `allowed_inputs`; `execute()` copies only those keys, so e.g. the Evaluation Agent physically cannot see the dataset or `model_results` from a different run. Agents never raise out of `execute()` — failures become `status="error"` audit records. The XGBoost agent uses `xgboost` when installed and otherwise falls back to sklearn `HistGradientBoostingClassifier`, declaring the engine in its output — do not report it as XGBoost without checking `engine`.

**Tests use `StaticPool` with `sqlite://`** (not `:memory:`) so every session shares one connection — required for data seeded in one fixture to be visible to the app's session.

### Frontend
```
src/
├── api.js                  # axios instance, baseURL = VITE_API_URL || http://localhost:8000
├── App.jsx                 # BrowserRouter; / redirects to /agents; routes: /agents, /knowledge, /history
├── hooks/useQuery.js       # query/result/loading/error + submitQuery (defaults to runMultiAgent)
├── hooks/useStats.js
├── components/             # Header, EmptyState, ErrorBoundary, LoadingSpinner, KnowledgeList
│                           # AgentAuditCard, ModelRankingTable (multi-agent page)
└── pages/                  # AgentPage, KnowledgePage, HistoryPage
```

- `useQuery()` owns the multi-agent query state and is used by `AgentPage`; change submit behavior there, not in the page.
- `HistoryPage` still renders `function_call` / `combined_tools` badges for legacy rows in `prediction_logs`; the `approach-badge-*` CSS classes must stay for that reason.
- Tests mock `../api` with `vi.mock`; keep API functions centralized in `api.js` so mocks stay simple.
- `AgentPage` fetches the registry on mount and tolerates failure; its tests mock `getAgentRegistry`, using a never-resolving promise where the roster is irrelevant.

## Gotchas

- `pytest.ini` always writes coverage to `backend/htmlcov/`; use `--no-cov` for quick loops.
- `frontend/htmlcov/` is a stale copied backend report, not generated by vitest — do not edit or treat it as frontend coverage.
- `/api/stats` hardcodes feature ranges and averages in `api.py` rather than deriving them from `df`; update both if the dataset changes.
- The Docker backend mounts `./backend/app` read-only-ish over the image and runs `--reload`; dependency changes require a rebuild.
- CORS in `main.py` only allows `localhost:5173` / `127.0.0.1:5173`.
- Agent/orchestrator tests take ~20s because they train six estimators (including 5-fold CV). Use `pytest app/tests/test_agents.py -q` for a focused loop.
- `/api/agents/analyze` is a sync endpoint (runs in FastAPI's threadpool) because the pipeline is CPU-bound; keep it sync if you extend it. The frontend axios timeout is 30s, which covers the ~5s pipeline.
