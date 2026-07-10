#!/usr/bin/env python3
"""Build clean bilingual captions for Blu from supplied lyrics."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "ke1YZYld0MY"
LYRICS = ROOT / "lyrics" / f"blue.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - Blu (Live Acoustic) - Arena di Verona [{YT_ID}].srt"

# Timings are anchored from the fresh Whisper and Parakeet runs in:
# - work/ke1YZYld0MY/whisper-video/ke1YZYld0MY.srt
# - work/ke1YZYld0MY/parakeet-video/Zucchero - Blu ... .srt
TIMINGS = [
    ("00:00:12,800", "00:00:15,440"),
    ("00:00:16,080", "00:00:18,720"),
    ("00:00:19,680", "00:00:23,600"),
    ("00:00:23,840", "00:00:26,800"),
    ("00:00:28,000", "00:00:30,720"),
    ("00:00:31,680", "00:00:33,920"),
    ("00:00:35,800", "00:00:38,700"),
    ("00:00:38,700", "00:00:41,680"),
    ("00:00:42,560", "00:00:44,640"),
    ("00:00:48,480", "00:00:53,840"),
    ("00:00:54,560", "00:00:58,880"),
    ("00:01:01,760", "00:01:06,960"),
    ("00:01:07,600", "00:01:12,640"),
    ("00:01:13,920", "00:01:19,360"),
    ("00:01:20,320", "00:01:24,800"),
    ("00:01:27,680", "00:01:32,000"),
    ("00:01:32,000", "00:01:34,480"),
    ("00:01:35,040", "00:01:38,800"),
    ("00:01:39,440", "00:01:43,200"),
    ("00:01:43,200", "00:01:46,560"),
    ("00:01:47,200", "00:01:50,000"),
    ("00:01:52,720", "00:01:54,560"),
    ("00:01:55,200", "00:01:57,600"),
    ("00:01:58,480", "00:02:01,000"),
    ("00:02:04,680", "00:02:07,000"),
    ("00:02:07,000", "00:02:09,800"),
    ("00:02:10,440", "00:02:15,800"),
    ("00:02:18,120", "00:02:23,560"),
    ("00:02:24,040", "00:02:28,680"),
    ("00:02:29,960", "00:02:35,480"),
    ("00:02:36,360", "00:02:40,760"),
    ("00:03:17,720", "00:03:21,480"),
    ("00:03:21,480", "00:03:22,360"),
    ("00:03:24,280", "00:03:25,480"),
    ("00:03:29,880", "00:03:35,480"),
    ("00:03:35,960", "00:03:39,800"),
    ("00:03:40,280", "00:03:44,960"),
    ("00:03:49,120", "00:03:53,600"),
    ("00:03:54,880", "00:04:00,560"),
    ("00:04:01,360", "00:04:06,240"),
    ("00:04:07,120", "00:04:09,360"),
    ("00:04:10,000", "00:04:12,320"),
    ("00:04:12,960", "00:04:17,920"),
    ("00:04:19,200", "00:04:24,640"),
    ("00:04:25,440", "00:04:30,560"),
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
