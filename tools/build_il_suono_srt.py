#!/usr/bin/env python3
"""Build clean bilingual captions for Il Suono Della Domenica."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "qWPy_XDm0FQ"
LYRICS = ROOT / "lyrics" / f"il-suono-della-domenica.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
GENERIC_CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - Il Suono Della Domenica [{YT_ID}].srt"

# Timings are anchored from:
# - work/qWPy_XDm0FQ/whisper-prompted/qWPy_XDm0FQ.srt
# - work/qWPy_XDm0FQ/parakeet-video/Zucchero - Il Suono Della Domenica [qWPy_XDm0FQ].srt
#
# Prompted Whisper removed the old repeated-outro failure; Parakeet gives finer
# line breaks. The local lyric file is the text authority.
TIMINGS = [
    ("00:00:08,720", "00:00:14,800"),
    ("00:00:16,080", "00:00:22,960"),
    ("00:00:24,560", "00:00:27,760"),
    ("00:00:28,400", "00:00:31,840"),
    ("00:00:32,480", "00:00:35,600"),
    ("00:00:36,240", "00:00:36,960"),
    ("00:00:41,680", "00:00:43,840"),
    ("00:00:46,000", "00:00:49,200"),
    ("00:00:49,840", "00:00:51,760"),
    ("00:00:53,680", "00:00:56,320"),
    ("00:00:58,240", "00:00:59,840"),
    ("00:01:07,200", "00:01:13,280"),
    ("00:01:15,040", "00:01:21,840"),
    ("00:01:23,600", "00:01:26,320"),
    ("00:01:26,960", "00:01:30,260"),
    ("00:01:30,860", "00:01:35,040"),
    ("00:01:35,040", "00:01:35,520"),
    ("00:01:40,560", "00:01:42,400"),
    ("00:01:44,480", "00:01:47,600"),
    ("00:01:48,400", "00:01:50,160"),
    ("00:01:52,560", "00:01:54,640"),
    ("00:01:56,720", "00:01:58,460"),
    ("00:02:05,160", "00:02:12,360"),
    ("00:02:13,000", "00:02:20,440"),
    ("00:02:21,080", "00:02:26,520"),
    ("00:02:27,320", "00:02:31,960"),
    ("00:02:36,680", "00:02:38,760"),
    ("00:02:40,360", "00:02:43,880"),
    ("00:02:44,840", "00:02:46,040"),
    ("00:02:48,600", "00:02:51,240"),
    ("00:02:52,520", "00:02:55,000"),
    ("00:03:00,760", "00:03:03,080"),
    ("00:03:04,680", "00:03:08,120"),
    ("00:03:08,760", "00:03:10,840"),
    ("00:03:12,760", "00:03:15,880"),
    ("00:03:17,400", "00:03:19,000"),
    ("00:03:25,560", "00:03:30,200"),
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


def main() -> None:
    text = render()
    for path in (CAPTION_OUT, GENERIC_CAPTION_OUT, WORK_OUT, SIDECAR_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
