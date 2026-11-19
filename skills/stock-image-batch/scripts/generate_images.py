#!/usr/bin/env python3
"""Generate images for every row in <batch>/plan.csv with the OpenAI Images API.

Resumable: rows whose raw/<id>.png already exists are skipped.
Usage: generate_images.py BATCH_DIR [--dry-run] [--limit N] [--yes] [--only IDS]
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API_URL = "https://api.openai.com/v1/images/generations"
SIZES = {"square": "1024x1024", "landscape": "1536x1024", "portrait": "1024x1536"}
SUFFIX = ", no text, no logo, no watermark"


def load_env(batch: Path) -> None:
    env_file = batch / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def read_plan(batch: Path) -> list[dict]:
    plan = batch / "plan.csv"
    if not plan.exists():
        sys.exit(f"Missing {plan}. Run stock-trend-research first.")
    with plan.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("prompt") or "").strip()]
    for r in rows:
        r["id"] = r["id"].strip().zfill(4)
        r["aspect"] = (r.get("aspect") or "landscape").strip().lower()
        if r["aspect"] not in SIZES:
            sys.exit(f"Row {r['id']}: aspect must be one of {list(SIZES)}")
    return rows


def generate(row: dict, out: Path, model: str, quality: str, key: str) -> str:
    prompt = row["prompt"].strip()
    if "no watermark" not in prompt.lower():
        prompt += SUFFIX
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": SIZES[row["aspect"]],
        "quality": quality,
        "n": 1,
    }).encode()
    delay = 5
    for attempt in range(1, 6):
        req = urllib.request.Request(API_URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                data = json.load(resp)
            item = data["data"][0]
            if item.get("b64_json"):
                raw = base64.b64decode(item["b64_json"])
            else:  # some models return a URL instead
                with urllib.request.urlopen(item["url"], timeout=120) as img:
                    raw = img.read()
            tmp = out.with_suffix(".part")
            tmp.write_bytes(raw)
            tmp.replace(out)
            return "ok"
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            # 400 = prompt rejected by safety system or bad params: retrying will not help
            return f"HTTP {e.code}: {detail}"
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            return f"network: {e}"
    return "gave up"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="", help="comma-separated ids to (re)generate")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--quality", default="high", choices=["high", "medium", "low"])
    ap.add_argument("--price-per-image", type=float, default=0.0)
    args = ap.parse_args()

    batch = args.batch.resolve()
    load_env(batch)
    raw = batch / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    rows = read_plan(batch)
    if args.only:
        wanted = {i.strip().zfill(4) for i in args.only.split(",") if i.strip()}
        rows = [r for r in rows if r["id"] in wanted]
        for r in rows:  # forced redo
            (raw / f"{r['id']}.png").unlink(missing_ok=True)
    todo = [r for r in rows if not (raw / f"{r['id']}.png").exists()]
    if args.limit:
        todo = todo[: args.limit]

    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
    print(f"Batch: {batch.name} | plan rows: {len(rows)} | to generate: {len(todo)} | model: {model}")
    if args.price_per_image:
        print(f"Estimated cost: ~${len(todo) * args.price_per_image:.2f}")
    if not todo:
        print("Nothing to do.")
        return
    if args.dry_run:
        print(f"Sample [{todo[0]['id']}] {todo[0]['aspect']}: {todo[0]['prompt'][:200]}")
        return

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set (env or batch/.env).")
    if not args.yes and input(f"Generate {len(todo)} images? [y/N] ").strip().lower() != "y":
        sys.exit("Cancelled.")

    failed: list[tuple[str, str]] = []
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futures = {pool.submit(generate, r, raw / f"{r['id']}.png", model, args.quality, key): r for r in todo}
        for fut in as_completed(futures):
            r = futures[fut]
            result = fut.result()
            done += 1
            if result == "ok":
                print(f"[{done}/{len(todo)}] {r['id']} ✓")
            else:
                failed.append((r["id"], result))
                print(f"[{done}/{len(todo)}] {r['id']} ✗ {result}")

    print(f"\nDone: {len(todo) - len(failed)} ok, {len(failed)} failed.")
    if failed:
        print("Re-run the same command to retry, or edit these prompts in plan.csv:")
        for i, why in failed:
            print(f"  {i}: {why}")
        sys.exit(1)


if __name__ == "__main__":
    main()
