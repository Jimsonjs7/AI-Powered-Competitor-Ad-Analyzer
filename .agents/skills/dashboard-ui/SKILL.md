---
name: dashboard-ui
description: Build or change screens and components for the Ad Analyzer dashboard in the light theme defined by DESIGN_RULES. Use for any frontend task.
---
# Dashboard UI

## Screens
Overview (key figures, top hooks, course share, longest-running ads), Competitors (table, confirm or remove, add, rediscover), Ad gallery (filters, grid, detail drawer), Poster studio (course and source ad, prompt tabs, copy set, preview, sizes), later: Insights and Settings.

## Stack
React + Vite + TypeScript, Tailwind with the project tokens as CSS variables, TanStack Query for data, Recharts for charts, React Router.

## Build steps
1. Read `rules/DESIGN_RULES.md` and open `ad-analyzer-ui.html` for the visual target.
2. Reuse existing components first: `Panel`, `Chip`, `DataTable`, `AdTile`, `Poster`, `Drawer`, `Tabs`, `Field`.
3. Fetch through the typed API client. Show loading, empty, error and partial states.
4. Long jobs (fetch ads, analyse, render): show inline status with `role="status"`, poll the job endpoint, allow retry.
5. Check keyboard use, focus order and 360px width before finishing.

## Specific patterns
- Ad media: store aspect ratio, render with `object-fit: contain` on a neutral background.
- Competitor status chips: Confirmed (green), Needs review (amber).
- Provider failure: banner "Some ad sources did not respond. Showing saved ads from yesterday." with a Retry button.
- Charts: one accent colour, labelled values, no 3D, no gradients.
- Copy button gives text feedback ("Prompt copied."), not a popup.
