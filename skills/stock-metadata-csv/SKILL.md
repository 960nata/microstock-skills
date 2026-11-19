---
name: stock-metadata-csv
description: Write SEO titles, ranked keywords, and categories for every image in a stock batch by actually looking at each image, then build and validate the Adobe Stock contributor CSV (Filename, Title, Keywords, Category, Releases). Use when the user needs Adobe Stock metadata, keywords/tags for stock photos, a CSV for bulk upload, or wants images to be found more easily in stock search.
---

# Stock metadata → Adobe Stock CSV

Metadata decides whether buyers ever find the image. Write it from **what is in the
final image**, not from the prompt (the model often drifts).

## 1. Look at each image
Open `final/*.jpg` in groups of ~10. For each, write one JSON line to `metadata.jsonl`:

```json
{"filename": "0001.jpg", "title": "Top view of iftar table with dates, lanterns and tea during Ramadan evening", "keywords": ["ramadan", "iftar", "dates", "lantern", "..."], "category": "Food"}
```

### Title (Adobe: max 200 chars; aim 60–120)
- A natural sentence a buyer would type: **subject + action + setting + mood/concept**.
- Most important words first. No keyword lists, no "AI generated", no brand/artist names,
  no camera jargon nobody searches ("8k", "octane render", "hyperrealistic").

### Keywords (Adobe: max 49; aim 30–49)
- **Order matters — the first ~10 weigh most.** Put the main subject and concept first.
- Mix: literal objects → setting/location type → concept/emotion → season/event →
  color/style/composition (`copy space`, `top view`, `flat lay`, `background`).
- Single words or short phrases; English; lowercase; no duplicates or plurals of the same word.
- Never: trademarks, celebrities, artist names, misleading tags, other contributors' names.

### Category (number or name)
1 Animals · 2 Buildings and Architecture · 3 Business · 4 Drinks · 5 The Environment ·
6 States of Mind · 7 Food · 8 Graphic Resources · 9 Hobbies and Leisure · 10 Industry ·
11 Landscapes · 12 Lifestyle · 13 People · 14 Plants and Flowers · 15 Culture and Religion ·
16 Science · 17 Social Issues · 18 Sports · 19 Technology · 20 Transport · 21 Travel

### Releases
Leave empty for AI images (people are fictional — tick the matching box in the portal).

## 2. Build + validate the CSV

```bash
S=<path-to-this-skill>/scripts
python3 $S/build_csv.py batches/<batch>              # writes adobe_stock.csv
python3 $S/build_csv.py batches/<batch> --stub       # creates metadata.jsonl rows for images without metadata
```
The script checks: file exists in `final/`, title length, 1–49 keywords (dedupes, lowercases,
trims), category valid, risky trademark words. Fix every ✗ before upload; ⚠ are advice.

## 3. Hand off
> Next: `stock-upload` — upload `final/*.jpg` by SFTP, then upload `adobe_stock.csv`
> in the contributor portal.
