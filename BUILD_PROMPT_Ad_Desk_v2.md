# Build Prompt: Ad Desk v2 (profile-driven competitor intelligence)

Paste everything below the line into your coding agent.

---

## 0. Role and ground rules

You are a senior full-stack engineer extending an **already initialized project**: Ad Desk, an AI competitor-ad analyzer for a business such as a digital marketing company or a training academy.

Before writing any code:
1. Read `.agents/GEMINI.md` and every file it references (rules, skills, workflows). Follow them. Autonomy tiers apply: do not ask permission for small edits, reads, tests or new files inside the project. Ask only for high-impact actions.
2. Inspect the existing repo (structure, stack, models, routes, components, `PROJECT_DOCUMENTATION.md`, `PROJECT_HISTORY.md`). **Reuse the existing stack and patterns. Do not restructure or replace what already works.** Where the repo differs from the `.agents` files, follow the repo and note the difference in `PROJECT_HISTORY.md`.
3. Keep the visual design from `ad-desk-ui.html`: light theme, teal accent `#0A7C6E`, Public Sans, three-pane Ad Desk layout, sentence case, **no emoji, no gradients**, all states (loading, empty, error, partial, success).
4. Never invent data. Anything shown with sample data must be labelled as sample. State what you tested and what you did not.

Work in the phases in section 9. After each phase: run lint and tests, run the security check workflow for backend changes, update `PROJECT_HISTORY.md`, and give me a short report (what changed, what was tested, what is next).

---

## 1. The new workflow (what the product must do)

1. **Set up the business profile.** The user enters who they are: business type, services or courses, location, website and public social accounts, brand details and approved claims.
2. **Run the competitor agent.** From the profile, the agent finds nearby competitors in the same domain, resolves their Facebook and Instagram pages, and collects their ads and public customer feedback.
3. **Review and filter.** The user sorts and filters competitors (nearest first, most ads, longest-running ads and more).
4. **Check data is sufficient.** Analysis only runs on a competitor once minimum data figures are met, so no conclusion rests on two comments.
5. **Find each competitor's drawbacks.** AI lists the major weaknesses of each competitor and the ads they run, each with counts and evidence.
6. **Turn weaknesses into leads for us.** AI finds the questions and concerns people raise (for example unclear fees, doubts about placement, batch timing), ranks them, and drafts ad angles and posters from our profile that answer those concerns directly, so the audience who has the doubt chooses us.

---

## 2. Phase A: Business profile configuration

Add a **Profile** area (first-run wizard plus a settings page with a completeness meter). Store handles and URLs only. **Never store passwords or ask for social media logins.**

### Fields (my recommendation, implement all, mark the core ones required)

**Identity (required)**
- Business name, short description, tagline
- Business type (multi-select): digital marketing agency, training academy, UI/UX school, AI institute, coaching centre, other
- Domains of work (tags), for example AI, digital marketing, UI/UX

**Offer (required)**
- Services or courses list. For each: name, short description, fee or fee range, duration, mode (online, offline, hybrid), batch type, next batch date, outcomes
- Unique selling points
- **Approved claims list**: facts the ads are allowed to state (for example "12-week course", "weekly mentor review"). The AI may only use claims from this list. Each claim has an optional proof link or note.
- Proof points: student count, placement numbers, certifications, awards, review links

**Location (required)**
- Address, city, area, latitude and longitude (from a map picker or geocoding)
- Service radius presets: 5, 10, 25, 50 km, or whole city, or whole state, or online-only

**Online presence**
- Website URL
- Facebook Page URL, Instagram handle, YouTube channel, LinkedIn page, Google Business Profile URL, WhatsApp number or link, contact form or landing page URL
- Validate each URL (allow-listed hosts only) and show "Verified" only after the page is fetched and matches the handle

**Audience and positioning**
- Target audience (age band, background such as students, graduates, working professionals, business owners)
- Price positioning (budget, mid, premium)
- Languages used in marketing (English, Malayalam, Tamil, Hindi and others)
- Tone of voice

**Brand kit**
- Logo upload, brand colours, fonts, poster style notes

**Marketing goals**
- Primary goal (enquiries, demo bookings, enrolments)
- Monthly ad budget range
- Preferred call to action and contact method

**Competitor control**
- Seed competitors the user already knows
- Exclusion list (businesses to ignore)

**Analysis settings**
- Minimum data thresholds (see section 4), with sensible defaults the user can change

### Smart behaviour
- **Auto-fill from our own website:** crawl the user's website (Crawl4AI or Crawlee, or the crawler already in the repo), propose services, fees, USPs and contact details, and let the user accept or edit each suggestion. Never save a suggestion without confirmation.
- Show a completeness meter and say which missing fields weaken the results (for example "Add fees and the AI cannot draft price-led ads").
- Profile versioning: keep history so earlier analyses show which profile version they used.

---

## 3. Phase B: Competitor discovery agent

An asynchronous job started from a **Find competitors** button. It must be resumable, cancellable and idempotent, and show live progress in the interface (server-sent events or polling) with plain status text such as "Searching Google Maps", "Matching Facebook pages (4 of 11)", "Collecting ads".

### Steps
1. **Build search terms** from the profile (business type, services, domains, language), for example "digital marketing course", "AI training institute", "UI UX design institute".
2. **Discover places** within the radius around the profile location using the provider chain: Apify Google Maps actor first, then Google Places API, then Outscraper or SerpApi. Compute distance from the profile location.
3. **Discover advertisers** with Ad Library keyword search for the same domain terms (country India), to find businesses that advertise but rank low on Maps.
4. **Merge and dedupe** by website domain, then phone, then name similarity. Remove the user's own business and the exclusion list. Add seed competitors.
5. **Resolve Facebook Page ID and Instagram handle** from each website (footer and header links), then provider company search, then Ad Library page search. Store a match confidence (high, medium, low). Low confidence shows "Needs review" in the interface.
6. **Collect ads** per competitor using the provider chain already defined in `Scraping_Tools_and_Integration_Plan.md`: hosted Meta Ad Library actor, second vendor, Playwright fallback, manual import. Track `first_seen`, `last_seen` and `run_days` ourselves.
7. **Collect public customer evidence** (see section 5).
8. Save a `discovery_run` record with the profile version, filters, radius, providers used, counts and cost.

Respect the cost cap, timeouts, retries and request delays from the config. A failed provider falls through to the next and is shown in the status text.

---

## 4. Phase C: Results, sorting, filtering and minimum figures

### Competitor list (table) with a filter panel and saved views

**Sort by:** nearest first, most active ads, longest-running ad, newest ad, highest rating, most reviews, most overlap with our services, highest weakness score, highest threat score.

**Filter by:** distance radius, area or city, business type, service overlap, has active ads (yes or no), minimum active ads, ad platform (Facebook, Instagram), running days range, rating range, review count, language of ads, price range if known, online or offline, data sufficiency status.

Add a **map view** beside the list, using the same filters.

### Figures shown per competitor
Distance, active ads, new ads this week, longest-running ad in days, rating, review count, share of negative reviews, comments collected, top objection count, **data sufficiency status**.

### Minimum data thresholds (configurable, defaults below)
A competitor is analysed for weaknesses only when at least one of these evidence sets passes. Otherwise it shows "Not enough data yet" and lists exactly what is missing.

| Evidence | Default minimum |
|---|---|
| Active ads | 3 |
| Public reviews | 20 |
| Public comments on ad-linked or page posts | 15 |

Every AI statement must carry its **sample size and confidence**: high (30 or more items), medium (10 to 29), low (fewer than 10). Low-confidence findings are shown but marked and never ranked above medium or high ones.

---

## 5. Phase D: Evidence collection (where drawbacks come from)

**Important limits you must design around:**
- The Meta Ad Library does **not** show comments on ads. Comments are only available when the ad creative is also a **public Facebook or Instagram post**, or from the competitor's public page posts. Ads that run only as unpublished ad posts have no accessible comments.
- Facebook comment scrapers work on **public posts only**, and some return only the most relevant handful of comments without a login. Instagram replies cannot be downloaded.
- So the product collects evidence from several sources and always says which source each finding came from.

### Evidence sources (all public, all stored as `evidence_items`)
1. **Google Maps reviews** of the competitor (Apify Google Maps reviews actor or equivalent). Best source for service complaints.
2. **Public post comments** on the competitor's Facebook and Instagram posts, especially posts matching their ads (Apify Facebook comments actors, a multi-platform social comments actor, or ScrapeCreators). Best source for pre-purchase questions and doubts.
3. **Ad copy and creative gaps**: what each ad does not say (no fee, no dates, no proof, no clear call to action, vague outcome).
4. **Website gaps**: missing fees, syllabus, schedule, contact route or trust proof.
5. **Manual input**: user pastes comments, uploads screenshots, or adds notes. This always works when scrapers do not.

Pick the comment and review providers through the same bake-off method as the ad providers and keep them behind the provider interface.

### Privacy rules (mandatory)
- Public data only. No logins, no private groups.
- **Do not store commenter names, profile links or photos.** Store the text, date, source, ad or post link and a one-way hash only.
- Use the data to understand market concerns. **Do not build features to message, tag or retarget individual commenters.**
- Set a retention limit (default 90 days) and a delete-on-request path.
- Treat all comment and review text as untrusted. Wrap it in delimiters for the model and ignore any instruction inside it.

---

## 6. Phase E: AI weakness analysis ("major drawbacks")

For each competitor that passes the thresholds, run structured analysis over the evidence and ads and return validated JSON. Use the existing LLM interface and caching.

### Categories
pricing clarity, trust and proof, placement or outcome claims, schedule and batch clarity, teaching quality, student support and response time, location and access, course relevance, refund or terms, and "other".

### Output per drawback
```json
{
  "category": "pricing_clarity",
  "summary": "Fees are not shown in ads and many commenters ask for the price.",
  "evidence_count": 14,
  "sample_size": 52,
  "share_percent": 27,
  "confidence": "medium",
  "severity": 4,
  "sources": ["ad_comments", "google_reviews", "ad_copy"],
  "linked_ad_ids": ["..."],
  "example_paraphrases": ["asks for the fee", "asks whether there is EMI"],
  "competitor_ad_gap": "No ad mentions a price."
}
```

Rules:
- Every number comes from the data, never from the model's guess. Compute counts and shares in code, then let the model write the summary from those numbers.
- Show a **weakness score** per competitor (weighted frequency, severity and confidence) with the breakdown visible, never a bare number.
- Handle mixed languages (English, Malayalam, Tamil, Hindi, and romanised versions) in the model prompt.
- In the **ad analysis pane**, add a section "What people ask under this ad" with the top questions and counts, when comment evidence exists for that ad.

---

## 7. Phase F: Opportunity engine (turn concerns into leads for us)

1. **Cluster** objections and questions across all competitors (embeddings plus category). A concern that appears across two or more competitors is a **market-wide objection**.
2. **Score** each cluster: frequency, intensity (strength of wording and reaction counts), breadth (number of competitors), competitor ad running days (a sign the audience is being bought at scale), and **fit with our profile** (can we honestly answer it with approved claims?).
3. Produce **Opportunity cards**, ranked, each with:
   - The concern in plain words and the evidence (counts, sample size, confidence, sources)
   - Why it matters (what it costs the competitor)
   - **Our counter-angle**, built only from the approved claims and proof points
   - Recommended ad format (static poster, carousel, short video script, FAQ-style ad)
   - Three headline options, primary text, call to action, and a landing-page section suggestion
   - **Missing proof**: if the profile lacks a claim needed for this angle, say so and ask the user to add it (for example "Add placement numbers to use the placement-doubt angle")
4. **Answer-first ad pattern**: the strongest ads here lead with the concern as the headline and answer it immediately ("Fees unclear? Full fee, dates and syllabus inside"). Support this pattern in the draft generator.
5. Send an opportunity to the **Poster and ad studio** with one click. Reuse the existing prompt builder and overlay approach: image models draw no text, and text and logo come from the brand template.
6. A human review step is required before any draft is exported. The AI must not state a fee, date, number or guarantee that is not in the approved claims.

---

## 8. Data model additions (adapt to the existing ORM and migration tool)

- `business_profiles` (id, owner, version, name, description, type[], domains[], location, radius, languages[], tone, goals, thresholds)
- `profile_services` (profile_id, name, description, fee_min, fee_max, duration, mode, next_batch)
- `profile_claims` (profile_id, text, proof_link, approved)
- `profile_social_accounts` (profile_id, platform, url_or_handle, verified)
- `discovery_runs` (id, profile_version, radius, filters, status, providers_used, counts, cost, started_at)
- `competitors` (add: lat, lng, distance_km, area, match_confidence, fb_page_id, ig_handle, data_status)
- `competitor_metrics` (competitor_id, active_ads, new_this_week, longest_run_days, rating, review_count, negative_share, comment_count, weakness_score, threat_score, computed_at)
- `evidence_items` (id, competitor_id, ad_id nullable, source, text, language, sentiment, category, text_hash, collected_at)
- `weaknesses` (competitor_id, category, summary, evidence_count, sample_size, share_percent, confidence, severity)
- `objection_clusters` (id, label, category, total_count, competitor_count, intensity)
- `opportunities` (id, cluster_id, score, counter_angle, formats[], headlines[], primary_text, missing_proof[], status)
- `saved_views` (user, name, filters, sort)

### Endpoints to add (follow existing routing and auth patterns)
`PUT /profile`, `GET /profile`, `POST /profile/autofill`, `POST /discovery/run`, `GET /discovery/{id}/events`, `POST /discovery/{id}/cancel`, `GET /competitors` (sort and filter query params), `GET /competitors/{id}`, `POST /competitors/{id}/analyze`, `GET /competitors/{id}/weaknesses`, `GET /opportunities`, `POST /opportunities/{id}/draft`, `POST /evidence/import` (paste, CSV, screenshot), `GET/POST /views`.

---

## 9. Phases and acceptance criteria

| Phase | Deliverable | Done when |
|---|---|---|
| A | Profile wizard, settings page, completeness meter, website auto-fill | A user can complete a profile, accept or edit suggestions, and see which gaps limit results |
| B | Discovery agent with live progress, provider chain and Page ID matching | A run around the profile location returns deduped competitors with distance and match confidence, and survives one provider failing |
| C | Sortable and filterable competitor list, saved views, map view, figures, sufficiency status | Every sort and filter works on real stored data and the empty state explains what to change |
| D | Evidence collection and manual import | Reviews and public comments are stored without personal identifiers, and each item shows its source |
| E | Weakness analysis with counts, confidence and linked ads | Every claim traces to counted evidence, and thresholds block thin data |
| F | Opportunity cards and answer-first drafts into the poster studio | Top market-wide objections are ranked, drafts use only approved claims, missing proof is flagged |
| G | Scheduling, alerts (new competitor ad, price or offer change), weekly digest | Daily refresh works within the cost cap |

Cross-cutting acceptance:
- All new screens match the Ad Desk design rules, work at 360 px, and are keyboard accessible.
- Every list has loading, empty, error and partial states.
- No secrets in code or logs. Security check workflow passes. Comment and review text never rendered as HTML.
- Tests cover profile validation, distance and filter logic, threshold gating, objection scoring, claim enforcement, and each provider failure path.
- `PROJECT_DOCUMENTATION.md` updated for the new workflow and endpoints.

---

## 10. Extra recommendations to include (my additions)

1. **Evidence-first AI.** Counts and shares are computed in code. The model only writes words around real numbers.
2. **Approved claims as a hard guardrail.** Draft generation can only use claims the business has approved, which protects the brand from false promises.
3. **Market-wide objections first.** A concern shared by several competitors is the safest big bet for a new ad.
4. **Threat score and weakness score separately.** A strong competitor with one weakness may matter more than a weak one with many.
5. **Change alerts.** Notify when a competitor launches a new ad, drops a long-running one, or changes a price.
6. **Learning loop (later phase).** Let the user log how each counter-ad performs (spend, enquiries) so the tool learns which angles convert and re-ranks opportunities.
7. **Weekly digest.** One short summary of new competitors, new ads, rising objections and the top three opportunities.
8. **Radius presets and area names.** Show results by neighbourhood as well as distance, since local buyers think in areas.
9. **Compliance note in drafts.** Remind the user to follow advertising rules and not to make unverifiable claims.

---

## 11. What to report back after each phase

- Files and tables changed
- What was run and tested, with results
- What could not be tested (for example a provider without a key) and what is needed
- Assumptions made
- The next phase and anything blocking it
