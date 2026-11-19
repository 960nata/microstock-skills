---
name: stock-image-batch
description: Generate a batch of ~100 stock images from a plan.csv with the OpenAI Images API (resumable, parallel, retrying), then convert them to Adobe Stock-ready JPEGs of at least 4 MP. Use in Codex (or any agent with an OpenAI key) when the user wants to generate many images at once for microstock, run a batch from plan.csv, or upscale/prepare images for Adobe Stock.
---

# Batch image generation (Codex)

Two scripts in `scripts/`, Python 3.9+ standard library + Pillow.

## 0. Requirements
- `OPENAI_API_KEY` in the environment (or in `batches/<batch>/.env` as `OPENAI_API_KEY=...`).
- `pip install pillow` (only for step 2).
- Optional `OPENAI_IMAGE_MODEL` (default `gpt-image-1`).

If your Codex session has built-in image generation and the user prefers it, you may
generate images that way instead — but **save them as `raw/<id>.png`** so step 2 and the
metadata skill still work. For 100 images the script is faster and resumable.

## 1. Generate

```bash
S=<path-to-this-skill>/scripts
python3 $S/generate_images.py batches/<batch> --dry-run      # shows count + sample prompt
python3 $S/generate_images.py batches/<batch> --limit 3      # test 3 first, look at them
python3 $S/generate_images.py batches/<batch> --yes          # the rest (skips existing)
```
Options: `--concurrency 4`, `--quality high|medium|low`, `--only 0007,0012` (redo some),
`--price-per-image 0.05` (prints an estimated total).

**Costs real money.** Always run `--limit 3` first, show the user the images and the
estimated cost, and get a "go" before the full run. Check current prices on OpenAI's
pricing page.

Failed rows are listed at the end; just re-run — finished files are skipped.

## 2. Review (do not skip)
Look at every image in `raw/`. Delete (or regenerate with `--only`) anything with
deformed hands/faces, garbled text, logos, watermarks, or that duplicates another.

## 3. Prepare for Adobe Stock

```bash
python3 $S/prepare_images.py batches/<batch>               # raw/*.png → final/*.jpg
python3 $S/prepare_images.py batches/<batch> --min-mp 6    # bigger output
```
- Upscales (Lanczos + light sharpening) until ≥ 4 MP, converts to RGB JPEG q95, strips metadata.
- If `realesrgan-ncnn-vulkan` is installed, pass `--upscaler realesrgan` for better detail.

## 4. Hand off
> Next: run `stock-metadata-csv` on `batches/<batch>` (Claude or Codex).
