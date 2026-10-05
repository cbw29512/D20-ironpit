#!/usr/bin/env python3
"""Process original portraits without overwriting sources.

Heroes keep full-color framed crops. Only monsters are converted to
shadow-box silhouettes.
"""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

CANVAS = (512, 640)
HERO_CANVAS = (480, 640)
PADDING_RATIO = 0.08
INK = (12, 10, 8, 255)
OUTLINE = (201, 163, 90, 255)
BACKGROUND_DISTANCE = 38
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}
VIGNETTE_INNER = (196, 122, 42)
VIGNETTE_OUTER = (10, 6, 3)
SAFE_SQUARE = 456


def _distance(pixel: tuple[int, int, int, int], color: tuple[int, int, int]) -> int:
    return max(abs(pixel[0] - color[0]), abs(pixel[1] - color[1]), abs(pixel[2] - color[2]))


def _border_colors(image: Image.Image) -> list[tuple[int, int, int]]:
    width, height = image.size
    colors: list[tuple[int, int, int]] = []
    for x in range(0, width, 8):
        colors.append(image.getpixel((x, 0))[:3])
        colors.append(image.getpixel((x, height - 1))[:3])
    for y in range(0, height, 8):
        colors.append(image.getpixel((0, y))[:3])
        colors.append(image.getpixel((width - 1, y))[:3])
    return colors


def _is_background(pixel: tuple[int, int, int, int], colors: list[tuple[int, int, int]]) -> bool:
    if pixel[3] < 24:
        return True
    return any(_distance(pixel, color) <= BACKGROUND_DISTANCE for color in colors)


def _largest_component(mask: Image.Image) -> Image.Image:
    width, height = mask.size
    pixels = mask.load()
    seen = [[False] * width for _ in range(height)]
    best: list[tuple[int, int]] = []
    for start_y in range(height):
        for start_x in range(width):
            if seen[start_y][start_x] or pixels[start_x, start_y] < 128:
                continue
            stack = [(start_x, start_y)]
            seen[start_y][start_x] = True
            blob: list[tuple[int, int]] = []
            while stack:
                x, y = stack.pop()
                blob.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and pixels[nx, ny] >= 128:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(blob) > len(best):
                best = blob
    cleaned = Image.new("L", mask.size, 0)
    if best:
        out = cleaned.load()
        for x, y in best:
            out[x, y] = 255
    return cleaned


def _foreground_mask(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[0] < 250:
        mask = alpha.point(lambda value: 255 if value >= 24 else 0)
        if mask.getbbox():
            return _largest_component(mask)
    colors = _border_colors(rgba)
    pixels = list(rgba.getdata())
    mask_values = [0 if _is_background(pixel, colors) else 255 for pixel in pixels]
    mask = Image.new("L", rgba.size)
    mask.putdata(mask_values)
    mask = mask.filter(ImageFilter.MaxFilter(5))
    if not mask.getbbox():
        gray = ImageOps.autocontrast(rgba.convert("L"))
        mask = gray.point(lambda value: 255 if value < 210 else 0)
    return _largest_component(mask)


def _fit_mask(mask: Image.Image) -> Image.Image:
    box = mask.getbbox()
    if box is None:
        raise ValueError("Portrait has no separable foreground to silhouette.")
    subject = mask.crop(box)
    pad = max(8, int(max(subject.size) * PADDING_RATIO))
    padded = Image.new("L", (subject.width + pad * 2, subject.height + pad * 2), 0)
    padded.paste(subject, (pad, pad))
    padded.thumbnail((int(CANVAS[0] * 0.9), int(CANVAS[1] * 0.9)), Image.Resampling.LANCZOS)
    canvas = Image.new("L", CANVAS, 0)
    left = (CANVAS[0] - padded.width) // 2
    top = CANVAS[1] - padded.height - int(CANVAS[1] * 0.06)
    canvas.paste(padded, (left, max(int(CANVAS[1] * 0.04), top)))
    return canvas.filter(ImageFilter.SMOOTH_MORE).point(lambda value: 255 if value >= 96 else 0)


def silhouette_from_image(image: Image.Image) -> Image.Image:
    try:
        working = image.copy()
        working.thumbnail((768, 768), Image.Resampling.LANCZOS)
        mask = _fit_mask(_foreground_mask(working))
        outline = mask.filter(ImageFilter.MaxFilter(5))
        result = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        result.paste(Image.new("RGBA", CANVAS, OUTLINE), mask=outline)
        result.paste(Image.new("RGBA", CANVAS, INK), mask=mask)
        return result
    except Exception:
        logger.exception("Failed to build a silhouette from an in-memory image.")
        raise


def _is_gold_rim(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue = pixel[:3]
    return red >= 120 and 70 <= green <= 210 and blue <= 110 and (red - blue) >= 40


def _subject_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    try:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        pixels = rgba.load()
        left, top, right, bottom = width, height, 0, 0
        found = False
        step = 2
        for y in range(0, height, step):
            for x in range(0, width, step):
                if _is_gold_rim(pixels[x, y]):
                    found = True
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x + step)
                    bottom = max(bottom, y + step)
        if not found:
            box = rgba.getbbox()
            if box is None:
                raise ValueError("Approved silhouette has no visible subject.")
            return box
        return (left, top, right + 1, bottom + 1)
    except Exception:
        logger.exception("Failed to measure a monster silhouette subject.")
        raise


def _expand_box(box: tuple[int, int, int, int], size: tuple[int, int], ratio: float) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    pad = max(8, int(max(right - left, bottom - top) * ratio))
    return (
        max(0, left - pad),
        max(0, top - pad),
        min(size[0], right + pad),
        min(size[1], bottom + pad),
    )


def _vignette_canvas(size: tuple[int, int], inner: tuple[int, int, int], outer: tuple[int, int, int]) -> Image.Image:
    try:
        width, height = size
        canvas = Image.new("RGB", size, outer)
        pixels = canvas.load()
        cx, cy = (width - 1) / 2, height * 0.46
        max_dist = (cx ** 2 + (height * 0.72) ** 2) ** 0.5
        for y in range(height):
            for x in range(width):
                t = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / max_dist)
                falloff = t * t * (3 - 2 * t)
                pixels[x, y] = tuple(int(inner[i] * (1 - falloff) + outer[i] * falloff) for i in range(3))
        return canvas.convert("RGBA")
    except Exception:
        logger.exception("Failed to paint an amber vignette canvas.")
        raise


def frame_monster_vignette(image: Image.Image) -> Image.Image:
    try:
        rgba = image.convert("RGBA")
        box = _expand_box(_subject_bbox(rgba), rgba.size, 0.06)
        subject = rgba.crop(box)
        scale = min(SAFE_SQUARE / max(1, subject.width), SAFE_SQUARE / max(1, subject.height))
        fitted = subject.resize(
            (max(1, int(subject.width * scale)), max(1, int(subject.height * scale))),
            Image.Resampling.LANCZOS,
        )
        canvas = _vignette_canvas(HERO_CANVAS, VIGNETTE_INNER, VIGNETTE_OUTER)
        faded = fitted.convert("RGBA")
        mask = Image.new("L", faded.size, 0)
        inset = max(18, min(faded.size) // 12)
        ImageDraw.Draw(mask).rectangle(
            (inset, inset, faded.width - inset - 1, faded.height - inset - 1), fill=255,
        )
        faded.putalpha(mask.filter(ImageFilter.GaussianBlur(22)))
        left = (HERO_CANVAS[0] - faded.width) // 2
        top = (HERO_CANVAS[1] - faded.height) // 2
        canvas.alpha_composite(faded, (left, top))
        return canvas.convert("RGB")
    except Exception:
        logger.exception("Failed to frame a monster silhouette without clipping.")
        raise


def frame_hero_portrait(image: Image.Image) -> Image.Image:
    try:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        target = HERO_CANVAS[0] / HERO_CANVAS[1]
        current = width / max(1, height)
        if current > target:
            new_width = max(1, int(height * target))
            left = (width - new_width) // 2
            box = (left, 0, left + new_width, height)
        else:
            new_height = max(1, int(width / target))
            top = max(0, int((height - new_height) * 0.12))
            box = (0, top, width, min(height, top + new_height))
        cropped = rgba.crop(box).resize(HERO_CANVAS, Image.Resampling.LANCZOS)
        return cropped.filter(ImageFilter.UnsharpMask(radius=1.1, percent=70, threshold=2))
    except Exception:
        logger.exception("Failed to frame a hero portrait.")
        raise


def _process_image(image: Image.Image, mode: str) -> Image.Image:
    if mode == "color-frame":
        return frame_hero_portrait(image)
    if mode == "vignette-contain":
        return frame_monster_vignette(image)
    return silhouette_from_image(image)


def process_file(source: Path, destination: Path, mode: str = "silhouette", quality: int = 80) -> Path:
    try:
        if source.resolve() == destination.resolve():
            raise ValueError("Refusing to overwrite an original portrait.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            destination.unlink()
        with Image.open(source) as image:
            processed = _process_image(image, mode)
            save_quality = 92 if mode == "silhouette" else quality
            processed.save(destination, "WEBP", quality=save_quality, method=6)
        logger.info("Wrote %s %s from %s", mode, destination, source)
        return destination
    except Exception:
        logger.exception("Failed to process portrait %s", source)
        raise


def process_tree(source_dir: Path, destination_dir: Path, mode: str = "silhouette", quality: int = 80) -> list[Path]:
    try:
        if source_dir.resolve() == destination_dir.resolve():
            raise ValueError("Input and output directories must be different so originals stay intact.")
        if mode not in {"silhouette", "color-frame", "vignette-contain"}:
            raise ValueError("Mode must be silhouette, color-frame, or vignette-contain.")
        written: list[Path] = []
        for source in sorted(source_dir.rglob("*")):
            if source.suffix.lower() not in SUPPORTED or not source.is_file():
                continue
            relative = source.relative_to(source_dir).with_suffix(".webp")
            written.append(process_file(source, destination_dir / relative, mode, quality))
        return written
    except Exception:
        logger.exception("Portrait export failed for %s", source_dir)
        raise


def _self_test() -> None:
    try:
        with tempfile.TemporaryDirectory() as raw:
            source_dir = Path(raw) / "originals"
            output_dir = Path(raw) / "silhouettes"
            source_dir.mkdir()
            original = Image.new("RGB", (240, 240), (210, 186, 140))
            draw = ImageDraw.Draw(original)
            draw.ellipse((70, 28, 150, 108), fill=(198, 142, 96))
            draw.polygon([(88, 100), (132, 100), (160, 210), (60, 210)], fill=(48, 72, 120))
            source = source_dir / "demo-hero.png"
            source.write_bytes(b"")
            original.save(source)
            before = source.read_bytes()
            silhouettes = process_tree(source_dir, output_dir, "silhouette")
            framed_dir = Path(raw) / "heroes"
            framed = process_tree(source_dir, framed_dir, "color-frame")
            after = source.read_bytes()
            if before != after:
                raise RuntimeError("Pipeline overwrote an original portrait.")
            if len(silhouettes) != 1 or len(framed) != 1:
                raise RuntimeError("Pipeline did not write one silhouette and one color frame.")
            result = Image.open(silhouettes[0]).convert("RGBA")
            color = Image.open(framed[0]).convert("RGBA")
            if result.size != CANVAS or color.size != HERO_CANVAS:
                raise RuntimeError(f"Canvas was {result.size}/{color.size}, expected {CANVAS}/{HERO_CANVAS}.")
            opaque = [pixel for pixel in result.getdata() if pixel[3] > 200]
            if len(opaque) < 4000:
                raise RuntimeError("Silhouette is empty.")
            if any(pixel[0] > 40 and pixel[3] > 200 for pixel in opaque if pixel[1] < 40):
                raise RuntimeError("Silhouette fill is not ink-dark.")
            if max(pixel[2] for pixel in color.getdata()) < 80:
                raise RuntimeError("Hero color-frame lost its color.")
            wide = Image.new("RGB", (320, 160), (12, 7, 3))
            draw = ImageDraw.Draw(wide)
            draw.ellipse((20, 30, 300, 130), fill=(8, 6, 4), outline=(201, 163, 90), width=3)
            wide_path = source_dir / "wide-wyvern.jpg"
            wide.save(wide_path)
            contained_dir = Path(raw) / "monsters"
            contained = process_tree(source_dir, contained_dir, "vignette-contain")
            framed_monster = Image.open(next(path for path in contained if path.stem == "wide-wyvern")).convert("RGB")
            if framed_monster.size != HERO_CANVAS:
                raise RuntimeError(f"Vignette-contain canvas was {framed_monster.size}, expected {HERO_CANVAS}.")
            if framed_monster.getpixel((8, 8))[0] < 8:
                raise RuntimeError("Vignette-contain did not extend the amber background.")
            logger.info("Portrait pipeline self-test passed.")
    except Exception:
        logger.exception("Portrait silhouette self-test failed.")
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Directory of original portraits")
    parser.add_argument("--output", type=Path, help="Directory for new processed assets")
    parser.add_argument("--mode", choices=("silhouette", "color-frame", "vignette-contain"), default="silhouette",
                        help="silhouette = ink cutout; color-frame = hero portraits; vignette-contain = approved silhouettes")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality for processed assets")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.self_test:
            _self_test()
            return 0
        if not args.input or not args.output:
            raise ValueError("Provide --input and --output, or use --self-test.")
        written = process_tree(args.input, args.output, args.mode, args.quality)
        logger.info("Processed %s portrait(s) as %s.", len(written), args.mode)
        return 0
    except Exception:
        logger.exception("Portrait pipeline failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
