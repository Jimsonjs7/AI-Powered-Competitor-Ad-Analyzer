---
name: ad-source-provider-chain
description: Collect Facebook and Instagram ads for a competitor from Meta Ad Library using a fallback chain of hosted scrapers, self-hosted Playwright and manual import. Use for any task about fetching, normalising or storing ads.
---
# Ad source provider chain

## Why
Meta's official Ad Library API does not return ordinary commercial ads shown only in India. The public Ad Library site does, so collection works at website level.

## Interface
```python
class AdSource(Protocol):
    name: str
    def fetch_ads(self, *, page_id: str | None, keyword: str | None,
                  country: str = "IN", status: str = "active", limit: int = 100) -> list[AdRecord]: ...
```

## Chain order (configurable)
1. Apify actor for Meta Ad Library (free monthly credit, run via apify-client)
2. ScrapeCreators (company search resolves Page ID, company ads endpoint, ad details, video transcript)
3. Self-hosted Playwright on `facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&search_type=page&view_all_page_id=<ID>`
4. Manual import: pasted Ad Library URL, CSV, HAR file or screenshots (vision extraction)

## Steps
1. Resolve the competitor to a Facebook Page ID (website footer link, provider company search, or Ad Library page search).
2. Call providers in order. Move on when a provider errors, times out, or returns zero rows. Record each attempt in `scrape_runs` (provider, status, rows, error, duration).
3. Normalise to `AdRecord`: `ad_archive_id, page_id, page_name, copy, headline, cta, platforms, start_date, is_active, media[]`.
4. Upsert by `ad_archive_id`. Update `last_seen`. Mark ads missing from a full run as inactive.
5. Download media into storage, store a content hash, skip duplicates.
6. Enqueue AI analysis only for new or changed ads.

## Rules
- Public data only, low request rate, exponential backoff, per-provider monthly cost cap.
- Provider actors differ in quality. Keep a small contract test with a fixed Page ID for each provider.
- A page with zero active ads is a valid result. Show it as such.
- Never expose provider tokens to the frontend.
