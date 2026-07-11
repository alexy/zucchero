#!/usr/bin/env python3
"""Build clean bilingual captions for Diamante from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "jlp3APIK7SA"
LYRICS = ROOT / "lyrics" / f"diamante.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
GENERIC_CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - Diamante [{YT_ID}].srt"

# Timings are anchored from a fresh prompted Whisper pass against
# work/jlp3APIK7SA/source/Zucchero - Diamante [jlp3APIK7SA].mp4, plus a Parakeet
# comparison pass. The local lyric file is the text authority.
TIMINGS = [
    ("00:00:36,920", "00:00:38,560"),
    ("00:00:38,600", "00:00:42,080"),
    ("00:00:44,200", "00:00:47,840"),
    ("00:00:47,880", "00:00:50,200"),
    ("00:00:52,900", "00:00:55,560"),
    ("00:00:55,600", "00:00:59,340"),
    ("00:01:00,760", "00:01:05,100"),
    ("00:01:05,140", "00:01:07,340"),
    ("00:01:12,360", "00:01:16,740"),
    ("00:01:20,000", "00:01:25,300"),
    ("00:01:28,140", "00:01:29,660"),
    ("00:01:50,660", "00:01:56,080"),
    ("00:01:57,380", "00:02:00,900"),
    ("00:02:00,940", "00:02:03,680"),
    ("00:02:06,340", "00:02:09,100"),
    ("00:02:09,140", "00:02:12,800"),
    ("00:02:14,580", "00:02:18,640"),
    ("00:02:18,680", "00:02:20,820"),
    ("00:02:24,740", "00:02:30,140"),
    ("00:02:33,160", "00:02:38,840"),
    ("00:02:43,100", "00:02:47,660"),
    ("00:02:48,000", "00:02:55,980"),
    ("00:02:58,880", "00:03:04,780"),
    ("00:03:07,000", "00:03:13,000"),
    ("00:03:17,000", "00:03:23,000"),
    ("00:03:27,000", "00:03:33,000"),
    ("00:03:51,180", "00:03:55,900"),
    ("00:03:57,420", "00:04:04,800"),
    ("00:04:04,840", "00:04:14,080"),
    ("00:04:17,120", "00:04:22,700"),
    ("00:05:14,200", "00:05:18,260"),
]


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[A-Za-zÀ-ÿ']+", text.casefold()))


def lyric_pairs() -> list[tuple[str, str]]:
    lines = [line.strip() for line in LYRICS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) % 2:
        raise SystemExit(f"Expected even English/Italian lyric lines in {LYRICS}, got {len(lines)}")
    return [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]


def render() -> str:
    pairs = lyric_pairs()
    if len(pairs) != len(TIMINGS):
        raise SystemExit(f"Expected {len(TIMINGS)} lyric pairs, got {len(pairs)}")

    blocks = []
    for index, ((english, italian), (start, end)) in enumerate(zip(pairs, TIMINGS), start=1):
        lines = [str(index), f"{start} --> {end}", italian]
        if normalize(english) != normalize(italian):
            lines.append(english)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def write_output(path: Path, text: str) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except PermissionError as exc:
        print(f"skipped {path}: {exc}")
        return False
    print(f"wrote {path}")
    return True


def main() -> None:
    text = render()
    for path in (CAPTION_OUT, GENERIC_CAPTION_OUT, WORK_OUT, SIDECAR_OUT):
        write_output(path, text)


if __name__ == "__main__":
    main()
