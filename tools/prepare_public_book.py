#!/usr/bin/env python3
"""Generate only the public-safe manuscript consumed by FirstPair."""

from __future__ import annotations

import os

os.environ["INCLUDE_LOCAL_LYRICS"] = "0"
os.environ.pop("PRIVATE_LYRICS_APPENDIX", None)

from build_book import BUILD_DIR, write_generated_manuscript  # noqa: E402


def main() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    manuscript = write_generated_manuscript()
    text = manuscript.read_text(encoding="utf-8")
    if "<!-- LYRIC_INDEX -->" in text or "<!-- PRIVATE_LYRICS -->" in text:
        raise SystemExit("public manuscript placeholders were not fully resolved")
    print(f"Prepared public manuscript: {manuscript}")


if __name__ == "__main__":
    main()
