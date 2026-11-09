# Scraping Tools and Integration Plan

**Product:** Ad Desk, the AI Competitor Ad Analyzer for BrandMonk Academy
**Purpose of this document:** list every practical tool for collecting the data the product needs, say which tool does which task, and define how the tools are wired together so the Ad Desk screens always have data.

> Pricing and free-tier figures come from public tool listings checked on 9 November 2026. They change often. Re-check before launch. No tool below has been run against a real Coimbatore competitor yet, so Section 9 defines the test that decides the final order.

---

## 1. What the product needs from scraping

Each Ad Desk screen depends on a specific data task.

| Ad Desk element | Data it needs | Scraping task |
|---|---|---|
| Competitor rail (left) | Institute names, city, website, social links, Page ID | T1 Discover, T2 Enrich and resolve |
| Ad wall (centre) | Ad creatives (image/video), copy, dates, platforms, active status | T3 Meta ads |
| Run-length bar on each tile | First seen, last seen, days running | T3 plus our own tracking |
| Analysis pane | Image or video frames, copy, transcript | T3 plus T5 Media processing |
| "Needs review" chip | Confidence of the Page ID match | T2 Resolve |
| Source status text (top bar) | Health of each provider | T7 Orchestration |
| Second channel (later) | Google search, display and YouTube ads | T4 Google ads |
| Supplementary signals (later) | Organic posts, offers, fees on websites | T6 Organic and website |

The official Meta Ad Library API does not return ordinary commercial ads shown only in India, so T3 must work at website level through hosted scrapers or our own browser automation. Everything else has easier options.

---

## 2. Task-to-tool map (the short version)

| Task | Primary tool | Fallback 1 | Fallback 2 | Last resort |
|---|---|---|---|---|
| T1 Discover competitors | Apify Google Maps actor | Google Places API | Outscraper or SerpApi Maps | Manual add |
| T2 Enrich and resolve Page ID | Website crawl (Crawl4AI or Crawlee) | ScrapeCreators company search | Ad Library page search by name | User pastes Page link |
| T3 Meta ads | Apify Meta Ad Library actor | ScrapeCreators | Self-hosted Playwright | URL, CSV, HAR or screenshot import |
| T4 Google ads | SerpApi Ads Transparency engine | Apify Ads Transparency actor | Self-hosted Playwright | Manual import |
| T5 Media processing | Our own downloader plus ffmpeg | Provider-hosted media | Re-fetch on view | Screenshot upload |
| T6 Organic and website | Crawl4AI or Crawlee | Instaloader or Apify Instagram actor | ScrapeCreators | Skip |
| T7 Orchestration | Apify scheduler and webhooks, plus our Celery jobs | APScheduler | Manual refresh button | None |

**Design principle:** one hub for most tasks, a second vendor for resilience, our own code for the part that must never fail, and a human path at the end of every chain.

---

## 3. Tool catalogue by task

### T1. Discover competitors (Google Maps and local search)

| Tool | Type | What it gives | Cost and limits (as listed) | Best use here |
|---|---|---|---|---|
| **Apify Google Maps actors** (for example `compass/crawler-google-places`, `s-r/free-google-maps-scraper`, `blueorion` simplified, `gurify`, `labrat011`, `scraperlink`) | Hosted | Name, address, phone, website, rating, hours, coordinates. Some add emails and social links | Listed from about $0.25 to $5 per 1,000 places depending on actor. Free Apify plan includes about $5 of monthly credit. One actor states its free credit covers about 3,750 locations a month | **Primary.** Cheap, scriptable, same account as the Meta scraper |
| **Google Places API** (Text Search, Place Details) | Official | Clean, stable place data | Needs a Google Cloud billing account. Check current free monthly allowance and per-request prices | Fallback when actors fail, and for stable Place IDs |
| **Outscraper** | Hosted | Maps listings, optional enrichment | About $3 per 1,000 basic listings, more for enriched | Second vendor |
| **SerpApi Google Maps** | Hosted | Maps results as a search type | Roughly $0.01 to $0.025 per search on paid plans, plus a small free tier | Second vendor, simple API |
| **gosom/google-maps-scraper** | Open source CLI | Maps listings from your own machine | Free, you provide infrastructure | Zero-cost option for one-off city runs |
| **OpenStreetMap (Overpass, Nominatim)** | Open data | Rough institute locations and names | Free, coverage varies for small businesses | Cross-check only |

Queries per city: "AI course", "artificial intelligence training institute", "digital marketing course", "digital marketing institute", "UI UX design course", "graphic design and UI UX training". Merge by website domain, then by phone number, to remove duplicates.

### T2. Enrich and resolve the Facebook Page ID

The Ad Library is searched by Page ID, so a wrong match means the wrong ads. This is the most important quality step.

| Tool | Type | Use |
|---|---|---|
| **Crawl4AI** | Open source (Python) | Crawl the institute's site and read footer or header links to Facebook and Instagram. Outputs clean text for LLM fallback parsing |
| **Crawlee** (Node or Python) | Open source | Same job with built-in queueing, retries and Playwright support. Better if the crawler grows |
| **httpx plus selectolax or BeautifulSoup** | Open source | Lightest option for simple sites |
| **Apify Maps actors with contact enrichment** | Hosted | Return socials with the place record, no extra crawl |
| **ScrapeCreators company search** | Hosted API (100 free credits on signup) | Search by company name and get Page IDs |
| **Ad Library page search** | Public site | Search the institute's name and compare results |

Match confidence rule (drives the "Needs review" chip in the rail):
- **High:** the Page link found on the institute's own website equals the Page found by name search.
- **Medium:** only one source found it, or names differ slightly.
- **Low:** several similar pages, or none found. The rail shows "Needs review" and the user confirms.

### T3. Meta ads from Meta Ad Library (the core task)

**A. Hosted scrapers (no infrastructure)**

| Tool | Notes |
|---|---|
| **Apify Meta Ad Library actors** (examples seen: `jaybird/meta-ad-library-scraper`, `deepmine/meta-ad-library`, `thirdwatch/fb-ad-library-scraper`, `prodiger/facebook-ads-library-scraper-v2`, `rbbscrap/fast-facebook-ads-scraper`, `123webdata/meta-ads-library-scraper`, `s-r/meta-ads-library`, `mikolabs/facebook-ad-library-scraper`, `lergassy/meta-ad-library-scraper`, `thenetaji/meta-ads-scraper`, `bockmurat/facebook-ads-scraper-actor`, `cryptosignals/facebook-ads-library-scraper`) | Community-maintained, pay per result (one lists about $0.75 per 1,000 ads). Input is a Page ID, keyword or Ad Library URL. Output is JSON or CSV with copy, media URLs, dates and platforms. One actor's changelog describes opening a Playwright page once to capture tokens, then paging through results over plain HTTP. Quality and upkeep vary, so test several |
| **ScrapeCreators** | REST API, 100 free credits, no card. Endpoints for ad search, company search, company ads, single-ad details, and video transcripts |
| **SearchAPI** | REST API with a Meta Ad Library engine, free trial |
| **SerpApi** | REST API with Meta Ad Library support, small free tier |
| **SocialCrawl-style unified APIs** | Small free allowance, useful as a third vendor |

**B. Self-hosted**

| Tool | Notes |
|---|---|
| **Playwright** (Python) | Opens `facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&search_type=page&view_all_page_id=<ID>`, scrolls, parses cards, downloads media. Free but fragile |
| **GraphQL replay** | Capture tokens with Playwright once, then call Meta's internal ad search over HTTP. Fast but breaks when the format changes |
| **Stealth browser variants** (Patchright, Camoufox, nodriver) | Reduce automation fingerprints when plain Playwright is blocked. Evaluate only if blocking appears |
| **Residential or rotating proxies** (Bright Data, Oxylabs, Decodo, IPRoyal and others) | Needed for sustained self-hosted scraping. Paid, so keep as a later option |
| **Open-source repos** (`NiksHacks/meta-ads-library-scraper`, `skylarcheung/Facebook-Ad-Library-Scraper`, `ChrisFeldmeier/fb_ad_scraper`, `kawai-senpai/adscraper`) | Use as references or starting points. Review code and licence before adopting, and expect some to be stale |
| **Facebook Ad Library MCP servers** (for example `facebook-ad-library-mcp-cli`) | Let an AI agent run ad searches, with a free local browser default and optional hosted backends. Useful for experiments, not the production path |

**C. Official and restricted**

| Tool | Notes |
|---|---|
| **Meta Ad Library API** (`/ads_archive`) | Free with a developer account and identity confirmation. Covers political and issue ads, and ads delivered in the EU and UK. Use only as optional enrichment |
| **Meta Content Library** | Approved researchers only. Not practical here |

**D. Human-assisted**

| Tool | Notes |
|---|---|
| **Pasted Ad Library URL or ad ID** | Backend fetches that ad. Always works |
| **CSV, HAR file or screenshot upload** | Vision model extracts copy and layout. Works when every scraper is down |
| **Browser extension or bookmarklet** | Captures cards while the user browses the Ad Library and posts them to our API |

### T4. Google ads (second channel, later phase)

| Tool | Notes |
|---|---|
| **SerpApi `google_ads_transparency_center` engine** | Query by `advertiser_id`, results paginate with a token. Paid with free tier |
| **Apify Ads Transparency actors** (examples: `scrapesage`, `DevilScrapes`, `api_creators`, `lurkapi`, `dltik`, `parsebird`) | Listed from about $1.20 to $5 per 1,000 ads. Query by domain, advertiser name or ID. Some add OCR, landing-page scrape and media download. One notes Google's per-call cap of about 100 ads per advertiser, so run extra regions or date filters for large advertisers. Free plans on some actors are limited to a couple of advertisers per run |
| **Self-hosted Playwright** | Possible but not needed at this scale |

### T5. Media processing (for the analysis pane)

| Tool | Use |
|---|---|
| **httpx plus our storage (Supabase Storage or S3)** | Download images and videos immediately, because platform links expire. Store a content hash |
| **ffmpeg** | Extract key frames from video ads, one every 2 to 3 seconds, maximum 8 |
| **Whisper (open source) or the multimodal model** | Transcribe spoken audio in video ads |
| **Tesseract, PaddleOCR or EasyOCR** | Read on-image text when the vision model needs help |
| **Pillow** | Thumbnails for the ad wall (4:5 tiles) and the poster text overlay later |

### T6. Organic content and website signals (optional)

| Tool | Use |
|---|---|
| **Crawl4AI or Crawlee** | Read course pages for fees, durations, batch dates and offers to compare with the ads |
| **Instaloader** (open source) | Public Instagram profiles and posts. Rate-limited, use sparingly |
| **Apify Instagram or Facebook page actors** | Hosted alternative for public posts |
| **ScrapeCreators** | Covers several social platforms through one API |

### T7. Orchestration and integration

| Tool | Use |
|---|---|
| **Apify platform** | Scheduler, webhooks, datasets, REST API and client libraries (Python, JavaScript), integrations with n8n and Make, and an MCP server. Lets one account run Maps, Meta, Google and Instagram actors with one token and one result format |
| **Celery plus Redis** | Our background jobs: fetch, normalise, download media, enqueue analysis |
| **APScheduler** | Lighter scheduler for the first version |
| **n8n** (self-hosted or cloud) | Optional visual automation for alerts and exports |
| **Sentry or simple health logs** | Catch provider failures and schema drift |

### T8. Paid commercial ad-spy tools (for completeness)

Several paid ad-intelligence products exist, such as Foreplay, AdSpy, BigSpy and Minea. They have not been verified for coverage in India and are not needed for this build. Keep as a later option only if hosted scrapers prove unreliable.

---

## 4. Integration approaches compared

| Approach | How it works | Strengths | Weaknesses | Fit |
|---|---|---|---|---|
| **A. One hub (Apify-first)** | Apify runs T1, T3, T4 and T6 actors, we call it through one client | One token, one bill, one webhook format, schedules built in, large actor choice | Depends on community actors, one vendor | Best for speed |
| **B. Best of breed** | Different vendor per task (Places API for T1, ScrapeCreators for T3, SerpApi for T4) | Each tool chosen on merit, official APIs where they exist | More keys, more bills, more formats to normalise | Good for quality, slower to build |
| **C. Self-hosted core** | Playwright, Crawl4AI and ffmpeg on our own server | No per-result fees, full control | Maintenance, blocking, proxy cost, fragile selectors | Good as a fallback layer |
| **D. Hybrid with fallback chain (recommended)** | A as the primary hub, one B vendor as secondary, C as tertiary, human import as final | Resilient, cheap, fast to launch, no single point of failure | Needs an adapter layer and a normalised schema | **Chosen** |

---

## 5. Recommended configuration (the chain)

```yaml
# providers.yaml (order is configurable, secrets come from environment variables)
discover:        [apify_maps, google_places, outscraper]
resolve_page:    [website_crawl, scrapecreators_company, adlibrary_name_search]
meta_ads:        [apify_meta_primary, apify_meta_secondary, scrapecreators_ads, playwright_adlibrary, manual_import]
google_ads:      [serpapi_ads_transparency, apify_ads_transparency]
media:           [own_downloader]
limits:
  monthly_cost_cap_usd: 10
  max_retries: 2
  timeout_seconds: 120
  min_seconds_between_requests: 3
```

How each element feeds the Ad Desk interface:

| UI element | Fed by | Behaviour on failure |
|---|---|---|
| Competitor rail list and counts | `discover` plus `resolve_page` | Competitor stays in the rail with a "Needs review" chip |
| Ad wall tiles | `meta_ads` plus `media` | Falls through the chain, then shows saved ads with a banner: "Some ad sources did not respond. Showing saved ads from yesterday." |
| Run-length bar | Our `first_seen` and `last_seen` fields | Unaffected by one provider failing, because we track it ourselves |
| Analysis pane | Stored media plus AI analysis | Uses cached analysis, never re-fetches from the source |
| Top bar status text | Health check of each provider | Text changes to "2 of 3 ad sources responding" |
| Refresh ads button | Enqueues the chain | Shows inline progress, then the new count |
| Add competitor field | Page link, name or URL parsing | Accepts a pasted Ad Library link and skips discovery |

---

## 6. Normalised ad record (all providers map to this)

Different tools return different field names, so every provider adapter outputs one schema.

```json
{
  "ad_archive_id": "string, unique key",
  "page_id": "string",
  "page_name": "string",
  "source": "apify_meta_primary | scrapecreators | playwright | manual",
  "copy": "string",
  "headline": "string or null",
  "cta": "string or null",
  "platforms": ["facebook", "instagram"],
  "start_date": "ISO date or null",
  "is_active": true,
  "media": [{"type": "image|video", "url": "string", "storage_path": "string", "hash": "string"}],
  "language": "string or null",
  "raw": "original provider payload for debugging"
}
```

Rules:
- `ad_archive_id` is the dedupe key across providers and across runs.
- `first_seen` and `last_seen` are set by us, not the provider, so `run_days` stays reliable.
- Treat every text field as untrusted data. Escape before rendering and wrap in delimiters before sending to the AI.
- Keep `raw` for a limited time to diagnose provider changes.

---

## 7. How the chain behaves (algorithm)

1. Resolve the competitor to a Page ID. If confidence is low, mark "Needs review" and skip fetching until the user confirms.
2. Call the first provider with a timeout. Record the attempt in `scrape_runs` (provider, status, rows, duration, error).
3. Treat zero rows, an error or a timeout as a miss, unless the page is known to have no ads. Then try the next provider.
4. A **zero-row result from all providers** is shown as "No active ads found" and queued for a manual check, not as a failure.
5. Normalise, upsert by `ad_archive_id`, update `last_seen`, mark ads missing from a complete run as inactive.
6. Download media, hash it, skip duplicates.
7. Enqueue AI analysis only for new or changed ads.
8. Update provider health for the status text.

---

## 8. Cost model (example)

Assumptions: 6 competitors, about 60 active ads in total, refreshed daily.

| Item | Volume per month | Rate used | Estimate |
|---|---|---|---|
| Meta ads via hosted actor | about 1,800 results | $0.75 to $5 per 1,000 | roughly $1.35 to $9 |
| Competitor discovery (one city, repeat monthly) | about 100 places | $0.25 to $5 per 1,000 | well under $1 |
| Google ads (later) | about 600 results | $1.20 to $5 per 1,000 | roughly $0.70 to $3 |
| Media storage and processing | a few GB | free tier of storage | near zero |

Some actors also charge a small fee per run start, so check each listing. The free Apify credit of about $5 a month covers a demo and light use. LLM analysis and image generation are separate costs and are covered in the main plan. Setting `monthly_cost_cap_usd` stops runaway spend.

---

## 9. Provider bake-off (do this before fixing the order)

Test every candidate for T3 on the same three real competitors, then fill this table.

| Measure | How to check |
|---|---|
| Coverage | Count ads by hand in the Ad Library site for the same Page and country, compare to the tool's count |
| Field completeness | Share of ads with copy, media URL, start date and platform filled |
| Media availability | Share of media URLs that still open 24 hours later |
| Speed | Seconds from request to results |
| Cost | Dollars per 100 ads including run-start fees |
| Stability | Run it on three different days and compare |
| Failure behaviour | Does it return a clear error, an empty list or wrong data |

Score each 1 to 5, pick the top two Meta providers as primary and secondary, and keep a small contract test with fixed Page IDs so a future provider change is caught early.

---

## 10. Code outline

```python
# providers/ads/base.py
from typing import Protocol

class AdSource(Protocol):
    name: str
    def fetch_ads(self, *, page_id: str | None, keyword: str | None,
                  country: str = "IN", status: str = "active",
                  limit: int = 100) -> list["AdRecord"]: ...
```

```python
# providers/ads/apify_meta.py (outline)
from apify_client import ApifyClient

class ApifyMeta:
    name = "apify_meta_primary"
    def __init__(self, token: str, actor_id: str):
        self.client = ApifyClient(token)
        self.actor_id = actor_id

    def fetch_ads(self, *, page_id=None, keyword=None, country="IN", status="active", limit=100):
        run_input = {"pageIds": [page_id], "country": country,
                     "activeStatus": status, "maxAds": limit}   # field names differ by actor
        run = self.client.actor(self.actor_id).call(run_input=run_input, timeout_secs=120)
        items = self.client.dataset(run["defaultDatasetId"]).iterate_items()
        return [to_ad_record(i, source=self.name) for i in items]
```

```python
# services/ads_service.py (outline)
def collect(competitor, chain, health):
    for provider in chain:
        try:
            ads = provider.fetch_ads(page_id=competitor.fb_page_id)
            health.record(provider.name, ok=True, rows=len(ads))
            if ads:
                return ads
        except Exception as e:
            health.record(provider.name, ok=False, error=str(e))
    return []   # triggers the "No active ads found" state, not an error
```

Input field names differ between actors. Read each actor's input schema and keep that mapping inside its own adapter file.

---

## 11. Reliability, ethics and compliance

- **Public data only.** Collect only what the Ad Library shows publicly. No logins, no private data, no personal data about viewers or commenters.
- **Terms of service.** Scraping Meta's website may breach its terms. Prefer hosted providers who take on that responsibility, keep request rates low, cache results and state this in the README. This is a technical plan, not legal advice.
- **Politeness.** Minimum delay between requests, exponential backoff, stop on repeated blocks, honour provider rate limits.
- **Schema drift.** Alert when a provider's rows suddenly drop to zero or key fields become empty. Fall through the chain automatically.
- **Secrets.** Provider tokens only in environment variables on the server, never in the frontend.
- **SSRF safety.** User-pasted links only accepted for facebook.com, instagram.com and the Google Ads Transparency domain. Block private IP ranges.
- **Originality.** Competitor creatives are analysed for strategy only. BrandMonk posters are original work.

---

## 12. Build order for the scraping layer

| Step | Deliverable | Ad Desk result |
|---|---|---|
| 1 | Adapter interface, `AdRecord`, `scrape_runs` table | Foundation |
| 2 | Apify Maps adapter plus website crawler plus resolver | Competitor rail with confidence chips |
| 3 | Apify Meta adapter plus media downloader | Ad wall with real creatives |
| 4 | Second provider (ScrapeCreators) plus chain and health check | Status text and fallback banner |
| 5 | Manual import (URL, CSV, screenshots) | Works even when all scrapers fail |
| 6 | Playwright fallback | Free tertiary source |
| 7 | Google Ads Transparency adapter | Second channel on the ad wall |
| 8 | Scheduler, alerts, cost cap | Daily refresh without clicking |

---

## 13. Final recommendation

Use the **hybrid chain**: Apify as the main hub for discovery and Meta ads, ScrapeCreators as the second vendor and Page ID helper, Playwright as the free fallback, and manual import as the guaranteed path. Run the bake-off in Section 9 first, because community actors differ in quality and the best two for Meta ads should be chosen from real results, not from listings.
