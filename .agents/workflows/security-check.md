# Security check (run before finishing backend work)

1. Search the diff for secrets, tokens, keys and real URLs with credentials. Remove any found.
2. Confirm every new route requires auth and checks object ownership.
3. Confirm every input is validated by a Pydantic model with limits.
4. Confirm user-supplied URLs go through the host allow-list and private-IP block.
5. Confirm uploads check size, type and magic bytes.
6. Confirm scraped and AI text is treated as untrusted data and AI output is schema-validated.
7. Confirm CORS, rate limits and timeouts are set on new endpoints and outbound calls.
8. Run `pip-audit`, `npm audit`, linter and tests. Fix or report findings.
9. Write a short result (pass or findings) in `PROJECT_HISTORY.md`.
