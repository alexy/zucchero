#!/usr/bin/env python3
"""Build Italian/English lyric captions from local lyrics and Whisper timings."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LYRICS_DIR = ROOT / "lyrics"
VIDEO_DIR = ROOT / "video"
WORK_DIR = ROOT / "work"
CAPTIONS_DIR = ROOT / "captions"
VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".mkv", ".webm"}
YOUTUBE_ID_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\](?:\.[^.]+)?$")
LYRIC_ID_RE = re.compile(r"\.([A-Za-z0-9_-]{11})\.en-it\.txt$")
WORD_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class WordTime:
    token: str
    start: float
    end: float


@dataclass(frozen=True)
class LyricToken:
    token: str
    line_index: int


@dataclass(frozen=True)
class BuildResult:
    youtube_id: str
    lyric_file: Path
    timing_source: str
    pairs: int
    lyric_tokens: int
    matched_tokens: int
    matched_lines: int
    output: Path
    work_output: Path


def youtube_id(path: Path) -> str | None:
    match = YOUTUBE_ID_RE.search(path.name)
    return match.group(1) if match else None


def youtube_id_from_lyrics(path: Path) -> str | None:
    match = LYRIC_ID_RE.search(path.name)
    return match.group(1) if match else None


def normalize_token(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return "".join(WORD_RE.findall(without_marks))


def tokens(text: str) -> list[str]:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return [piece for piece in WORD_RE.findall(without_marks) if piece]


def parse_pairs(path: Path) -> list[tuple[str, str]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) % 2:
        raise SystemExit(f"{path}: expected alternating English/Italian lines, got {len(lines)} nonblank lines")
    return [(lines[index], lines[index + 1]) for index in range(0, len(lines), 2)]


def lyric_tokens(pairs: list[tuple[str, str]]) -> list[LyricToken]:
    flattened: list[LyricToken] = []
    for line_index, (_, italian) in enumerate(pairs):
        flattened.extend(LyricToken(token=token, line_index=line_index) for token in tokens(italian))
    return flattened


def whisper_json_for(youtube_id_value: str) -> Path:
    candidates = [
        WORK_DIR / youtube_id_value / "whisper-prompted" / f"{youtube_id_value}.json",
        WORK_DIR / youtube_id_value / "whisper" / f"{youtube_id_value}.json",
        WORK_DIR / youtube_id_value / "whisper-video" / f"{youtube_id_value}.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(f"{youtube_id_value}: no Whisper JSON found in work/{youtube_id_value}/")


def whisper_words(path: Path) -> list[WordTime]:
    data = json.loads(path.read_text(encoding="utf-8"))
    output: list[WordTime] = []
    for segment in data.get("segments", []):
        for word in segment.get("words", []):
            token = normalize_token(str(word.get("word", "")))
            if not token:
                continue
            start = float(word.get("start", segment.get("start", 0.0)))
            end = float(word.get("end", segment.get("end", start + 0.5)))
            if end <= start:
                end = start + 0.5
            output.append(WordTime(token=token, start=start, end=end))
    if not output:
        raise SystemExit(f"{path}: no word timestamps found")
    return output


def parakeet_jsons_for(youtube_id_value: str) -> list[Path]:
    parakeet_dir = WORK_DIR / youtube_id_value / "parakeet-video"
    if not parakeet_dir.exists():
        return []
    return sorted(parakeet_dir.glob("*.json"))


def parakeet_words(path: Path) -> list[WordTime]:
    data = json.loads(path.read_text(encoding="utf-8"))
    output: list[WordTime] = []
    for sentence in data.get("sentences", []):
        for token_info in sentence.get("tokens", []):
            token = normalize_token(str(token_info.get("text", "")))
            if not token:
                continue
            start = float(token_info.get("start", sentence.get("start", 0.0)))
            end = float(token_info.get("end", sentence.get("end", start + 0.5)))
            if end <= start:
                end = start + 0.5
            output.append(WordTime(token=token, start=start, end=end))
    return output


def timing_sources_for(youtube_id_value: str) -> list[tuple[str, list[WordTime]]]:
    sources = [(str(whisper_json_for(youtube_id_value).relative_to(ROOT)), whisper_words(whisper_json_for(youtube_id_value)))]
    for path in parakeet_jsons_for(youtube_id_value):
        words = parakeet_words(path)
        if words:
            sources.append((str(path.relative_to(ROOT)), words))
    return sources


def edit_distance_at_most_one(left: str, right: str) -> bool:
    if abs(len(left) - len(right)) > 1:
        return False
    if left == right:
        return True
    edits = 0
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(left) == len(right):
            i += 1
            j += 1
        elif len(left) < len(right):
            j += 1
        else:
            i += 1
    return edits + (len(left) - i) + (len(right) - j) <= 1


def token_score(left: str, right: str) -> float:
    if left == right:
        return 4.0
    if min(len(left), len(right)) >= 5 and edit_distance_at_most_one(left, right):
        return 2.0
    if min(len(left), len(right)) >= 5 and (left.startswith(right[:5]) or right.startswith(left[:5])):
        return 1.25
    return -2.0


def align_tokens(lyric: list[LyricToken], words: list[WordTime]) -> dict[int, int]:
    gap = -0.65
    rows = len(lyric) + 1
    cols = len(words) + 1
    scores = [[0.0] * cols for _ in range(rows)]
    back = [[""] * cols for _ in range(rows)]

    for i in range(1, rows):
        scores[i][0] = scores[i - 1][0] + gap
        back[i][0] = "up"
    for j in range(1, cols):
        scores[0][j] = scores[0][j - 1] + gap
        back[0][j] = "left"

    for i in range(1, rows):
        left_token = lyric[i - 1].token
        for j in range(1, cols):
            match_score = token_score(left_token, words[j - 1].token)
            choices = [
                (scores[i - 1][j - 1] + match_score, "diag"),
                (scores[i - 1][j] + gap, "up"),
                (scores[i][j - 1] + gap, "left"),
            ]
            scores[i][j], back[i][j] = max(choices, key=lambda item: item[0])

    matches: dict[int, int] = {}
    i = len(lyric)
    j = len(words)
    while i > 0 or j > 0:
        direction = back[i][j]
        if direction == "diag":
            if token_score(lyric[i - 1].token, words[j - 1].token) > 0:
                matches[i - 1] = j - 1
            i -= 1
            j -= 1
        elif direction == "up":
            i -= 1
        else:
            j -= 1
    return matches


def seconds_to_srt(value: float) -> str:
    value = max(0.0, value)
    milliseconds = round(value * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def line_timings(
    pairs: list[tuple[str, str]],
    flat_lyrics: list[LyricToken],
    words: list[WordTime],
    matches: dict[int, int],
) -> tuple[list[tuple[float, float]], int]:
    line_matches: list[list[int]] = [[] for _ in pairs]
    for lyric_index, word_index in matches.items():
        line_matches[flat_lyrics[lyric_index].line_index].append(word_index)

    timings: list[tuple[float | None, float | None]] = []
    matched_lines = 0
    for word_indexes in line_matches:
        if word_indexes:
            matched_lines += 1
            timings.append(
                (
                    min(words[index].start for index in word_indexes),
                    max(words[index].end for index in word_indexes),
                )
            )
        else:
            timings.append((None, None))

    average_duration = 2.6
    last_word_end = max(word.end for word in words)
    resolved: list[tuple[float, float]] = [(0.0, 0.0)] * len(timings)
    anchors = [index for index, (start, end) in enumerate(timings) if start is not None and end is not None]

    if not anchors:
        for index in range(len(timings)):
            start = index * average_duration
            resolved[index] = (start, min(start + average_duration, last_word_end + average_duration))
    else:
        first = anchors[0]
        first_start = timings[first][0] or 0.0
        for index in range(first):
            start = max(0.0, first_start - (first - index) * average_duration)
            resolved[index] = (start, min(start + average_duration, first_start - 0.05))

        for left, right in zip(anchors, anchors[1:]):
            left_start, left_end = timings[left]
            right_start, _ = timings[right]
            resolved[left] = (float(left_start), float(left_end))
            gap_count = right - left - 1
            if gap_count:
                available_start = float(left_end) + 0.08
                available_end = max(available_start + gap_count * 0.5, float(right_start) - 0.08)
                step = (available_end - available_start) / gap_count
                for offset in range(gap_count):
                    start = available_start + offset * step
                    resolved[left + offset + 1] = (start, min(start + step * 0.85, available_end))

        last = anchors[-1]
        last_start, last_end = timings[last]
        resolved[last] = (float(last_start), float(last_end))
        for index in range(last + 1, len(timings)):
            start = resolved[index - 1][1] + 0.2
            resolved[index] = (start, min(start + average_duration, last_word_end + average_duration))

    for index, (start, end) in enumerate(resolved):
        start = max(0.0, start - 0.04)
        end = max(start + 0.55, end + 0.08)
        resolved[index] = (start, end)

    for index in range(len(resolved) - 1):
        start, end = resolved[index]
        next_start, next_end = resolved[index + 1]
        if next_start <= start:
            next_start = start + 0.6
        if end >= next_start - 0.04:
            end = max(start + 0.45, next_start - 0.04)
        resolved[index] = (start, end)
        resolved[index + 1] = (next_start, max(next_start + 0.55, next_end))

    previous_end = -0.04
    for index, (start, end) in enumerate(resolved):
        if start < previous_end + 0.04:
            start = previous_end + 0.04
        if end <= start + 0.45:
            end = start + 0.45
        resolved[index] = (start, end)
        previous_end = end

    return resolved, matched_lines


def normalized_text(text: str) -> str:
    return " ".join(tokens(text))


def render_srt(pairs: list[tuple[str, str]], timings: list[tuple[float, float]]) -> str:
    blocks: list[str] = []
    for index, ((english, italian), (start, end)) in enumerate(zip(pairs, timings), start=1):
        lines = [str(index), f"{seconds_to_srt(start)} --> {seconds_to_srt(end)}", italian]
        if normalized_text(english) != normalized_text(italian):
            lines.append(english)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def build_one(lyric_file: Path) -> BuildResult:
    yt_id = youtube_id_from_lyrics(lyric_file)
    if not yt_id:
        raise SystemExit(f"{lyric_file}: could not find YouTube ID in filename")

    pairs = parse_pairs(lyric_file)
    flat = lyric_tokens(pairs)
    best: tuple[str, list[WordTime], dict[int, int], list[tuple[float, float]], int] | None = None
    for source_name, words in timing_sources_for(yt_id):
        matches = align_tokens(flat, words)
        timings, matched_lines = line_timings(pairs, flat, words, matches)
        candidate = (source_name, words, matches, timings, matched_lines)
        if best is None:
            best = candidate
            continue
        if (matched_lines, len(matches)) > (best[4], len(best[2])):
            best = candidate

    if best is None:
        raise SystemExit(f"{yt_id}: no usable timing sources found")

    source_name, _, matches, timings, matched_lines = best
    srt = render_srt(pairs, timings)

    caption_out = CAPTIONS_DIR / f"{yt_id}.en-it.srt"
    work_out = WORK_DIR / yt_id / "final" / f"{yt_id}.en-it.srt"
    for path in (caption_out, work_out):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(srt, encoding="utf-8")

    return BuildResult(
        youtube_id=yt_id,
        lyric_file=lyric_file,
        timing_source=source_name,
        pairs=len(pairs),
        lyric_tokens=len(flat),
        matched_tokens=len(matches),
        matched_lines=matched_lines,
        output=caption_out,
        work_output=work_out,
    )


def top_level_video_ids() -> set[str]:
    if not VIDEO_DIR.exists():
        return set()
    ids: set[str] = set()
    for path in VIDEO_DIR.iterdir():
        if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS:
            if found := youtube_id(path):
                ids.add(found)
    return ids


def lyric_files_for_top_level_videos() -> list[Path]:
    ids = top_level_video_ids()
    files = []
    for path in sorted(LYRICS_DIR.glob("*.en-it.txt")):
        if youtube_id_from_lyrics(path) in ids:
            files.append(path)
    return files


def validate_result(result: BuildResult) -> None:
    blocks = re.split(r"\n\s*\n", result.output.read_text(encoding="utf-8").strip())
    if len(blocks) != result.pairs:
        raise SystemExit(f"{result.youtube_id}: expected {result.pairs} SRT blocks, got {len(blocks)}")

    previous_end = -1.0
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            raise SystemExit(f"{result.youtube_id}: malformed SRT block")
        timing = lines[1]
        match = re.match(
            r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)$",
            timing,
        )
        if not match:
            raise SystemExit(f"{result.youtube_id}: malformed timing {timing}")
        parts = [int(part) for part in match.groups()]
        start = parts[0] * 3600 + parts[1] * 60 + parts[2] + parts[3] / 1000
        end = parts[4] * 3600 + parts[5] * 60 + parts[6] + parts[7] / 1000
        if end <= start:
            raise SystemExit(f"{result.youtube_id}: non-positive cue duration")
        if start < previous_end:
            raise SystemExit(f"{result.youtube_id}: non-monotonic cue timing")
        previous_end = end


def run_ffprobe(path: Path) -> float | None:
    try:
        output = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            text=True,
        ).strip()
        return float(output)
    except (subprocess.CalledProcessError, ValueError):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lyrics", nargs="*", type=Path, help="Specific .en-it.txt lyric files to build")
    parser.add_argument("--top-level", action="store_true", help="Build lyric captions for top-level video/ files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lyric_files = [path.expanduser() for path in args.lyrics]
    if args.top_level:
        lyric_files.extend(lyric_files_for_top_level_videos())
    if not lyric_files:
        raise SystemExit("No lyric files selected; pass files or use --top-level")

    seen: set[Path] = set()
    for lyric_file in lyric_files:
        lyric_file = lyric_file.resolve()
        if lyric_file in seen:
            continue
        seen.add(lyric_file)
        result = build_one(lyric_file)
        validate_result(result)
        print(
            "built {id}: pairs={pairs}, matched_lines={matched}/{total}, "
            "matched_tokens={tokens}/{all_tokens}, source={source}, output={output}, work={work}".format(
                id=result.youtube_id,
                pairs=result.pairs,
                matched=result.matched_lines,
                total=result.pairs,
                tokens=result.matched_tokens,
                all_tokens=result.lyric_tokens,
                source=result.timing_source,
                output=result.output,
                work=result.work_output,
            )
        )


if __name__ == "__main__":
    main()
