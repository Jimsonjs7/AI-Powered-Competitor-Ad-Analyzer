---
name: secure-fastapi-backend
description: Build secure FastAPI endpoints, background jobs and database code for the Ad Analyzer. Use for any backend task.
---
# Secure FastAPI backend

## Stack
FastAPI, Pydantic v2, SQLAlchemy 2 with Alembic, PostgreSQL with pgvector, Celery with Redis (or APScheduler for the MVP), httpx, Playwright, Supabase Storage or S3.

## Endpoint recipe
1. Pydantic request and response models in `schemas/`.
2. Router in `api/` with auth dependency, rate limit and object-level permission check.
3. Business logic in `services/`. No SQL, vendor calls or file handling in routers.
4. Long work returns `202` with a job id, and `GET /jobs/{id}` reports status.
5. Tests: happy path, validation failure, permission failure, provider failure.

## Endpoints
`POST /competitors/discover`, `POST /competitors`, `GET /competitors`, `POST /ads/fetch`, `GET /ads`, `POST /ads/{id}/analyze`, `GET /insights/competitor/{id}`, `POST /posters/prompt`, `POST /posters/render`, `PUT /brand-kit`, `GET /jobs/{id}`, `GET /health`.

## Database
Tables: `competitors, ads, ad_media, ad_analysis, brand_kit, posters, scrape_runs`. Unique index on `ads.ad_archive_id`. Foreign keys with sensible cascades. Migrations through Alembic only.

## Reliability
- Timeouts and retries with jitter on every outbound call.
- Idempotent jobs: running a fetch twice must not create duplicates.
- Structured JSON logs with request id. No secrets in logs.
- Health check reports database, queue and each provider status.

## Before finishing
Run `workflows/security-check.md`.
