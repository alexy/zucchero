#!/usr/bin/env python3
"""Build clean bilingual captions for Un Soffio Caldo from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "FkTtldGRxMo"
LYRICS = ROOT / "lyrics" / "un-soffio-caldo.EUmKOY9xxSk.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
GENERIC_CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"ZUCCHERO - UN SOFFIO CALDO OFFICIAL VIDEO [{YT_ID}].srt"

# Timings are anchored from:
# - work/FkTtldGRxMo/whisper-prompted/FkTtldGRxMo.srt
# - work/FkTtldGRxMo/parakeet-video/ZUCCHERO - UN SOFFIO CALDO OFFICIAL VIDEO [FkTtldGRxMo].srt
#
# The prompted Whisper run gives the best full-song section anchors; Parakeet
# gives tighter split points in the opening and middle sections. The local lyric
# file remains the text authority.
TIMINGS = [
    ("00:00:46,200", "00:00:48,900"),
    ("00:00:49,120", "00:00:51,580"),
    ("00:00:54,480", "00:00:56,850"),
    ("00:00:56,850", "00:00:59,900"),
    ("00:01:02,940", "00:01:05,300"),
    ("00:01:05,300", "00:01:08,580"),
    ("00:01:10,400", "00:01:17,100"),
    ("00:01:17,100", "00:01:24,800"),
    ("00:01:24,800", "00:01:33,140"),
    ("00:01:34,800", "00:01:41,840"),
    ("00:01:43,260", "00:01:49,740"),
    ("00:01:51,600", "00:01:58,180"),
    ("00:02:01,420", "00:02:03,900"),
    ("00:02:03,900", "00:02:06,760"),
    ("00:02:10,100", "00:02:14,620"),
    ("00:02:17,620", "00:02:20,440"),
    ("00:02:20,920", "00:02:23,800"),
    ("00:02:25,420", "00:02:29,000"),
    ("00:02:29,000", "00:02:32,300"),
    ("00:02:33,500", "00:02:39,000"),
    ("00:02:40,500", "00:02:48,260"),
    ("00:02:49,980", "00:02:57,080"),
    ("00:02:59,240", "00:03:05,320"),
    ("00:03:06,900", "00:03:13,600"),
    ("00:03:48,780", "00:03:55,200"),
    ("00:03:55,200", "00:04:03,380"),
    ("00:04:06,140", "00:04:12,900"),
    ("00:04:12,900", "00:04:20,280"),
    ("00:04:21,860", "00:04:28,600"),
    ("00:04:34,860", "00:04:36,960"),
]


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[A-Za-zÀ-ÿ']+", text.casefold()))


def lyric_pairs() -> list[tuple[str, str]]:
    lines = [line.strip() for line in LYRICS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) % 2:
        raise SystemExit(f"Expected even English/Italian lyric lines in {LYRICS}")
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


def main() -> None:
    text = render()
    for path in (CAPTION_OUT, GENERIC_CAPTION_OUT, WORK_OUT, SIDECAR_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
