#!/usr/bin/env python3
"""Render the checked-in Zucchero cover and headboard artwork.

This is an optional cover-production helper, not part of the book build. It
requires Pillow and the canonical First Pair publisher mask from the sibling
FirstPair checkout.
"""

from __future__ import annotations

import argparse
import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "book" / "assets"
SOURCE_DIR = ASSET_DIR / "source"
DEFAULT_FIRSTPAIR_ROOT = ROOT.parent / "firstpair"
DEFAULT_FONT = Path("/System/Library/Fonts/Supplemental/Baskerville.ttc")

COVER_SIZE = (1800, 2880)
HEADBOARD_SIZE = (2400, 1350)
TITLE = "Imparare l'italiano con Zucchero"
SUBTITLE = "Learn Italian with Zucchero"
AUTHOR = "Alexy Khrabrov con Zucchero"


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    ).convert("RGBA")


def palette_tint(image: Image.Image) -> tuple[int, int, int]:
    """Choose the brightest warm midtone from the cover's own palette."""
    sample = image.convert("RGB")
    sample.thumbnail((320, 320), Image.Resampling.LANCZOS)
    quantized = sample.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    colors = quantized.getcolors() or []
    candidates: list[tuple[float, tuple[int, int, int]]] = []

    for count, index in colors:
        rgb = tuple(palette[index * 3 : index * 3 + 3])
        hue, saturation, value = colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))
        if 0.035 <= hue <= 0.17 and 0.18 <= saturation <= 0.62 and 0.52 <= value <= 0.9:
            candidates.append((value * 2 + saturation + min(count / 5000, 1), rgb))

    if not candidates:
        return (194, 169, 121)
    return max(candidates)[1]


def gradient_overlay(
    image: Image.Image,
    *,
    start_y: int,
    end_alpha: int,
    color: tuple[int, int, int] = (18, 15, 12),
) -> None:
    height = image.height - start_y
    gradient = Image.new("RGBA", (1, height))
    pixels = []
    for y in range(height):
        alpha = round(end_alpha * (y / max(height - 1, 1)) ** 1.35)
        pixels.append((*color, alpha))
    gradient.putdata(pixels)
    gradient = gradient.resize((image.width, height))
    image.alpha_composite(gradient, (0, start_y))


def tinted_mark(
    mask_path: Path,
    *,
    color: tuple[int, int, int],
    width: int,
    max_alpha: int,
) -> Image.Image:
    mask = Image.open(mask_path).convert("L")
    height = round(mask.height * width / mask.width)
    mask = mask.resize((width, height), Image.Resampling.LANCZOS)
    alpha = mask.point(lambda value: round(value * max_alpha / 255))
    mark = Image.new("RGBA", mask.size, (*color, 0))
    mark.putalpha(alpha)
    return mark


def font(path: Path, size: int, index: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size, index=index)


def draw_cover(
    source: Path,
    output: Path,
    mask_path: Path,
    font_path: Path,
) -> tuple[int, int, int]:
    cover = fit(Image.open(source), COVER_SIZE)
    tint = palette_tint(cover)
    dark_ink = (35, 28, 22, 246)
    light_ink = (*tint, 248)
    draw = ImageDraw.Draw(cover, "RGBA")

    title_lines = [
        ("IMPARARE", 146, 118),
        ("L'ITALIANO", 188, 290),
        ("CON ZUCCHERO", 138, 508),
    ]
    for text, size, y in title_lines:
        draw.text(
            (138, y),
            text,
            font=font(font_path, size, 1),
            fill=dark_ink,
            anchor="la",
            stroke_width=1,
            stroke_fill=(220, 194, 149, 120),
        )

    draw.line((142, 700, 650, 700), fill=(78, 91, 73, 210), width=5)
    draw.text(
        (140, 728),
        SUBTITLE.upper(),
        font=font(font_path, 48, 4),
        fill=dark_ink,
        anchor="la",
    )

    gradient_overlay(cover, start_y=2050, end_alpha=158)
    draw = ImageDraw.Draw(cover, "RGBA")
    author_font = font(font_path, 67, 4)
    draw.text(
        (COVER_SIZE[0] // 2 + 2, 2310 + 3),
        AUTHOR,
        font=author_font,
        fill=(0, 0, 0, 150),
        anchor="mm",
    )
    draw.text(
        (COVER_SIZE[0] // 2, 2310),
        AUTHOR,
        font=author_font,
        fill=light_ink,
        anchor="mm",
    )

    mark = tinted_mark(
        mask_path,
        color=tint,
        width=round(COVER_SIZE[0] * 0.26),
        max_alpha=105,
    )
    x = (COVER_SIZE[0] - mark.width) // 2
    y = COVER_SIZE[1] - mark.height - round(COVER_SIZE[1] * 0.01)
    cover.alpha_composite(mark, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    cover.convert("RGB").save(output, format="PNG", optimize=True, compress_level=9)
    return tint


def draw_headboard(
    source: Path,
    output: Path,
) -> None:
    headboard = fit(Image.open(source), HEADBOARD_SIZE)
    output.parent.mkdir(parents=True, exist_ok=True)
    headboard.convert("RGB").save(output, format="PNG", optimize=True, compress_level=9)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firstpair-root", type=Path, default=DEFAULT_FIRSTPAIR_ROOT)
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--cover-art", type=Path, default=SOURCE_DIR / "zucchero-cover-art.png")
    parser.add_argument(
        "--headboard-art",
        type=Path,
        default=SOURCE_DIR / "zucchero-headboard-art.png",
    )
    parser.add_argument("--cover-out", type=Path, default=ASSET_DIR / "zucchero-cover.png")
    parser.add_argument(
        "--headboard-out",
        type=Path,
        default=ASSET_DIR / "zucchero-headboard.png",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mask = args.firstpair_root / "logo" / "firstpair-publisher-mask.png"
    for required in (args.cover_art, args.headboard_art, mask, args.font):
        if not required.exists():
            raise SystemExit(f"missing required asset: {required}")

    tint = draw_cover(args.cover_art, args.cover_out, mask, args.font)
    draw_headboard(args.headboard_art, args.headboard_out)
    print(f"Rendered {args.cover_out}")
    print(f"Rendered {args.headboard_out}")
    print(f"First Pair tint: #{tint[0]:02x}{tint[1]:02x}{tint[2]:02x}")
    print(f"Title: {TITLE}")
    print(f"Author: {AUTHOR}")


if __name__ == "__main__":
    main()
