#!/usr/bin/env python3
"""Build clean bilingual captions for Amor Che Muovi Il Sole from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "_igNxWonKfs"
LYRICS = ROOT / "lyrics" / f"amor-che-muove-il-sol.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - Amor Che Muovi Il Sole [{YT_ID}].srt"

# Timings are anchored from the fresh recognizer runs in:
# - work/_igNxWonKfs/whisper-video/_igNxWonKfs.srt
# - work/_igNxWonKfs/parakeet-video/Zucchero - Amor Che Muovi Il Sole [_igNxWonKfs].srt
#
# Parakeet gives the stronger lyric-line structure for this track. Whisper
# confirms full media coverage, but the later vocalizations collapse into
# repeated one-word cues and are not used as lyric text authority.
TIMINGS = [
    ("00:00:06,000", "00:00:10,160"),
    ("00:00:12,160", "00:00:13,440"),
    ("00:00:14,640", "00:00:17,600"),
    ("00:00:19,520", "00:00:24,560"),
    ("00:00:27,120", "00:00:31,040"),
    ("00:01:04,000", "00:01:05,120"),
    ("00:01:06,240", "00:01:08,640"),
    ("00:01:09,440", "00:01:11,360"),
    ("00:01:11,360", "00:01:14,720"),
    ("00:01:15,680", "00:01:17,840"),
    ("00:01:18,800", "00:01:20,840"),
    ("00:01:20,840", "00:01:22,400"),
    ("00:01:22,400", "00:01:24,240"),
    ("00:01:26,400", "00:01:30,560"),
    ("00:01:32,480", "00:01:33,440"),
    ("00:01:34,720", "00:01:37,200"),
    ("00:01:38,560", "00:01:43,120"),
    ("00:01:43,680", "00:01:49,280"),
    ("00:01:50,640", "00:01:53,440"),
    ("00:01:53,680", "00:01:54,600"),
    ("00:01:54,600", "00:01:59,200"),
    ("00:01:59,840", "00:02:01,960"),
    ("00:02:03,160", "00:02:05,300"),
    ("00:02:05,300", "00:02:08,600"),
    ("00:02:10,280", "00:02:14,440"),
    ("00:02:34,080", "00:02:40,120"),
    ("00:02:41,960", "00:02:43,240"),
    ("00:02:44,120", "00:02:46,520"),
    ("00:02:48,760", "00:02:52,680"),
    ("00:02:53,240", "00:02:58,760"),
    ("00:03:00,040", "00:03:02,200"),
    ("00:03:02,840", "00:03:05,080"),
    ("00:03:05,160", "00:03:06,300"),
    ("00:03:06,300", "00:03:08,280"),
    ("00:03:09,400", "00:03:11,560"),
    ("00:03:12,920", "00:03:14,600"),
    ("00:03:14,600", "00:03:17,800"),
    ("00:03:20,600", "00:03:23,960"),
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
