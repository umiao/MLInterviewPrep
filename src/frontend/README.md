# MLInterviewPrep Frontend

React single-page application for the ML/SDE Interview Preparation Platform.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript |
| Build | Vite |
| Styling | Tailwind CSS |
| HTTP | Fetch via custom `useApi` hook |
| Visualization | D3.js (treemap) |

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Aggregated stats: problem progress, framework coverage, recent activity, company deadlines |
| Problems | `/problems` | Problem list with filters (difficulty, pattern, company), SM-2 review queue, practice modal with timer |
| Framework | `/framework` | Knowledge tree with treemap visualization, node detail panel, AI study plan generator |
| Questions | `/questions` | Interview question bank with company/role/type filters, LLM analysis |
| Companies | `/companies` | Company tracker with application status, interview stages, topic weight configuration |

## Components

| Component | Purpose |
|-----------|---------|
| Layout | Top-level page wrapper with sidebar |
| Sidebar | Navigation menu across pages |
| ReviewPanel | SM-2 spaced-repetition review queue for due problems |
| PracticeModal | Timed problem-solving modal with approach notes and complexity inputs |
| FrameworkTreeView | Hierarchical tree view of knowledge framework nodes |
| FrameworkTreemap | D3 treemap visualization of framework nodes by importance |
| NodeDetailPanel | Detail/edit panel for a selected framework node with study log |
| StudyPlanCard | AI-generated study plan with urgency ranking and time allocation |

## Hooks

| Hook | Purpose |
|------|---------|
| `useApi` | Generic fetch wrapper with loading/error state management |
| `useTimer` | Stopwatch hook for timing problem attempts |

## Type Definitions

Type files in `src/types/` mirror backend models: `problem.ts`, `framework.ts`,
`company.ts`, `question.ts`, `dashboard.ts`.

## Development

```bash
# Install dependencies
npm install

# Start dev server (proxies /api to localhost:8100)
npm run dev

# Production build
npm run build

# Lint
npm run lint
```

The Vite dev server runs on port 5173 and proxies `/api` requests to
`http://localhost:8100` (see `vite.config.ts`).

## Docker

```bash
# Build frontend image (serves via nginx on port 80)
docker build -t mlinterviewprep-frontend .
```

Or use `docker-compose up` from the project root to run both backend and frontend.
