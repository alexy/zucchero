#!/usr/bin/env python3
"""Build clean bilingual captions for Spirito Nel Buio from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LYRICS = ROOT / "lyrics" / "buio.Dz0Okxx9_u8.en-it.txt"
CAPTION_OUT = ROOT / "captions" / "Dz0Okxx9_u8.en-it.srt"
WORK_OUT = ROOT / "work" / "Dz0Okxx9_u8" / "final" / "Dz0Okxx9_u8.en-it.srt"

# Timings are anchored from the fresh Whisper and Parakeet runs in:
# - work/Dz0Okxx9_u8/whisper-audio/Dz0Okxx9_u8.srt
# - work/Dz0Okxx9_u8/parakeet/Zucchero - Spirito Nel Buio [Dz0Okxx9_u8].f140.srt
TIMINGS = [
    ("00:00:25,600", "00:00:28,160"),
    ("00:00:29,680", "00:00:32,560"),
    ("00:00:33,840", "00:00:36,560"),
    ("00:00:38,160", "00:00:41,520"),
    ("00:00:42,160", "00:00:45,840"),
    ("00:00:46,640", "00:00:49,520"),
    ("00:00:50,720", "00:00:54,640"),
    ("00:00:55,200", "00:00:58,560"),
    ("00:01:01,440", "00:01:02,240"),
    ("00:01:07,000", "00:01:08,600"),
    ("00:01:14,400", "00:01:17,360"),
    ("00:01:18,560", "00:01:21,520"),
    ("00:01:22,480", "00:01:25,920"),
    ("00:01:27,440", "00:01:30,000"),
    ("00:01:30,640", "00:01:34,800"),
    ("00:01:35,440", "00:01:38,560"),
    ("00:01:39,520", "00:01:44,560"),
    ("00:01:44,560", "00:01:47,600"),
    ("00:01:50,320", "00:01:50,960"),
    ("00:01:52,800", "00:01:55,500"),
    ("00:01:55,510", "00:01:57,410"),
    ("00:02:03,160", "00:02:06,570"),
    ("00:02:07,480", "00:02:09,910"),
    ("00:02:11,290", "00:02:15,230"),
    ("00:02:15,880", "00:02:18,850"),
    ("00:02:20,280", "00:02:23,960"),
    ("00:02:24,450", "00:02:27,160"),
    ("00:02:30,600", "00:02:31,640"),
    ("00:02:33,160", "00:02:35,300"),
    ("00:02:35,730", "00:02:37,650"),
    ("00:02:41,240", "00:02:41,960"),
    ("00:02:45,800", "00:02:48,760"),
    ("00:02:50,200", "00:02:53,960"),
    ("00:02:54,280", "00:02:57,610"),
    ("00:02:58,600", "00:03:01,410"),
    ("00:03:02,600", "00:03:06,680"),
    ("00:03:06,920", "00:03:09,400"),
    ("00:03:10,680", "00:03:14,680"),
    ("00:03:15,160", "00:03:15,900"),
    ("00:03:22,630", "00:03:28,280"),
    ("00:03:31,000", "00:03:32,760"),
    ("00:03:33,000", "00:03:34,600"),
    ("00:03:36,760", "00:03:38,600"),
    ("00:03:39,000", "00:03:40,500"),
    ("00:03:40,500", "00:03:42,000"),
    ("00:03:42,000", "00:03:43,500"),
    ("00:03:43,500", "00:03:45,000"),
    ("00:03:45,000", "00:03:47,000"),
    ("00:03:47,000", "00:03:49,000"),
    ("00:03:49,000", "00:03:50,600"),
    ("00:03:50,600", "00:03:51,940"),
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
    CAPTION_OUT.parent.mkdir(parents=True, exist_ok=True)
    WORK_OUT.parent.mkdir(parents=True, exist_ok=True)
    CAPTION_OUT.write_text(text, encoding="utf-8")
    WORK_OUT.write_text(text, encoding="utf-8")
    print(f"wrote {CAPTION_OUT}")
    print(f"wrote {WORK_OUT}")


if __name__ == "__main__":
    main()
