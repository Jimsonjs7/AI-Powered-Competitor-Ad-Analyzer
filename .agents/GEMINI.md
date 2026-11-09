# Project Instructions: BrandMonk Ad Analyzer

AI web app that finds local training-institute competitors, collects their Facebook and Instagram ads from Meta Ad Library, analyses the ads with AI, and generates original poster prompts and posters for BrandMonk Academy.

## Always load
- `rules/GENERAL_AGENT_RULES.md` for every task.
- `rules/ARCHITECTURE_RULES.md` before adding or moving any module.
- `rules/SECURITY_RULES.md` for backend work, then run `workflows/security-check.md` before finishing.
- `rules/DESIGN_RULES.md` for frontend work (use it instead of the security file on pure UI tasks).

## Skills (read the matching SKILL.md before starting)
- `skills/ad-source-provider-chain` for scraping and ad collection.
- `skills/ad-analysis-pipeline` for AI analysis of ads.
- `skills/poster-generation` for prompts and poster rendering.
- `skills/dashboard-ui` for any screen or component.
- `skills/secure-fastapi-backend` for any API, job or database code.

## Source of truth
Reference design: `ad-analyzer-ui.html`. Requirement plan: `AI_Competitor_Ad_Analyzer_Plan.md`. Do not invent features beyond these without asking.
