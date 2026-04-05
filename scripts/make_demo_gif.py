"""Build a short loop GIF from docs/images/dashboard-overview.png (Ken Burns–style zoom).

Requires: pip install pillow

Usage (from repo root):
  python scripts/make_demo_gif.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow: python -m pip install pillow", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "images" / "dashboard-overview.png"
OUT = ROOT / "docs" / "images" / "demo.gif"

MAX_WIDTH = 560
FRAMES = 12
ZOOM = 1.04  # max zoom-in vs full frame
FRAME_MS = 110


def _crop_zoom(img: Image.Image, zoom: float) -> Image.Image:
    """Return image scaled as if camera zoomed toward center (zoom > 1 crops then scales)."""
    w, h = img.size
    zw, zh = int(w / zoom), int(h / zoom)
    x0 = (w - zw) // 2
    y0 = (h - zh) // 2
    cropped = img.crop((x0, y0, x0 + zw, y0 + zh))
    return cropped.resize((w, h), Image.Resampling.LANCZOS)


def main() -> None:
    if not SRC.is_file():
        print(f"Missing source image: {SRC}", file=sys.stderr)
        raise SystemExit(1)

    img = Image.open(SRC).convert("RGB")
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize(
            (MAX_WIDTH, int(img.height * ratio)),
            Image.Resampling.LANCZOS,
        )

    frames_rgb: list[Image.Image] = []
    for i in range(FRAMES):
        t = (i / (FRAMES - 1)) * math.pi
        z = 1.0 + (ZOOM - 1.0) * (1.0 - abs(math.cos(t)))  # smooth in-out
        frames_rgb.append(_crop_zoom(img, z))

    # Single adaptive palette keeps GIF size reasonable for README
    palette = frames_rgb[0].quantize(colors=80, method=Image.Quantize.MEDIANCUT)
    frames_p = [f.quantize(palette=palette) for f in frames_rgb]

    frames_p[0].save(
        OUT,
        save_all=True,
        append_images=frames_p[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
