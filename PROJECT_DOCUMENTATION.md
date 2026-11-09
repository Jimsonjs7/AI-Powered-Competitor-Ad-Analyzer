# Project Documentation: Ad Desk (BrandMonk Ad Analyzer)

## 1. Project Overview
Ad Desk is an AI-powered competitor ad intelligence and creative generation web application built for BrandMonk Academy. It finds local training institute competitors (in Coimbatore, Kochi, Bengaluru, etc.), gathers active Facebook and Instagram ads from Meta Ad Library through a resilient fallback provider chain, analyses the persuasion mechanics and creative strategy with multimodal AI, and generates original strategy-inspired poster prompts and rendered posters for BrandMonk Academy.

## 2. Tech Stack
- Backend: Python 3.14 / FastAPI, Pydantic v2, SQLAlchemy 2, SQLite (dev) / PostgreSQL (prod), httpx, Pillow
- Ad Collection: Hybrid provider chain (Apify Meta actors, ScrapeCreators, self-hosted Playwright fallback, manual import)
- AI Analysis: Google Gemini / Anthropic Claude multimodal models with structured JSON schemas
- Poster Generation: Pillow canvas overlay engine with clean AI-generated backgrounds
- Frontend: React 18, Vite, TypeScript, Tailwind CSS with design tokens, TanStack Query
- Architecture Pattern: Router -> Service -> Provider (providers hidden behind protocols)

## 3. Folder Structure
```
.
|-- .agents/
|   |-- rules/               (general, architecture, security, design)
|   |-- skills/              (ad-analysis, ad-source, poster-gen, dashboard-ui, backend)
|   `-- workflows/           (feature workflow, security check)
|-- backend/
|   |-- app/
|   |   |-- api/             (FastAPI route endpoints, dependency injection)
|   |   |-- core/            (config, security, database session, logging)
|   |   |-- models/          (SQLAlchemy database tables)
|   |   |-- providers/
|   |   |   |-- ads/         (AdSource protocol implementations)
|   |   |   |-- images/      (ImageClient protocol implementations)
|   |   |   `-- llm/         (LLMClient protocol implementations)
|   |   |-- schemas/         (Pydantic request and response models)
|   |   `-- services/        (competitor, ad collection, analysis, poster services)
|   |-- tests/               (unit and integration contract tests)
|   |-- requirements.txt
|   `-- run.py
|-- frontend/
|   |-- src/
|   |   |-- api/             (typed HTTP client for backend endpoints)
|   |   |-- components/      (TopBar, CompetitorRail, AdWall, DetailPane, PosterStudio)
|   |   |-- hooks/           (query hooks and keyboard navigation)
|   |   |-- styles/          (Tailwind configuration and CSS tokens)
|   |   |-- types/           (TypeScript interfaces matching Pydantic schemas)
|   |   |-- App.tsx
|   |   `-- main.tsx
|   |-- index.html
|   |-- package.json
|   |-- tsconfig.json
|   `-- vite.config.ts
|-- docs/                    (architecture and integration specs)
|-- ad-desk-ui.html          (reference visual design)
|-- Scraping_Tools_and_Integration_Plan.md
|-- PROJECT_DOCUMENTATION.md
|-- PROJECT_HISTORY.md       (gitignored local log)
`-- README.md
```

## 4. Important Files
- `ad-desk-ui.html`: Authoritative reference design and design system notes
- `Scraping_Tools_and_Integration_Plan.md`: Ad scraping strategy, provider chain, and normalized schema
- `backend/app/schemas/ad.py`: Normalized `AdRecord` contract across all providers
- `backend/app/providers/ads/base.py`: `AdSource` protocol
- `backend/app/services/ad_service.py`: Provider fallback chain orchestrator
- `backend/app/core/config.py`: Environment validation and cost caps
- `frontend/src/App.tsx`: Three-pane desktop workspace (Rail, Wall, Pane) and responsive view

## 5. Setup Process
### Backend Setup (Recommended: uv)
`uv` is pre-installed on this machine at `~/.local/bin/uv`.
1. Navigate to `backend/`
2. Sync dependencies: `uv sync` (or `~/.local/bin/uv sync`)
3. Run dev server: `uv run python run.py` (serves on `http://localhost:8000`)
4. Run tests: `uv run pytest tests/`

### Backend Setup (Alternative: standard pip)
1. Navigate to `backend/`
2. Create and activate virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run dev server: `python run.py`

### Frontend Setup
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev` (serves on `http://localhost:5173`)

## 6. Current Workflow
1. Competitor Discovery & Resolution: Add competitor name or Facebook Page URL; system verifies Page ID with confidence rating.
2. Ad Collection: Ad fetch job iterates through configured provider chain, normalizes payloads into `AdRecord`, downloads media locally, and computes running days.
3. Analysis: Multimodal model scores ad effectiveness (0-100), extracts hooks, offers, tactics, and BrandMonk opportunities.
4. Poster Studio: User selects an ad angle (Outcome, Proof, Urgency) and course, reviews prompt, and generates BrandMonk branded creative with dynamic overlay.

## 7. Known Limitations
- Meta Ad Library does not offer a free commercial API for India; collection relies on hosted scrapers or browser replay.
- External scraping runs are subject to provider availability; cached ads and offline fallbacks are served during provider outages.

