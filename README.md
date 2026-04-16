# MLInterviewPrep

Full-stack ML/SDE interview preparation platform with spaced repetition,
knowledge framework tracking, and AI-powered study planning.

## Features

- **Problem Tracking** -- CRUD for coding problems with difficulty, tags, patterns, and company associations
- **Spaced Repetition (SM-2)** -- Automatic review scheduling with a timed practice modal
- **Knowledge Framework** -- Hierarchical topic tree with progress tracking and D3 treemap visualization
- **AI Study Planner** -- LLM-generated study plans ranked by urgency with time allocation
- **Interview Question Bank** -- Scrape/paste interview questions, filter by company/role/type, LLM analysis
- **Company Tracker** -- Track application status, interview stages, and topic weights per company
- **Q&A Chat** -- Multi-turn LLM conversations for problem discussion and session summaries
- **Import/Export** -- Full JSON and CSV import/export with merge semantics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, SQLite (WAL mode) |
| Frontend | React 19, TypeScript, Tailwind CSS, Vite |
| LLM | Anthropic Claude API (optional) |
| Testing | pytest (512+ tests) |
| Linting | ruff |
| Deployment | Docker / Docker Compose |

## Quick Start

See [`scripts/QUICKSTART.md`](scripts/QUICKSTART.md) for full setup details.

### Local

```bash
# Backend
python -m venv .venv
source .venv/bin/activate        # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: scraper deps (bs4 + playwright) for forum-ingest features
# pip install -r requirements-scraper.txt
uvicorn src.backend.main:app --reload --port 8100

# Frontend (separate terminal)
cd src/frontend
npm install
npm run dev

# Or run both in one terminal:
python scripts/dev.py
```

Create a `.env` file in the project root with `ANTHROPIC_API_KEY=sk-ant-...`
to enable LLM features. All other features work without it.

### Docker

```bash
docker-compose up --build
```

Backend on `http://localhost:8100`, frontend on `http://localhost:3000`.

## Project Structure

```
MLInterviewPrep/
  src/
    backend/
      main.py              # FastAPI app, lifespan, import/export endpoints
      config.py             # Pydantic settings (env vars)
      database.py           # SQLAlchemy engine, session, DB views
      models/               # SQLAlchemy models (Problem, FrameworkNode, Company, etc.)
      routers/              # API route modules
      services/             # Business logic (SM-2, seed loader, LLM client)
    frontend/
      src/
        pages/              # Dashboard, Problems, Framework, Questions, Companies
        components/         # Layout, Sidebar, ReviewPanel, PracticeModal, Treemap, etc.
        hooks/              # useApi, useTimer
        types/              # TypeScript interfaces
  tests/                    # pytest test suite
  data/                     # SQLite database (created at runtime)
  config/                   # Seed data (YAML)
  Dockerfile                # Backend container
  docker-compose.yml        # Full-stack orchestration
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | Aggregated stats across all modules |
| GET | `/api/problems` | List problems (filterable) |
| POST | `/api/problems` | Create a problem |
| PUT | `/api/problems/{id}` | Update a problem |
| DELETE | `/api/problems/{id}` | Delete a problem |
| GET | `/api/problems/review-queue` | SM-2 due problems |
| POST | `/api/problems/{id}/attempts` | Record an attempt |
| POST | `/api/problems/{id}/review` | LLM review of approach |
| GET | `/api/framework/tree` | Knowledge tree |
| PUT | `/api/framework/nodes/{id}` | Update a node |
| POST | `/api/framework/nodes/{id}/log` | Log a study session |
| GET | `/api/framework/suggest` | AI study plan |
| GET | `/api/companies` | List companies |
| POST | `/api/companies` | Create a company |
| PUT | `/api/companies/{id}` | Update a company |
| GET | `/api/questions` | List interview questions |
| PUT | `/api/questions/{id}` | Update a question |
| POST | `/api/questions/{id}/analyze` | LLM question analysis |
| POST | `/api/qa/chat` | Multi-turn Q&A |
| GET | `/api/export` | Export all data (JSON) |
| POST | `/api/import` | Import data (JSON) |
| POST | `/api/import/csv` | Import problems (CSV) |
| POST | `/api/import/seed` | Reload seed data |

## Testing

```bash
pytest                  # Run all tests
pytest -x               # Stop on first failure
pytest tests/test_foo.py  # Run specific test file
```

## Development Infrastructure

This project uses a Claude Code workflow with automated hooks, task management,
and autonomous session support. See
[`claude-code-workflow-guide.md`](claude-code-workflow-guide.md) for details
on the hook architecture, session lifecycle, and autonomous mode.
