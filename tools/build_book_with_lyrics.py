#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from build_song_manifest import render_markdown as render_song_manifest_markdown
from build_song_manifest import write_song_manifest


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "docs" / "book"
DEFAULT_APPENDIX = BOOK_DIR / "private" / "lyrics-appendix.md"
DEFAULT_EXTENSIONS = (".txt",)


@dataclass(frozen=True)
class LyricFile:
    path: Path
    title: str
    text: str
    format: str
    units: int


def natural_parts(value: str) -> tuple[tuple[int, object], ...]:
    parts: list[tuple[int, object]] = []
    for piece in re.split(r"(\d+)", value):
        if not piece:
            continue
        parts.append((0, int(piece)) if piece.isdigit() else (1, piece.casefold()))
    return tuple(parts)


def natural_path_key(path: Path) -> tuple[tuple[tuple[int, object], ...], ...]:
    return tuple(natural_parts(part) for part in path.parts)


def title_from_path(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"\.(?:en-it|it|en)$", "", stem)
    stem = re.sub(r"\.[A-Za-z0-9_-]{6,}$", "", stem)
    stem = re.sub(r"^\d+[\s._-]+", "", stem)
    stem = stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip(" .")
    return stem.title() or path.stem


def format_and_units(path: Path, text: str) -> tuple[str, int]:
    nonblank = [line for line in text.splitlines() if line.strip()]
    if ".en-it." in path.name and len(nonblank) % 2 == 0:
        return "English/Italian pairs", len(nonblank) // 2
    if ".it." in path.name:
        return "Italian-only lyric lines", len(nonblank)
    if len(nonblank) % 2 == 0:
        return "Possible English/Italian pairs", len(nonblank) // 2
    return "Lyric lines", len(nonblank)


def read_lyric_file(path: Path) -> LyricFile | None:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        print(f"Skipping empty lyric file: {path}")
        return None
    lyric_format, units = format_and_units(path, text)
    return LyricFile(
        path=path,
        title=title_from_path(path),
        text=text,
        format=lyric_format,
        units=units,
    )


def find_lyric_files(lyrics_dir: Path, extensions: set[str], recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    paths = [
        path
        for path in lyrics_dir.glob(pattern)
        if path.is_file() and path.suffix.casefold() in extensions
    ]
    return sorted(paths, key=natural_path_key)


def code_fence_for(text: str) -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return fence


def relative_display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def render_appendix(entries: list[LyricFile], song_manifest_markdown: str) -> str:
    lines = [
        song_manifest_markdown.rstrip(),
        "",
        "## Appendice privata: testi locali",
        "## Private Appendix: Local Lyrics",
        "",
        "Questa appendice e generata da file locali per lo studio privato.\\",
        "_This appendix is generated from local files for private study._",
        "",
        "Non e destinata alla pubblicazione su GitHub o First Pair.\\",
        "_It is not intended for publication on GitHub or First Pair._",
        "",
    ]

    for entry in entries:
        fence = code_fence_for(entry.text)
        lines.extend(
            [
                f"### {entry.title}",
                "",
                f"_Fonte locale: `{relative_display_path(entry.path)}`_\\",
                f"_Local source: `{relative_display_path(entry.path)}`_",
                "",
                f"_Formato: {entry.format}; unita: {entry.units}._\\",
                f"_Format: {entry.format}; units: {entry.units}._",
                "",
                f"{fence}text",
                entry.text,
                fence,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_appendix(
    lyrics_dir: Path,
    appendix: Path,
    extensions: set[str],
    recursive: bool,
) -> list[LyricFile]:
    paths = find_lyric_files(lyrics_dir, extensions, recursive)
    entries = [entry for path in paths if (entry := read_lyric_file(path))]
    if not entries:
        allowed = ", ".join(sorted(extensions))
        raise SystemExit(f"No lyric files found in {lyrics_dir} with extensions: {allowed}")

    appendix.parent.mkdir(parents=True, exist_ok=True)
    song_rows = write_song_manifest(lyrics_dir, appendix.parent)
    appendix.write_text(render_appendix(entries, render_song_manifest_markdown(song_rows)), encoding="utf-8")
    print(f"Generated {appendix} from {len(entries)} lyric files")
    return entries


def rebuild_book(appendix: Path) -> None:
    env = os.environ.copy()
    env["INCLUDE_LOCAL_LYRICS"] = "1"
    env["PRIVATE_LYRICS_APPENDIX"] = str(appendix)
    subprocess.run(["python3", "tools/build_book.py"], cwd=ROOT, env=env, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a private lyrics appendix from a lyrics directory and rebuild the book."
    )
    parser.add_argument("lyrics_dir", type=Path, help="Directory containing local lyric files")
    parser.add_argument("--appendix", type=Path, default=DEFAULT_APPENDIX)
    parser.add_argument("--no-build", action="store_true", help="Only generate the appendix")
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
    lyrics_dir = args.lyrics_dir.expanduser().resolve()
    if not lyrics_dir.is_dir():
        raise SystemExit(f"Lyrics directory not found: {lyrics_dir}")

    raw_extensions = args.extensions if args.extensions else DEFAULT_EXTENSIONS
    extensions = {
        extension.casefold() if extension.startswith(".") else f".{extension.casefold()}"
        for extension in raw_extensions
    }
    appendix = args.appendix.expanduser().resolve()
    write_appendix(lyrics_dir, appendix, extensions, recursive=not args.flat)

    if not args.no_build:
        rebuild_book(appendix)


if __name__ == "__main__":
    main()
