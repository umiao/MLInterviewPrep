# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker and Docker Compose
- (Optional) Anthropic API key -- required only for LLM features (Q&A chat,
  problem review, study plan generation, question analysis)

## Option A: Local Development

### 1. Backend

**bash:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Create `.env`

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...       # optional, needed for LLM features
DATABASE_URL=sqlite:///data/mle_prep.db  # default, can be omitted
LLM_MODEL=claude-sonnet-4-20250514      # default, can be omitted
```

If you skip the API key, all CRUD features work normally; only LLM-powered
endpoints (Q&A chat, review, study plan, question analysis) will fail.

### 3. Start the backend

```bash
uvicorn src.backend.main:app --reload
```

The API server starts on `http://localhost:8100`. On first launch, the database
is created at `data/mle_prep.db` and seed data (problems, framework nodes) is
loaded automatically if the problems table is empty.

### 4. Frontend

```bash
cd src/frontend
npm install
npm run dev
```

The frontend starts on `http://localhost:5173` and proxies `/api` requests to
the backend at `localhost:8100`.

### Option A (combined): Single-Command Local Dev

After completing steps 1-2 above (venv + `.env`), run both servers with one
command:

```bash
python scripts/dev.py
```

This starts the backend on `http://localhost:8100` and frontend on
`http://localhost:5173` in a single terminal. Press Ctrl+C to stop both.

## Option B: Docker

```bash
docker-compose up --build
```

- Backend: `http://localhost:8100`
- Frontend: `http://localhost:3000`

A `.env` file is still required in the project root (Docker reads it via
`env_file`). Data is persisted in a Docker volume (`app-data`).

## Seed Data

Seed data loads automatically on first startup when the problems table is
empty. To reload seeds manually at any time:

```bash
curl -X POST http://localhost:8100/api/import/seed
```

## Running Tests

```bash
pytest
```

The test suite (512+ tests) covers all backend endpoints, models, and services.
No running server or API key is required for tests.

## Git Hooks (Optional -- for contributors)

```bash
bash scripts/setup-hooks.sh
```

Installs a pre-commit hook that checks ruff version parity, runs lint on staged
Python files, and scans for emoji.

## Troubleshooting

### Encoding errors on Windows

All file I/O in this project uses explicit `encoding="utf-8"`. If you see
`UnicodeDecodeError` or cp1252 errors, check that any new code you added
specifies the encoding parameter.

### Missing API key

Without `ANTHROPIC_API_KEY` in `.env`, LLM-powered endpoints return errors.
All other features (problem CRUD, framework management, import/export) work
without it.

### Port conflicts

| Service | Default Port | Override |
|---------|-------------|----------|
| Backend | 8100 | `uvicorn ... --port <N>` |
| Frontend (dev) | 5173 | `npm run dev -- --port <N>` |
| Frontend (Docker) | 3000 | Change `ports` in `docker-compose.yml` |
