#!/usr/bin/env python3
"""Build clean bilingual captions for 13 Buone Ragioni from supplied lyrics."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YT_ID = "--xzsrU_cK8"
LYRICS = ROOT / "lyrics" / f"13-buone-ragioni.{YT_ID}.en-it.txt"
CAPTION_OUT = ROOT / "captions" / f"{YT_ID}.en-it.srt"
WORK_OUT = ROOT / "work" / YT_ID / "final" / f"{YT_ID}.en-it.srt"
SIDECAR_OUT = ROOT / "video" / "done" / f"Zucchero - 13 Buone Ragioni [{YT_ID}].srt"

# Timings are anchored from the fresh recognizer runs in:
# - work/--xzsrU_cK8/whisper-prompted/--xzsrU_cK8.srt
# - work/--xzsrU_cK8/parakeet-video/--xzsrU_cK8.srt
#
# Prompted Whisper gives the stronger verse wording and phrase splits. Parakeet
# gives cleaner refrain boundaries and identifies all four outro repetitions.
# The supplied bilingual lyric file remains the caption text authority.
TIMINGS = [
    ("00:00:06,840", "00:00:09,520"),
    ("00:00:09,960", "00:00:11,920"),
    ("00:00:11,960", "00:00:13,360"),
    ("00:00:14,360", "00:00:16,480"),
    ("00:00:24,760", "00:00:27,840"),
    ("00:00:27,880", "00:00:30,120"),
    ("00:00:30,200", "00:00:31,440"),
    ("00:00:32,600", "00:00:34,880"),
    ("00:00:37,240", "00:00:39,920"),
    ("00:00:40,360", "00:00:42,280"),
    ("00:00:42,360", "00:00:43,680"),
    ("00:00:44,840", "00:00:46,880"),
    ("00:00:48,920", "00:00:51,960"),
    ("00:00:52,200", "00:00:54,940"),
    ("00:00:54,980", "00:00:58,120"),
    ("00:00:58,200", "00:01:01,160"),
    ("00:01:01,420", "00:01:04,100"),
    ("00:01:04,100", "00:01:07,120"),
    ("00:01:07,120", "00:01:10,160"),
    ("00:01:10,620", "00:01:13,600"),
    ("00:01:16,360", "00:01:19,280"),
    ("00:01:19,320", "00:01:21,760"),
    ("00:01:21,800", "00:01:22,800"),
    ("00:01:23,960", "00:01:26,320"),
    ("00:01:28,440", "00:01:31,440"),
    ("00:01:31,480", "00:01:33,600"),
    ("00:01:33,640", "00:01:34,960"),
    ("00:01:36,440", "00:01:38,480"),
    ("00:01:40,600", "00:01:43,200"),
    ("00:01:43,600", "00:01:46,600"),
    ("00:01:46,640", "00:01:49,640"),
    ("00:01:49,680", "00:01:53,080"),
    ("00:01:54,840", "00:01:56,720"),
    ("00:02:01,040", "00:02:02,840"),
    ("00:02:04,560", "00:02:07,820"),
    ("00:02:07,820", "00:02:10,940"),
    ("00:02:10,940", "00:02:13,680"),
    ("00:02:13,680", "00:02:16,980"),
    ("00:02:16,980", "00:02:20,060"),
    ("00:02:20,060", "00:02:23,080"),
    ("00:02:23,080", "00:02:26,160"),
    ("00:02:26,340", "00:02:29,560"),
    ("00:02:35,520", "00:02:38,360"),
    ("00:02:38,520", "00:02:40,680"),
    ("00:02:40,760", "00:02:42,080"),
    ("00:02:43,920", "00:02:45,280"),
    ("00:02:47,840", "00:02:50,680"),
    ("00:02:50,960", "00:02:52,920"),
    ("00:02:52,960", "00:02:54,240"),
    ("00:02:56,080", "00:02:57,560"),
    ("00:03:01,760", "00:03:03,480"),
    ("00:03:07,840", "00:03:09,640"),
    ("00:03:13,920", "00:03:15,720"),
    ("00:03:20,000", "00:03:21,800"),
]


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[A-Za-zÀ-ÿ']+", text.casefold()))


def lyric_pairs() -> list[tuple[str, str]]:
    lines = [line.strip() for line in LYRICS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) % 2:
        raise SystemExit(f"Expected even English/Italian lyric lines in {LYRICS}")
    return [(lines[index], lines[index + 1]) for index in range(0, len(lines), 2)]


def milliseconds(timestamp: str) -> int:
    match = re.fullmatch(r"(\d\d):(\d\d):(\d\d),(\d\d\d)", timestamp)
    if not match:
        raise SystemExit(f"Malformed SRT timestamp: {timestamp}")
    hours, minutes, seconds, millis = (int(part) for part in match.groups())
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def validate_timings() -> None:
    previous_end = -1
    for index, (start, end) in enumerate(TIMINGS, start=1):
        start_ms = milliseconds(start)
        end_ms = milliseconds(end)
        if end_ms <= start_ms:
            raise SystemExit(f"Cue {index} has non-positive duration")
        if start_ms < previous_end:
            raise SystemExit(f"Cue {index} overlaps the previous cue")
        previous_end = end_ms


def render() -> str:
    pairs = lyric_pairs()
    if len(pairs) != len(TIMINGS):
        raise SystemExit(f"Expected {len(TIMINGS)} lyric pairs, got {len(pairs)}")
    validate_timings()

    blocks = []
    for index, ((english, italian), (start, end)) in enumerate(zip(pairs, TIMINGS), start=1):
        lines = [str(index), f"{start} --> {end}", italian]
        if normalize(english) != normalize(italian):
            lines.append(english)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sidecar",
        action="store_true",
        help="Also replace the VLC sidecar in the iCloud-backed video/done directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = render()
    outputs = [CAPTION_OUT, WORK_OUT]
    if args.sidecar:
        outputs.append(SIDECAR_OUT)
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
