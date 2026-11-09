---
name: poster-generation
description: Create original BrandMonk poster prompts and rendered posters from a competitor ad strategy. Use for the prompt builder, brand kit, image rendering and text overlay.
---
# Poster generation

## Inputs
BrandMonk course, source ad analysis (hook, offer, tactics), variant (outcome-led, proof-led, urgency-led), size (square 1080x1080, feed 1080x1350, story 1080x1920), Brand Kit (logo, colours, fonts, tone, course USPs, contact).

## Steps
1. Build three prompt variations. Each prompt names the strategy, composition, palette (from Brand Kit), mood and audience, and ends with: leave clean space for text and logo, draw no lettering.
2. Generate a copy set per variant: headline (under 8 words), subline, button text, and optional fine print.
3. Render the background with `ImageClient` (Imagen, GPT-image or Ideogram, behind one interface).
4. Overlay headline, subline, button and logo from the template engine (Pillow or Satori) using Brand Kit fonts and colours. Check text fits the safe area.
5. Store prompt, copy set and final image. Offer PNG and JPG download per size.

## Rules
- Create original work from the strategy. Never copy a competitor's image, wording, logo or layout. Show a short note in the UI that posters are strategy-inspired.
- Do not invent facts (fees, dates, placement numbers). Use only values from the Brand Kit or typed by the user.
- Keep a human review step before download.
- AI text rendering is unreliable, so text always comes from the overlay.
