---
name: stock-trend-research
description: Research what images buyers are searching for on Adobe Stock right now — seasonal demand, trending themes, and high-demand/low-supply gaps — and turn it into a plan.csv of ~100 varied, sellable, IP-free image prompts. Use when the user asks what to make for microstock, what sells on Adobe Stock, wants trending stock photo ideas, or wants to start a new stock image batch.
---

# Stock trend research → plan.csv

Goal: pick concepts **people are searching for** that are **not yet flooded**, then
write 100 prompts that are different enough to be accepted as separate assets.

## 1. Collect demand signals (use web search)
Check several sources, note evidence for each idea:
- **Seasonal calendar** — upload 1–3 months before the event (review + indexing take time).
  Examples (verify exact dates): Lunar New Year (6 Feb 2027), Ramadan (starts ~8 Feb 2027),
  Eid al-Fitr (~10 Mar 2027), Easter (28 Mar 2027), Mother's Day, back to school, Halloween,
  Black Friday, Christmas, New Year.
- **Adobe's own trend content** — Adobe Stock "Creative Trends"/visual trends posts and the
  Contributor blog list themes buyers want this year.
- **Search pages** — search candidate keywords on stock.adobe.com; note the result count
  (supply) and whether the top results look dated/weak (opportunity).
- **Google Trends / news** — rising topics that marketers will need visuals for
  (AI at work, sustainability, wellness, remote work, fintech, local culture…).
- **Buyer intent** — think of who pays: marketers, bloggers, presentation makers,
  app designers. They need *backgrounds, copy space, concepts, people at work, flat-lays,
  textures, isolated objects*, not art pieces.

## 2. Score and pick concepts
For each candidate: `demand (1–5)`, `supply saturation (1–5, lower is better)`,
`commercial usefulness (1–5)`, `AI feasibility (1–5)` (avoid hands-heavy, text-heavy,
or exact-logo subjects). Keep the top **15–25 concepts**.

Show the user a short table of chosen concepts with the evidence before writing prompts.

## 3. Write plan.csv (100 rows)
Columns:

```csv
id,concept,prompt,aspect,category,seed_keywords
0001,ramadan table,"Top view of an iftar table with dates, ...",landscape,Food,"ramadan;iftar;dates;..."
```
- `id`: 4-digit, sequential. Becomes the filename.
- `aspect`: `landscape` | `portrait` | `square` (landscape sells best for web banners — use ~60 %).
- `category`: one Adobe category name (see `stock-metadata-csv`).
- 4–6 variations per concept, each changing **at least two** of: subject, composition/angle,
  color palette, setting, lighting, people/no people, copy-space position.

Prompt recipe (photorealistic stock):
`<subject + action>, <setting>, <composition: top view / close-up / wide>,
<copy space left/right/top>, <lighting>, <color palette>, commercial stock photo,
realistic, high detail, sharp focus, no text, no logo, no watermark`

Never put brands, celebrities, real landmarks with protected designs, artist names, or
"in the style of …" in prompts.

## 4. Hand off
Save `batches/<date>-<slug>/plan.csv`, then tell the user:
> Open Codex in this repo and say: *"Use stock-image-batch on batches/<date>-<slug>"*.
