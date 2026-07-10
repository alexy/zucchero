#!/usr/bin/env python3
"""Create a blank SRT timing skeleton from local media using ffmpeg silence detection."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


SILENCE_RE = re.compile(r"silence_(start|end):\s*([0-9.]+)")


@dataclass
class Segment:
    start: float
    end: float


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def media_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(result.stdout.strip())


def detect_silences(path: Path, noise: str, min_silence: float) -> list[Segment]:
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            f"silencedetect=noise={noise}:d={min_silence}",
            "-f",
            "null",
            "-",
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    events: list[tuple[str, float]] = []
    for match in SILENCE_RE.finditer(result.stderr):
        events.append((match.group(1), float(match.group(2))))

    silences: list[Segment] = []
    open_start: float | None = None
    for kind, value in events:
        if kind == "start":
            open_start = value
        elif kind == "end" and open_start is not None:
            silences.append(Segment(open_start, value))
            open_start = None
    duration = media_duration(path)
    if open_start is not None:
        silences.append(Segment(open_start, duration))
    return silences


def invert_silences(silences: list[Segment], duration: float, padding: float) -> list[Segment]:
    active: list[Segment] = []
    cursor = 0.0
    for silence in silences:
        if silence.start > cursor:
            active.append(Segment(max(0.0, cursor - padding), min(duration, silence.start + padding)))
        cursor = max(cursor, silence.end)
    if cursor < duration:
        active.append(Segment(max(0.0, cursor - padding), duration))
    return active


def split_long_segments(segments: list[Segment], max_len: float) -> list[Segment]:
    split: list[Segment] = []
    for segment in segments:
        start = segment.start
        while segment.end - start > max_len:
            split.append(Segment(start, start + max_len))
            start += max_len
        if segment.end - start > 0.25:
            split.append(Segment(start, segment.end))
    return split


def merge_short_gaps(segments: list[Segment], max_gap: float) -> list[Segment]:
    if not segments:
        return []
    merged = [segments[0]]
    for segment in segments[1:]:
        previous = merged[-1]
        if segment.start - previous.end <= max_gap:
            previous.end = segment.end
        else:
            merged.append(segment)
    return merged


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def write_srt(segments: list[Segment], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for index, segment in enumerate(segments, 1):
        blocks.append(
            f"{index}\n"
            f"{timestamp(segment.start)} --> {timestamp(segment.end)}\n"
            "[caption]\n"
        )
    destination.write_text("\n".join(blocks), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="Local video or audio file")
    parser.add_argument("destination", type=Path, help="Output blank .srt file")
    parser.add_argument("--noise", default="-32dB", help="ffmpeg silencedetect noise threshold")
    parser.add_argument("--min-silence", type=float, default=0.45, help="Minimum silence length in seconds")
    parser.add_argument("--padding", type=float, default=0.08, help="Seconds to pad active regions")
    parser.add_argument("--merge-gap", type=float, default=0.25, help="Merge active regions separated by this gap")
    parser.add_argument("--max-len", type=float, default=5.0, help="Split active regions longer than this")
    args = parser.parse_args()

    duration = media_duration(args.media)
    silences = detect_silences(args.media, args.noise, args.min_silence)
    active = invert_silences(silences, duration, args.padding)
    active = merge_short_gaps(active, args.merge_gap)
    active = split_long_segments(active, args.max_len)
    write_srt(active, args.destination)


if __name__ == "__main__":
    main()

