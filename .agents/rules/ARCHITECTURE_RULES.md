# Architecture Rules

## Layout
```
backend/app/
  api/            routers only: validate input, call services, shape output
  services/       business logic (discovery, ads, analysis, posters)
  providers/
    ads/          one file per ad source implementing AdSource
    llm/          one file per model vendor implementing LLMClient
    images/       one file per image vendor implementing ImageClient
  models/         SQLAlchemy models
  schemas/        Pydantic request/response models
  jobs/           Celery or scheduler tasks
  core/           config, security, logging, db session
frontend/src/
  pages/ components/ api/ hooks/ styles/
```

## Rules
1. Routers never call providers directly. Router, service, provider only.
2. External vendors sit behind interfaces: `AdSource.fetch_ads(page_id|keyword, country, status)`, `LLMClient.analyze(images, text, schema)`, `ImageClient.generate(prompt, size)`. Swapping a vendor must touch one file.
3. Ad collection uses a provider chain with fallback: hosted scraper A, hosted scraper B, self-hosted Playwright, manual import. A failure falls through to the next and is logged in `scrape_runs`.
4. Every provider returns the same internal `AdRecord` schema. Normalise at the edge.
5. Deduplicate ads by `ad_archive_id`. Track `first_seen`, `last_seen`, `run_days`.
6. Download creatives into our own storage. Never hotlink platform URLs, they expire.
7. Slow work (scraping, analysis, rendering) runs as background jobs. API returns a job id and the UI polls or subscribes.
8. Cache AI analysis by ad id and content hash. Re-analyse only new or changed ads.
9. Config only through environment variables validated at startup. No hardcoded keys, URLs or model names.
10. Poster images contain no text. Text and logo are overlaid from the brand template.
11. The frontend talks only to our API. It never holds vendor keys.
