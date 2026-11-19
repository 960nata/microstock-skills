---
name: stock-pipeline
description: End-to-end workflow for selling AI-generated images on Adobe Stock — trend research, batch generation of ~100 images, upscaling to stock specs, SEO title/keyword metadata CSV, Google Drive backup, and SFTP upload. Use when the user wants to make a microstock batch, sell AI images on Adobe Stock (or Shutterstock/Freepik), or asks which step/agent comes next. Explains the hand-off between Claude (research, metadata) and Codex (image generation).
---

# Microstock pipeline (Adobe Stock)

One batch = one folder. Every step reads the previous step's file, so any agent can
pick up where another stopped.

```
batches/2026-11-20-ramadan/
├── plan.csv            ← 1. stock-trend-research   (Claude: web research)
├── raw/0001.png …      ← 2. stock-image-batch       (Codex: image generation)
├── final/0001.jpg …    ← 2. stock-image-batch       (≥ 4 MP JPEG, sRGB)
├── metadata.jsonl      ← 3. stock-metadata-csv      (Claude or Codex: looks at each image)
├── adobe_stock.csv     ← 3. stock-metadata-csv      (validated CSV for the portal)
└── upload.log          ← 4. stock-upload            (Drive backup + Adobe SFTP)
```

## Who does what

| Step | Best agent | Why |
| ---- | ---------- | --- |
| 1 Research | Claude (or any agent with web search) | Needs fresh search/trend data and judgment |
| 2 Generate | **Codex** | Has OpenAI image generation; Claude cannot make images |
| 3 Metadata | Claude or Codex | Both can view images; metadata must describe the *actual* image |
| 4 Upload | Any | Shell + rclone |

Hand-off rule: when you finish a step, tell the user the exact next command or prompt,
e.g. *"Open Codex in this folder and say: generate the batch in batches/2026-11-20-ramadan"*.

## Start a batch

```bash
mkdir -p batches/$(date +%F)-<slug>/{raw,final}
```
Then run the skills in order: `stock-trend-research` → `stock-image-batch` →
`stock-metadata-csv` → `stock-upload`.

## Rules that get images accepted (all steps must respect them)
- **No IP**: no brands, logos, trademarks, characters, celebrities, real people, artist
  names or "in the style of <artist>" in prompts, titles, or keywords.
- **No near-duplicates**: 100 images = many concepts × a few clearly different
  variations. Adobe rejects "similar content" and may limit spammy contributors.
- **Quality over count**: drop images with broken hands, garbled text, warped faces,
  extra limbs, or melted objects before uploading.
- **Mark AI**: in the contributor portal tick *"Created using generative AI tools"*;
  if people/property appear, also tick *"People and Property are fictional"*.
- **Specs**: JPEG, ≥ 4 MP (e.g. 2560×1600), sRGB, no watermark/text unless intended.
- Rules change — before a big batch, re-read Adobe Stock's current *Generative AI
  content* guidelines in the Contributor help center.
