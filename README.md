# Ad Desk - BrandMonk Ad Analyzer

Ad Desk is an AI competitor ad intelligence web application that collects competitor Facebook and Instagram ads from Meta Ad Library, analyses them with multimodal AI, and generates original poster concepts for BrandMonk Academy.

## Architecture Highlights
- Hybrid scraping provider chain with automatic fallback (Apify, ScrapeCreators, Playwright, Manual Import)
- Strict router -> service -> provider separation
- Normalized `AdRecord` contract across all data providers
- Local media caching to prevent hotlinking expired platform CDNs
- Dedicated BrandMonk poster template overlay engine (Pillow) with text safe zones
- Fast, accessible three-pane interface adhering to strict light theme design rules

## Getting Started
See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for full setup instructions, architecture details, and development workflow.
