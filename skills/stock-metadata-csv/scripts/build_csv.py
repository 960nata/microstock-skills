#!/usr/bin/env python3
"""Validate <batch>/metadata.jsonl and write <batch>/adobe_stock.csv.

Usage: build_csv.py BATCH_DIR [--stub] [--out NAME]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

CATEGORIES = [
    "Animals", "Buildings and Architecture", "Business", "Drinks", "The Environment",
    "States of Mind", "Food", "Graphic Resources", "Hobbies and Leisure", "Industry",
    "Landscapes", "Lifestyle", "People", "Plants and Flowers", "Culture and Religion",
    "Science", "Social Issues", "Sports", "Technology", "Transport", "Travel",
]
BY_NAME = {c.lower(): i + 1 for i, c in enumerate(CATEGORIES)}
BY_NAME.update({"environment": 5, "architecture": 2, "buildings": 2, "plants": 14})

# Words that usually mean a trademark/IP problem or useless spam. Extend as needed.
RISKY = {
    "apple", "iphone", "ipad", "macbook", "samsung", "google", "android", "microsoft",
    "windows", "facebook", "instagram", "tiktok", "whatsapp", "youtube", "netflix",
    "disney", "marvel", "pixar", "pokemon", "lego", "barbie", "nike", "adidas",
    "coca-cola", "coca cola", "pepsi", "starbucks", "mcdonalds", "tesla", "bmw",
    "mercedes", "ferrari", "rolex", "louis vuitton", "gucci", "chanel", "ikea",
    "ghibli", "midjourney", "dall-e", "dalle", "stable diffusion", "chatgpt", "openai",
    "ai generated", "generative ai", "8k", "4k", "octane render", "unreal engine",
    "trending on artstation", "artstation",
}
MAX_TITLE, MAX_KW = 200, 49


def norm_keywords(raw) -> list[str]:
    items = raw if isinstance(raw, list) else re.split(r"[,;]", str(raw))
    out: list[str] = []
    seen: set[str] = set()
    for k in items:
        k = re.sub(r"\s+", " ", str(k)).strip().lower()
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def category_id(raw) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
        return n if 1 <= n <= 21 else None
    except (TypeError, ValueError):
        return BY_NAME.get(str(raw).strip().lower())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--stub", action="store_true", help="append empty rows for images lacking metadata")
    ap.add_argument("--out", default="adobe_stock.csv")
    args = ap.parse_args()

    final = args.batch / "final"
    meta_path = args.batch / "metadata.jsonl"
    images = sorted(p.name for p in final.glob("*.jpg")) if final.exists() else []

    rows: list[dict] = []
    if meta_path.exists():
        for n, line in enumerate(meta_path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    sys.exit(f"metadata.jsonl line {n}: invalid JSON ({e})")

    if args.stub:
        have = {r.get("filename") for r in rows}
        missing = [i for i in images if i not in have]
        with meta_path.open("a", encoding="utf-8") as f:
            for name in missing:
                f.write(json.dumps({"filename": name, "title": "", "keywords": [], "category": ""}) + "\n")
        print(f"Added {len(missing)} stub rows to {meta_path}")
        return

    if not rows:
        sys.exit(f"No metadata in {meta_path}. Write it first (or run with --stub).")

    errors = warnings = 0
    out_rows = []
    seen_files: set[str] = set()
    for r in rows:
        name = str(r.get("filename", "")).strip()
        tag = name or "<no filename>"
        problems, advice = [], []
        if not name:
            problems.append("missing filename")
        elif name in seen_files:
            problems.append("duplicate filename")
        elif images and name not in images:
            problems.append("file not found in final/")
        seen_files.add(name)

        title = re.sub(r"\s+", " ", str(r.get("title", ""))).strip()
        if not title:
            problems.append("empty title")
        elif len(title) > MAX_TITLE:
            problems.append(f"title {len(title)} chars > {MAX_TITLE}")
        elif len(title.split()) < 4:
            advice.append("title is very short; describe subject + setting + concept")

        kws = norm_keywords(r.get("keywords", []))
        if not kws:
            problems.append("no keywords")
        if len(kws) > MAX_KW:
            advice.append(f"{len(kws)} keywords, trimmed to {MAX_KW}")
            kws = kws[:MAX_KW]
        elif len(kws) < 25:
            advice.append(f"only {len(kws)} keywords; aim for 30-49")

        text = " " + title.lower() + " " + " ".join(kws) + " "
        risky = sorted(w for w in RISKY if re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", text))
        if risky:
            problems.append("risky/trademark words: " + ", ".join(risky))

        cat = category_id(r.get("category"))
        if cat is None:
            problems.append(f"invalid category {r.get('category')!r}")

        for p in problems:
            print(f"✗ {tag}: {p}")
        for a in advice:
            print(f"⚠ {tag}: {a}")
        errors += len(problems)
        warnings += len(advice)
        out_rows.append([name, title, ", ".join(kws), cat or "", str(r.get("releases", "") or "")])

    without = [i for i in images if i not in seen_files]
    if without:
        print(f"⚠ {len(without)} images in final/ have no metadata (e.g. {without[0]}); they will not be in the CSV")
        warnings += 1

    if errors:
        sys.exit(f"\n{errors} error(s), {warnings} warning(s). CSV not written — fix metadata.jsonl and re-run.")

    out = args.batch / args.out
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["Filename", "Title", "Keywords", "Category", "Releases"])
        w.writerows(out_rows)
    print(f"\n✓ {out} written: {len(out_rows)} rows, {warnings} warning(s).")


if __name__ == "__main__":
    main()
