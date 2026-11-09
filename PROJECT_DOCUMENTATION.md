# Project Documentation: Ad Desk (BrandMonk Ad Analyzer)

## 1. Project Overview
Ad Desk is an AI-powered competitor ad intelligence and creative generation web application built for BrandMonk Academy. It finds local training institute competitors (in Coimbatore, Kochi, Bengaluru, etc.), gathers active Facebook and Instagram ads from Meta Ad Library through a resilient fallback provider chain, analyses the persuasion mechanics and creative strategy with multimodal AI, and generates original strategy-inspired poster prompts and rendered posters for BrandMonk Academy.

## 2. Tech Stack
- Backend: Python 3.14 / FastAPI, Pydantic v2, SQLAlchemy 2, SQLite (dev) / PostgreSQL (prod), httpx, Pillow, uv package manager
- Ad Collection: Hybrid provider chain (Apify Meta actors with multi-key failover pool, ScrapeCreators, self-hosted Playwright fallback, manual import)
- Background Jobs: AsyncIO background scheduler daemon (`backend/app/jobs/scheduler.py`) for automated ad scraping, media caching, and AI analysis
- AI Analysis: Google Gemini (`gemini-3.5-flash-lite`) with multi-key failover pool and structured JSON schemas
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
|   |   |-- jobs/            (automated scraping and analysis scheduler)
|   |   |-- models/          (SQLAlchemy database tables: Competitor, Ad, Media, Analysis, Poster, ScrapeRun)
|   |   |-- providers/
|   |   |   |-- ads/         (AdSource protocol implementations: Apify, ScrapeCreators, Playwright, Manual)
|   |   |   |-- images/      (ImageClient protocol implementations)
|   |   |   `-- llm/         (LLMClient protocol implementations: Gemini 3-key pool)
|   |   |-- schemas/         (Pydantic request and response models)
|   |   `-- services/        (competitor, ad collection, analysis, poster services)
|   |-- tests/               (unit and integration contract tests)
|   |-- pyproject.toml       (uv / hatchling build and pytest config)
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
- `backend/app/providers/ads/apify_meta.py`: Apify Meta Ad Library actor adapter with 3-key failover pool
- `backend/app/jobs/scheduler.py`: Automated ad collection, creative download, and AI analysis scheduler
- `backend/app/services/ad_service.py`: Provider fallback chain orchestrator and deduplication engine
- `backend/app/services/competitor_service.py`: Dynamic database-backed competitor queries and Page ID resolver
- `backend/app/core/config.py`: Environment validation, cost caps, and multi-key rotation pools
- `frontend/src/App.tsx`: Three-pane desktop workspace (Rail, Wall, Pane) and responsive view

## 5. Setup & Running Process
### Prerequisites
Ensure `.env` in the project root contains your API keys:
```bash
GEMINI_API_KEY=your_primary_gemini_key
GEMINI_API_KEY_2=your_backup_gemini_key
GEMINI_API_KEY_3=your_third_gemini_key

APIFY_API_TOKEN=your_primary_apify_token
APIFY_API_TOKEN_2=your_backup_apify_token
APIFY_API_TOKEN_3=your_third_apify_token
```

### Running Backend with uv
`uv` is pre-installed at `~/.local/bin/uv`.
1. Navigate to backend:
   ```bash
   cd backend
   ```
2. Start server:
   ```bash
   uv run python run.py
   ```
   Server starts at `http://localhost:8000` with Swagger UI at `http://localhost:8000/docs`.
3. Run tests:
   ```bash
   uv run pytest tests/
   ```

### Running Automated Scraping Scheduler
You can run the scraping & AI analysis scheduler as a standalone automated job:
- Single execution run:
  ```bash
  cd backend && uv run python -m app.jobs.scheduler --once
  ```
- Continuous background daemon (cycles every 24 hours):
  ```bash
  cd backend && uv run python -m app.jobs.scheduler --daemon
  ```
- Or enable in FastAPI lifespan by setting `AUTO_SCRAPE_ENABLED=true` in `.env`.

### Running Frontend
1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Start Vite development server:
   ```bash
   npm run dev
   ```
   Web interface opens at `http://localhost:5173`.
3. Build for production:
   ```bash
   npm run build
   ```

## 6. End-to-End Automated Workflow
1. **Competitor Onboarding**: Add competitor name, Facebook Page link, or Meta Ad Library link in the sidebar. The resolver detects the Page ID or creates a tracking record with verification status.
2. **Automated Scraping**: The scheduler loops through active competitors, passes Page IDs/URLs to Apify with multi-key failover, normalizes ad cards, downloads media to `./media_storage/creatives/`, and saves deduplicated records by `ad_archive_id`.
3. **Automated AI Analysis**: Every new ad is automatically sent to the Gemini 3-key pool (`gemini-3.5-flash-lite`). The AI extracts the hook, offer, target audience, persuasion tactics, and why it works, scoring effectiveness from 0-100.
4. **Dynamic Market Insights**: Ad Desk aggregates live database ads by city, computing dominant hook frequencies, course distributions, and underserved course gaps.
5. **BrandMonk Poster Generation**: Choose an ad to examine in the detail pane, click to generate a BrandMonk angle, review the prompt, and render a branded creative badge and overlay.
