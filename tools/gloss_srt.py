#!/usr/bin/env python3
"""Create literal word-gloss study captions from an SRT file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOSSARY = ROOT / "data" / "glossary.tsv"
WORD_RE = re.compile(r"\b[\wÀ-ÿ']+\b", re.UNICODE)


def load_glossary(path: Path) -> dict[str, str]:
    glossary: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            italian, english = line.split("\t", 1)
        except ValueError as exc:
            raise SystemExit(f"{path}:{line_number}: expected tab-separated italian/english") from exc
        glossary[italian.casefold()] = english.strip()
    return glossary


def parse_srt(text: str) -> list[tuple[str, str, list[str]]]:
    blocks: list[tuple[str, str, list[str]]] = []
    for raw_block in re.split(r"\n\s*\n", text.strip()):
        lines = raw_block.splitlines()
        if len(lines) < 3:
            continue
        index = lines[0].strip()
        timing = lines[1].strip()
        captions = [line.strip() for line in lines[2:] if line.strip()]
        blocks.append((index, timing, captions))
    return blocks


def gloss_line(line: str, glossary: dict[str, str], unknown_marker: str) -> str:
    glosses: list[str] = []
    for match in WORD_RE.finditer(line):
        word = match.group(0)
        gloss = glossary.get(word.casefold())
        glosses.append(gloss if gloss else f"{unknown_marker}{word}{unknown_marker}")
    return " ".join(glosses)


def render(blocks: list[tuple[str, str, list[str]]], glossary: dict[str, str], unknown_marker: str) -> str:
    rendered: list[str] = []
    for index, timing, captions in blocks:
        rendered.append(index)
        rendered.append(timing)
        for caption in captions:
            rendered.append(caption)
            rendered.append(gloss_line(caption, glossary, unknown_marker))
        rendered.append("")
    return "\n".join(rendered).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Input .srt file")
    parser.add_argument("destination", type=Path, help="Output study-caption text file")
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    parser.add_argument("--unknown-marker", default="?", help="Marker around unknown words")
    args = parser.parse_args()

    glossary = load_glossary(args.glossary)
    blocks = parse_srt(args.source.read_text(encoding="utf-8"))
    output = render(blocks, glossary, args.unknown_marker)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()

