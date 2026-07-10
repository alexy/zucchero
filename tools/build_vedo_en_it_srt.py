#!/usr/bin/env python3
"""Build clean bilingual captions for Vedo Nero from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "Z43t5mXB4Mo"
LYRICS = ROOT / "lyrics" / f"vedo.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - Vedo Nero [{YT_ID}].srt"

# Timings are anchored from the fresh Whisper and Parakeet runs in:
# - work/Z43t5mXB4Mo/whisper/Z43t5mXB4Mo.srt
# - work/Z43t5mXB4Mo/parakeet-video/Zucchero - Vedo Nero [Z43t5mXB4Mo].srt
#
# Whisper gives the stronger whole-song sequence. Parakeet gives useful split
# points where Whisper merges short adjacent lyric lines, especially at the
# beginning and in the outro.
TIMINGS = [
    ("00:00:38,300", "00:00:39,840"),
    ("00:00:39,840", "00:00:41,400"),
    ("00:00:41,400", "00:00:42,320"),
    ("00:00:42,320", "00:00:44,740"),
    ("00:00:45,820", "00:00:47,040"),
    ("00:00:47,600", "00:00:48,820"),
    ("00:00:49,620", "00:00:50,560"),
    ("00:00:50,560", "00:00:52,300"),
    ("00:00:53,140", "00:00:57,140"),
    ("00:01:00,440", "00:01:04,980"),
    ("00:01:07,600", "00:01:09,000"),
    ("00:01:09,000", "00:01:11,600"),
    ("00:01:11,600", "00:01:15,420"),
    ("00:01:15,420", "00:01:17,500"),
    ("00:01:17,500", "00:01:19,280"),
    ("00:01:19,280", "00:01:22,400"),
    ("00:01:22,400", "00:01:23,120"),
    ("00:01:23,120", "00:01:24,700"),
    ("00:01:24,700", "00:01:26,240"),
    ("00:01:26,240", "00:01:27,420"),
    ("00:01:29,380", "00:01:31,140"),
    ("00:01:36,140", "00:01:39,260"),
    ("00:01:45,620", "00:01:47,460"),
    ("00:01:47,460", "00:01:49,400"),
    ("00:01:50,100", "00:01:52,840"),
    ("00:01:53,900", "00:01:55,040"),
    ("00:01:55,040", "00:01:56,840"),
    ("00:01:57,700", "00:01:58,900"),
    ("00:01:58,900", "00:02:00,340"),
    ("00:02:00,340", "00:02:05,360"),
    ("00:02:09,280", "00:02:12,860"),
    ("00:02:13,580", "00:02:15,300"),
    ("00:02:16,740", "00:02:18,000"),
    ("00:02:18,000", "00:02:20,860"),
    ("00:02:20,860", "00:02:23,380"),
    ("00:02:23,380", "00:02:25,300"),
    ("00:02:25,300", "00:02:27,300"),
    ("00:02:27,300", "00:02:31,080"),
    ("00:02:31,080", "00:02:32,500"),
    ("00:02:32,500", "00:02:34,800"),
    ("00:02:34,800", "00:02:38,580"),
    ("00:02:38,580", "00:02:40,500"),
    ("00:02:40,500", "00:02:42,360"),
    ("00:02:42,360", "00:02:45,400"),
    ("00:02:45,400", "00:02:46,300"),
    ("00:02:46,300", "00:02:47,850"),
    ("00:02:47,850", "00:02:49,420"),
    ("00:02:49,520", "00:02:50,600"),
    ("00:02:52,480", "00:02:54,400"),
    ("00:03:00,020", "00:03:02,460"),
    ("00:03:04,760", "00:03:09,140"),
    ("00:03:09,140", "00:03:10,660"),
    ("00:03:11,080", "00:03:15,780"),
    ("00:03:15,780", "00:03:18,720"),
    ("00:03:20,680", "00:03:21,600"),
    ("00:03:22,540", "00:03:24,240"),
    ("00:03:24,240", "00:03:26,600"),
    ("00:03:27,140", "00:03:28,780"),
    ("00:03:28,780", "00:03:29,600"),
    ("00:03:29,600", "00:03:32,560"),
    ("00:03:32,560", "00:03:33,720"),
    ("00:03:37,880", "00:03:39,960"),
    ("00:03:40,600", "00:03:41,080"),
    ("00:03:41,640", "00:03:43,520"),
    ("00:03:43,520", "00:03:44,800"),
    ("00:03:44,920", "00:03:47,200"),
    ("00:03:47,200", "00:03:48,560"),
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
    for path in (CAPTION_OUT, WORK_OUT, SIDECAR_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
