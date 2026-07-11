#!/usr/bin/env python3
"""Prepare the private lyric-inclusive manuscript consumed by FirstPair."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from build_book import BUILD_DIR, ROOT, write_generated_manuscript
from build_book_with_lyrics import DEFAULT_APPENDIX, DEFAULT_EXTENSIONS, write_appendix


def resolve_repo_path(path: Path) -> Path:
    expanded = path.expanduser()
    return expanded if expanded.is_absolute() else ROOT / expanded


def extension_set(values: list[str] | None) -> set[str]:
    raw = values if values else list(DEFAULT_EXTENSIONS)
    return {
        value.casefold() if value.startswith(".") else f".{value.casefold()}"
        for value in raw
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lyrics-dir", type=Path, default=ROOT / "lyrics")
    parser.add_argument("--appendix", type=Path, default=DEFAULT_APPENDIX)
    parser.add_argument("--flat", action="store_true", help="Read only direct children of lyrics_dir")
    parser.add_argument(
        "--extension",
        action="append",
        dest="extensions",
        help="Lyric extension to include. Can be repeated. Defaults to .txt",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lyrics_dir = resolve_repo_path(args.lyrics_dir).resolve()
    appendix = resolve_repo_path(args.appendix).resolve()

    if not lyrics_dir.is_dir():
        raise SystemExit(f"Lyrics directory not found: {lyrics_dir}")

    entries = write_appendix(
        lyrics_dir,
        appendix,
        extension_set(args.extensions),
        recursive=not args.flat,
    )

    os.environ["INCLUDE_LOCAL_LYRICS"] = "1"
    os.environ["PRIVATE_LYRICS_APPENDIX"] = str(appendix)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    manuscript = write_generated_manuscript()
    text = manuscript.read_text(encoding="utf-8")
    if "<!-- LYRIC_INDEX -->" in text or "<!-- PRIVATE_LYRICS -->" in text:
        raise SystemExit("private manuscript placeholders were not fully resolved")

    print(f"Prepared private manuscript: {manuscript} ({len(entries)} lyric files)")


if __name__ == "__main__":
    main()
