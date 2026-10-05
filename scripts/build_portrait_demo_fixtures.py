#!/usr/bin/env python3
"""Paint two reproducible demo originals: color hero + monster source."""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "artifacts" / "card-art" / "fixtures" / "originals"


def paint_karnok(path: Path) -> None:
    image = Image.new("RGB", (420, 520), (214, 198, 168))
    draw = ImageDraw.Draw(image)
    draw.ellipse((168, 46, 256, 140), fill=(214, 168, 126))
    draw.polygon([(178, 136), (246, 136), (272, 350), (150, 350)], fill=(42, 64, 118))
    draw.rectangle((154, 338, 268, 478), fill=(36, 32, 40))
    draw.polygon([(248, 150), (328, 64), (344, 84), (266, 178)], fill=(210, 210, 216))
    draw.rectangle((236, 168, 270, 192), fill=(210, 210, 216))
    draw.ellipse((188, 78, 210, 100), fill=(36, 32, 30))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def paint_goblin(path: Path) -> None:
    image = Image.new("RGB", (420, 520), (214, 198, 168))
    draw = ImageDraw.Draw(image)
    draw.ellipse((148, 84, 272, 198), fill=(104, 156, 58))
    draw.polygon([(168, 108), (118, 28), (196, 98)], fill=(86, 138, 52))
    draw.polygon([(252, 108), (302, 28), (224, 98)], fill=(86, 138, 52))
    draw.ellipse((176, 126, 198, 148), fill=(28, 24, 18))
    draw.polygon([(188, 186), (232, 186), (210, 214)], fill=(48, 36, 28))
    draw.polygon([(174, 196), (246, 196), (264, 400), (156, 400)], fill=(118, 72, 36))
    draw.polygon([(246, 228), (324, 200), (314, 226), (252, 246)], fill=(86, 138, 52))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        karnok = DEST / "heroes" / "karnok-stoneward-demo.png"
        goblin = DEST / "monsters" / "goblin-demo.png"
        paint_karnok(karnok)
        paint_goblin(goblin)
        logger.info("Wrote demo originals to %s", DEST)
    except Exception:
        logger.exception("Failed to paint demo portrait originals.")
        raise


if __name__ == "__main__":
    main()
