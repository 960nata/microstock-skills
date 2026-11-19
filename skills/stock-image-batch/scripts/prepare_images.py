#!/usr/bin/env python3
"""Convert <batch>/raw/* into Adobe Stock-ready JPEGs in <batch>/final/.

- upscale until width*height >= --min-mp megapixels (default 4, Adobe's minimum)
- RGB JPEG quality 95, no EXIF/metadata
Usage: prepare_images.py BATCH_DIR [--min-mp 4] [--upscaler lanczos|realesrgan] [--force]
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

EXTS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_MP = 100  # Adobe Stock upper limit


def realesrgan(src: Path) -> Image.Image:
    exe = shutil.which("realesrgan-ncnn-vulkan")
    if not exe:
        sys.exit("realesrgan-ncnn-vulkan not found in PATH; use --upscaler lanczos")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "up.png"
        subprocess.run([exe, "-i", str(src), "-o", str(out), "-s", "4"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return Image.open(out).copy()


def process(src: Path, dst: Path, min_mp: float, upscaler: str) -> str:
    img = Image.open(src)
    img = img.convert("RGB")
    w, h = img.size
    target = min_mp * 1_000_000
    if w * h < target:
        if upscaler == "realesrgan":
            img = realesrgan(src).convert("RGB")
            w, h = img.size
        scale = math.sqrt(target / (w * h)) if w * h < target else 1.0
        if scale > 1:
            nw, nh = math.ceil(w * scale), math.ceil(h * scale)
            img = img.resize((nw, nh), Image.LANCZOS)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=3))
    w, h = img.size
    if w * h > MAX_MP * 1_000_000:
        s = math.sqrt(MAX_MP * 1_000_000 / (w * h))
        img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "JPEG", quality=95, optimize=True, subsampling=0)
    return f"{w}x{h} ({w * h / 1e6:.1f} MP)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--min-mp", type=float, default=4.0)
    ap.add_argument("--upscaler", choices=["lanczos", "realesrgan"], default="lanczos")
    ap.add_argument("--force", action="store_true", help="overwrite existing final/*.jpg")
    args = ap.parse_args()

    raw, final = args.batch / "raw", args.batch / "final"
    files = sorted(p for p in raw.glob("*") if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No images in {raw}")
    made = 0
    for src in files:
        dst = final / f"{src.stem}.jpg"
        if dst.exists() and not args.force:
            continue
        print(f"{src.name} → {dst.name}  {process(src, dst, args.min_mp, args.upscaler)}")
        made += 1
    print(f"\n{made} prepared, {len(files) - made} already existed. Output: {final}")


if __name__ == "__main__":
    main()
