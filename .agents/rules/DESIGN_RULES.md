# Design Rules (frontend)

Follow `ad-analyzer-ui.html` as the visual reference.

## Visual
- Light theme only. Canvas `#F4F6FA`, surface `#FFFFFF`, ink `#17202F`, muted `#5B6678`, line `#DCE2EC`, accent `#2447C9`, good `#17795A`, warn `#9A5A08`. Define as CSS variables. Do not add new colours without a reason.
- **No gradients. No emoji.** Not in UI text, buttons, empty states or toasts. Use simple SVG line icons (1.7px stroke) or text.
- No decorative glow, glassmorphism or heavy shadows. Use borders for structure. Shadows only for floating layers (drawer, menus).
- Radius: 8px panels, 6px controls and images, 4px chips. Do not use one radius for everything.
- Font: Instrument Sans with a system fallback. Tabular numbers for data.

## Layout
- Left sidebar navigation, content max width 1240px, 8px spacing scale.
- Ad creatives are the hero. Show real ad images and video at their true aspect ratio, never cropped to hide text.
- Use a table for competitors, a grid for ads, a right-side drawer for ad detail, tabs for prompt variations.
- Do not turn every block into an identical card. Vary structure to match the content.

## Writing
- Sentence case. Plain words. Buttons say what happens: "Refresh ads", "Create BrandMonk poster from this ad".
- No all-caps labels, no spaced-dash labels, no arrows appended to buttons.
- Errors say what went wrong and what to do next. No apologies, no vague text.
- Empty states say what to do next, for example "No active ads found. Try another Page ID or import an ad link."

## States every screen must have
Loading (skeleton or inline status), empty, error with retry, partial (some providers failed), and success.

## Accessibility and responsiveness
- WCAG AA contrast. Visible focus outline on every control. Full keyboard use. Drawer traps focus and closes on Escape.
- Respect `prefers-reduced-motion`. Motion only in response to a user action.
- Works from 360px wide. Tables scroll inside their own container. Touch targets at least 40px.
- Real labels on inputs. `aria-pressed`, `aria-selected`, `aria-current` on toggles, tabs and nav. `role="status"` for async messages.

## Code
- Components small and typed (TypeScript). Server data through one API client with typed responses. Data fetching with caching and retry (TanStack Query).
- Never render scraped text as HTML. Output is escaped by default.
