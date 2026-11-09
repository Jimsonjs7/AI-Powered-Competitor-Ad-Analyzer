# General Agent Rules

## 1. Working style
- Be fast and decisive. Make the change, then report briefly what changed.
- Prefer small, reviewable edits over rewrites. Keep functions short and named for what they do.
- Match existing patterns before introducing a new one.

## 2. Autonomy tiers
**Do without asking:** read any file, search the repo, run linters, formatters and tests, create or edit files inside `backend/`, `frontend/`, `docs/`, add dependencies already listed in the plan, fix bugs you introduced.

**Do, then tell the user:** refactors inside one module, new endpoints that follow the existing pattern, new UI components that follow DESIGN_RULES, adding tests.

**Ask first (high impact only):** deleting files or data, changing the database schema in a way that drops data, changing the provider chain order, adding a paid service, touching authentication, rotating or committing secrets, force-pushing, running anything against a production URL.

## 3. Definition of done
- Code runs, lints clean and tests pass.
- No secrets, tokens or personal data in code, logs or commits.
- UI changes checked at mobile and desktop widths.
- `PROJECT_HISTORY.md` updated (see section 4).

## 4. Documentation and history
- `PROJECT_DOCUMENTATION.md`: the stable description of architecture, endpoints, data model and setup. Update when behaviour changes.
- `PROJECT_HISTORY.md`: running log of what was done each session (date, task, files, decisions). It is gitignored. Never put it in commits.
- Commit messages: imperative, one line, scope first (`ads: dedupe by ad_archive_id`).

## 5. Honesty
- State what was tested and what was not. Do not claim a scraper works without a real run.
- If a requirement conflicts with a rule, say so and propose the closest compliant option.
