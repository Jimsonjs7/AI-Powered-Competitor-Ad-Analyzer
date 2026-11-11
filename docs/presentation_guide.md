# BrandMonk Academy: AI Competitor Ad Analyzer — Complete Presentation & Demo Walkthrough

This presentation guide covers **every menu, tab, button, modal, and data visualization** across the entire application, with exact instructions on what to click, what appears on screen, how the underlying AI and scraping engines operate, and the exact words to speak during a presentation.

---

## Visual Presentation Roadmap

````carousel
![By Company Category View - Nexora Academy](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/by_company_category_view.png)
<!-- slide -->
![Ad Wall with Real Ad Creatives](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/ad_wall_real_images.png)
<!-- slide -->
![Ad Detail Pane with Why It's Attractive Highlight](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/ad_detail_pane.png)
<!-- slide -->
![Creative Counter-Ad Modal](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/creative_counter_ad_modal.png)
<!-- slide -->
![Competitors Directory Table](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/competitors_table_view.png)
<!-- slide -->
![Opportunities Objection Engine](/home/jims/.gemini/antigravity/brain/26632a49-1c98-4d64-b3ed-cfd4a08ffc68/opportunities_view.png)
````

---

## 1. Executive Introduction & Context

### What to say:
> *"Good morning/afternoon. Today I am presenting **Ad Desk**, the AI-powered Competitor Ad Intelligence and Creative Generation System built specifically for **BrandMonk Academy**.*
>
> *BrandMonk Academy provides professional courses in **Artificial Intelligence**, **Digital Marketing**, and **UI/UX Design** in Coimbatore. Local training institutes actively run ads on Facebook and Instagram to capture student enrollments. Until now, tracking them meant manually searching Meta Ad Library, guessing how long their ads had been running, and guessing why their ads were converting.*
>
> *Ad Desk solves this completely: it discovers our competitors, automatically collects their live Facebook and Instagram ads using a resilient Apify scraping chain, uses Google Gemini Multimodal AI to decode why their ads are attractive, and generates original, brand-safe counter-posters for BrandMonk."*

---

## 2. Top Bar Controls & Live Health Status

### Where to look:
The top navigation bar across the very top of the application.

```
[Logo: Ad Desk]  [Ad Wall] [By Company] [Competitors] [Opportunities] [Profile 55%]  ...  (• All 3 ad sources responding)  [City: Coimbatore v]  [Find competitors]  [Refresh ads]
```

### Button-by-Button Walkthrough:

1. **Brand Logo & Mark (`Ad Desk`)**:
   - **Clicking it**: Resets filters and returns directly to the primary **Ad Wall**.
   - **Speaking point**: *"Our design strictly follows BrandMonk's light theme: clean surfaces, zero visual clutter, and instant keyboard-accessible navigation."*

2. **Primary Navigation Tabs (`Ad Wall` | `By Company` | `Competitors` | `Opportunities` | `Profile`)**:
   - **Speaking point**: *"Every stage of the competitive workflow is mapped to a primary tab—from raw ad discovery to institutional dossiers and creative generation."*

3. **Live Health Status (`• All 3 ad sources responding`)**:
   - **Speaking point**: *"This green health beacon confirms our scraping pipelines are active. If Meta changes an endpoint or a provider experiences downtime, our automatic failover kicks in without human intervention."*

4. **City Selector Dropdown (`Coimbatore` | `Kochi` | `Bengaluru`)**:
   - **Clicking it**: Selects **Coimbatore**. The entire dataset, market insights, and ad inventory recalibrate to Coimbatore training institutes.

5. **`Refresh ads` Button (Primary Teal Button)**:
   - **Clicking it**: Triggers an on-demand crawl across all competitor Facebook Page IDs, runs media downloads with SHA-256 caching, runs Gemini multimodal analysis on new ads, and updates the view.

---

## 3. Business Profile & Hard Guardrail Setup (`Profile` Tab)

### How to navigate:
Click the **Profile** tab in the top bar.

### Screen Elements & Controls:

1. **Profile Completeness Progress Bar**:
   - Shows current onboarding score (e.g. `55%`) with missing field guidance.
2. **Tab 1: `Identity`**:
   - BrandMonk Academy name, tagline, domains (*AI, Digital Marketing, UI/UX*), tone (*Confident & Practical*).
3. **Tab 2: `Courses & Services`**:
   - Catalog of BrandMonk's programs, duration (12 weeks), fees, and batch limit (15 students).
4. **Tab 3: `Approved Claims (Hard Guardrail)`** ⭐:
   - List of verified facts BrandMonk can legally and ethically advertise (e.g., *"100% upfront transparent fee with zero extra exam charges"*, *"Every design portfolio reviewed live by senior designers"*).
   - **Speaking point**: *"This is our hard safety guardrail. Many AI tools hallucinate false marketing claims. In Ad Desk, the creative generation engine is physically locked to our approved claims ledger. It will never generate an ad angle BrandMonk cannot prove."*
5. **Tab 4: `Location & Radius`**:
   - City (*Coimbatore*), Area (*Gandhipuram / RS Puram*), and Radius presets (**5 km**, **10 km**, **25 km**, **50 km**).
6. **Tab 5: `Online Presence & Auto-fill`**:
   - Public URLs: Website, Facebook page, Instagram profile, LinkedIn, YouTube.
   - **`Auto-fill from website`**: Automatically crawls the institute's domain to extract official course names and social media links.
   - Click **`Save profile`** to persist updates.

---

## 4. Automated Competitor Discovery Engine

### How to navigate:
Click the **`Find competitors`** button in the top navigation bar.

### Modal Elements & Walkthrough:

1. **Mode 1: `Area & Radius Discovery`**:
   - Set City to *Coimbatore*, Area to *Gandhipuram*, Radius to *10 km*, and select target courses (*AI*, *Digital marketing*, *UI/UX*).
   - Click **`Start Competitor Discovery`**:
     - The modal activates a background crawl agent.
     - Live counter chips increment: *Places found*, *Pages resolved*, *Ads collected*.
   - Click **`Run in background`**: The modal closes while a top **Background Queue Banner** continues tracking the task.

2. **Mode 2: `Direct URL / Social Crawler`**:
   - Paste any competitor website URL.
   - Click **`Crawl Website & Extract Meta Links`**: The crawler parses HTML metadata, finds embedded Facebook Page IDs and Instagram handles, and displays them for manual verification before saving.

---

## 5. The Ad Wall (`Ad Wall` Tab)

### How to navigate:
Click **Ad Wall** in the top bar.

### Component Breakdown:

1. **Left Sidebar: `Competitor Rail`**:
   - Checkboxes allow users to toggle specific competitors on or off the wall.
   - Each entry features a **`Dossier`** shortcut that jumps straight into the By-Company view.
   - Bottom input: Enter competitor name/URL + click **`Add`** to track a new competitor immediately.
2. **Market Intelligence Summary Banner**:
   > *"Most ads focus on scarcity. 33% of active ads use it. AI has the fewest ads in Coimbatore, leaving room for BrandMonk."*
3. **Filter & Sort Bar**:
   - Course Pills: **`All courses`**, **`AI`**, **`Digital marketing`**, **`UI/UX`**.
   - Sort Dropdown: **`Longest running`** (identifies ads with sustained budget), **`Highest score`**, **`Newest`**.
   - Real-time counter: *6 ads from 6 competitors*.
4. **Authentic Meta Creative Tiles**:
   - **Real Media Display**: Shows the actual image used in the live Meta ad campaign (or video thumbnail with play badge).
   - **Course Tag & Creative Score**: Top overlay (e.g. `AI`, `Score: 86`).
   - **Longevity Progress Bar**: Visual bar showing runtime (e.g., *Running 87 days*).
   - **Speaking point**: *"An ad running for over 60 days is a proven winner. Institutes don't burn ad spend on campaigns that don't generate enrollments. Longevity is our strongest signal of a winning creative."*

---

## 6. Detail Pane & Decoding "Why Ads Are Attractive"

### How to navigate:
Click on any ad card on the Ad Wall (e.g., **Nexora Academy: "Learn AI. Get hired in 90 days."**). The right-hand detail pane slides open.

### Tab 1: `Analysis` (Core Requirement)
1. **Ad Creative & Meta Source Link**:
   - Full 4:5 visual preview.
   - Click **`View high-res ad image`** or **`Open video creative`** to inspect the source file directly.
2. **Why This Advertisement Is Attractive (Highlighted Box)**:
   > *"It promises a concrete result in a fixed time, and the free demo lowers the risk of saying yes."*
   - **Speaking point**: *"Here is where Gemini AI breaks down the prospect psychology. Students are anxious about wasting months without getting hired. The 90-day deadline gives certainty, while the free demo eliminates financial fear."*
3. **Structured Strategy Breakdown**:
   - **Core Hook**: *Outcome promise with a deadline*
   - **Offer**: *Free demo class and placement assistance*
   - **Target Audience**: *Graduates and career switchers, ages 20 to 28*
   - **Ad Tactics Chips**: `Fixed timeline`, `Placement promise`, `Free trial`
   - **Competitor Weakness (Exploitation Angle)**: *No verified student names, salary proof, or batch size limits.*
4. **Primary CTA**: Click **`Create BrandMonk poster`** to jump to the poster studio.

### Tab 2: `Marketing Report` (Admissions & Counselor Battlecard)
1. **Target Audience Profile & Intent**:
   - Explains the student's psychological mindset and funnel stage.
2. **Decoded Ad Subtext ("What They Really Mean")**:
   - Compares the surface marketing pitch against the hidden reality.
3. **Counselor Talking Point**:
   - Pre-written scripts for BrandMonk admissions counselors when prospective students mention competitor offers.

---

## 7. By-Company Category View (`By Company` Tab) ⭐

### How to navigate:
Click the **By Company** tab in the top navigation bar.

### Action Steps:

1. **Left Panel — Institution Category Selector**:
   - Use the **`Filter institutions...`** search bar to search for any institute by name.
   - Click on **Nexora Academy** (AI), then **Growth Lab** (Digital Marketing), then **Lumen Design School** (UI/UX).
   - The selection border highlights in teal.
2. **Right Panel — Institution Dossier**:
   - **Header**: Shows institution name, course, city, official Meta Ad Library Page ID, and website link.
   - **Active Ads Gallery**: Displays every active creative run by that specific company.
   - For every ad, shows:
     - Real ad image / video link.
     - Active longevity (e.g., *87 days active*).
     - Platforms deployed (*Facebook, Instagram*).
     - **Why this advertisement is attractive (Prospect psychology)**.
     - Decoded Hook, Offer, and Audience.
     - Competitor vulnerabilities.
   - **Direct Actions**:
     - Click **`Launch counter-ad`**: Opens the Strategic Inversion modal targeting this exact creative.
     - Click **`Generate BrandMonk poster`**: Opens the poster generator.

---

## 8. Strategic Inversion & Creative Recommender Modal

### How to navigate:
Click the **`Launch counter-ad`** button on any ad in the By-Company view or Detail Pane.

### Walkthrough & Explanations:

1. **Left Side: Competitor Audit**:
   - Shows the competitor's ad visual, headline, copy snippet, active days, identified vulnerabilities, and prospect doubts left unanswered.
2. **Right Side: 3 Counter-Creative Angles (Tabs)**:
   - **Tab 1: `The Contrarian Pattern Interrupt`**:
     - *Strategy*: Questions the competitor's generic promise, positioning BrandMonk as the mature, high-rigor alternative.
     - *Approved Claim*: Backed by verified BrandMonk claim.
   - **Tab 2: `Verified Proof & Live ROI Contrast`**:
     - *Strategy*: Contrasts competitor's vague claims with verified alumni GitHub portfolios and live campaign metrics.
   - **Tab 3: `Friction-Free Transparency & Zero Hidden Fees`**:
     - *Strategy*: Exposes hidden certification and exam fees, promoting BrandMonk's 100% upfront fee schedule.
3. **Complete Ad Copy Deck**:
   - **Punchy Headline (<8 words)** + **`Copy`** button.
   - **Supporting Subline** + **`Copy`** button.
   - **Primary Text Copy** + **`Copy`** button.
   - **Call to Action (CTA)**.
4. **Visual Direction & Image Generation Prompt**:
   - Composition guide, brand palette hex codes (`#16202E`, `#1F4FD8`, `#F2B84B`), and typography specs.
   - **Copy Prompt**: Ready-to-use Midjourney/Flux prompt with negative prompt included.

---

## 9. Market Opportunities & Objection Clusters (`Opportunities` Tab)

### How to navigate:
Click the **Opportunities** tab in the top navigation bar.

### What it shows:
Aggregates weaknesses across **all competitor ads in the entire city** into ranked market opportunities:

1. **Cluster 1: Unclear course fees and unexpected add-on costs**:
   - Threat/Opportunity score: `27.0`.
   - Counter-Angle: *Answer-first fee transparency*.
   - Pre-drafted headlines: *"Clear fees. Live mentors. Zero guesswork."*
2. **Cluster 2: Doubts around real placement statistics and hiring partners**:
   - Counter-Angle: *Showcase real alumni portfolio links and verifiable project outcomes*.
3. **Cluster 3: Inflexible batch timings and unannounced schedule delays**:
   - Counter-Angle: *Announce guaranteed weekend and evening slots*.

---

## 10. Conclusion & Business Value Summary

### What to say to close the presentation:
> *"To summarize the business value of Ad Desk for BrandMonk Academy:*
>
> 1. ***Zero Manual Effort***: *Competitor ads from Meta Ad Library are scraped, deduplicated, and media-cached automatically.*
> 2. ***Deep Psychological Understanding***: *We don't just see the ad; Google Gemini explains exactly why the ad attracts students.*
> 3. ***Categorized Intelligence***: *The new **By Company** category view gives our management an instant dossier of each competitor's full campaign footprint.*
> 4. ***100% Brand-Safe Counter Ads***: *Our Strategic Inversion engine generates ready-to-run counter-posters and copy decks constrained strictly by our verified claims.*
> 5. ***Commercial Readiness***: *The entire system is live, tested, and actively running on our local environment with full fallback resilience.*
>
> *Thank you. I am ready to answer any questions or demonstrate any specific screen."*
