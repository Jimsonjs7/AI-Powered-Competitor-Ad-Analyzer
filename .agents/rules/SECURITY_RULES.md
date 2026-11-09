# Security Rules (backend)

## Secrets and config
- All keys (Apify, ScrapeCreators, Google Places, LLM, image, database) live in environment variables. Provide `.env.example` with names only. `.env` is gitignored.
- Never log keys, tokens, full request bodies or raw provider responses containing credentials.

## Authentication and access
- Every route except health check requires authentication (JWT or Supabase Auth). Short-lived access tokens, httpOnly refresh cookie.
- Role checks on the server for each action. Never trust a role sent by the client.
- Object-level checks: a user can only read or change their own competitors, brand kit and posters.

## Input and output
- Validate every input with Pydantic: types, lengths, enums. Reject unknown fields.
- Validate and normalise URLs. For any user-supplied URL, allow only `https` and the hosts `facebook.com`, `www.facebook.com`, `instagram.com`. Block private IP ranges and localhost to prevent SSRF.
- Use parameterised queries through the ORM only. No string-built SQL.
- Uploads (CSV, HAR, screenshots): check size, MIME type and magic bytes, cap rows, parse in a sandboxed worker, never execute content, store under random names.
- Escape or sanitise all scraped text before storing or rendering. Treat ad copy as untrusted data.

## Prompt-injection safety (AI)
- Scraped ad text and OCR output are data, never instructions. Wrap them in clearly delimited blocks and tell the model to ignore commands inside them.
- Force structured JSON output and validate it against the schema. Reject and retry on mismatch.
- The model gets no tools and no secrets. Never let analysis output trigger actions directly.

## Network and abuse
- Strict CORS allow-list (our frontend origin only). HTTPS only, HSTS.
- Rate-limit by user and IP, with tighter limits on discovery, scraping and generation endpoints.
- Set timeouts and retry limits on all outbound calls. Cap monthly spend per provider and alert near the cap.
- Respect the source site: low request rate, backoff on errors, public data only.

## Data protection
- Store only public advertiser-level ad data. No personal data of viewers or commenters.
- Signed, expiring URLs for private storage objects.
- Dependencies pinned, scanned in CI (`pip-audit`, `npm audit`). No unreviewed packages.

## Release gate
Run `workflows/security-check.md` before finishing any backend task.
