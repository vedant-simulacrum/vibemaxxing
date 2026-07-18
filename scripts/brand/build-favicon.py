#!/usr/bin/env python3
"""Build the legacy multi-resolution favicon.ico from generated PNGs."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
FAVICONS = ROOT / "assets" / "brand" / "exports" / "favicon"

images = [Image.open(FAVICONS / f"favicon-{size}.png").convert("RGBA") for size in (16, 32, 48)]
images[-1].save(
    FAVICONS / "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)],
    append_images=images[:-1],
)
print(f"Built {FAVICONS / 'favicon.ico'}")
