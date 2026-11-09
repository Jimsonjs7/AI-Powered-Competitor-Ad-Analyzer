# New feature workflow

1. Read GEMINI.md, the matching rules and the matching skill.
2. State the plan in three lines: what changes, which layers, which files.
3. Backend first: schema, service, route, tests. Then frontend: API client, component, states.
4. Check against DESIGN_RULES (no gradients, no emoji, all states, keyboard, 360px).
5. Run the security check for backend changes.
6. Update PROJECT_DOCUMENTATION.md if behaviour changed and add an entry to PROJECT_HISTORY.md.
