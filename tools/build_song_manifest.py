#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "docs" / "book"
PRIVATE_DIR = BOOK_DIR / "private"
YOUTUBE_ID_RE = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])")


@dataclass(frozen=True)
class SongRow:
    title: str
    youtube_id: str
    youtube_url: str
    lyrics_file: str
    srt_file: str


def relative_display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def extract_youtube_id(value: str) -> str | None:
    match = YOUTUBE_ID_RE.search(value)
    return match.group(1) if match else None


def title_from_slug(value: str) -> str:
    value = re.sub(r"\.(?:en-it|it|en)$", "", value)
    value = re.sub(r"\.[A-Za-z0-9_-]{11}$", "", value)
    value = re.sub(r"\[[A-Za-z0-9_-]{11}\]", "", value)
    value = re.sub(r"^\s*Zucchero\s*-\s*", "", value, flags=re.IGNORECASE)
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value.title() if value else ""


def title_from_path(path: Path) -> str:
    return title_from_slug(path.stem) or path.stem


def read_existing_index(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    return {row["youtube_id"]: row for row in rows if row.get("youtube_id")}


def paths_by_id(paths: list[Path]) -> dict[str, list[Path]]:
    by_id: dict[str, list[Path]] = {}

    for path in paths:
        youtube_id = extract_youtube_id(path.name)

        if not youtube_id:
            continue

        by_id.setdefault(youtube_id, []).append(path)

    return by_id


def find_lyric_files(lyrics_dir: Path) -> list[Path]:
    if not lyrics_dir.exists():
        return []

    return sorted(path for path in lyrics_dir.rglob("*.txt") if path.is_file())


def find_srt_files() -> list[Path]:
    roots = [ROOT / "captions", ROOT / "work", ROOT / "video" / "done"]
    files: list[Path] = []

    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*.srt") if path.is_file())

    return sorted(files)


def lyric_priority(path: Path, youtube_id: str, existing: dict[str, str] | None) -> tuple[int, str]:
    rel = relative_display_path(path)

    if existing and existing.get("local_lyric_file") == rel:
        return (-10, rel)
    if f".{youtube_id}.en-it.txt" in path.name:
        return (0, rel)
    if f".{youtube_id}.it.txt" in path.name:
        return (1, rel)
    return (9, rel)


def srt_priority(path: Path, youtube_id: str, existing: dict[str, str] | None) -> tuple[int, str]:
    rel = relative_display_path(path)

    if existing and existing.get("caption_file") == rel:
        return (-10, rel)
    if rel == f"captions/{youtube_id}.en-it.srt":
        return (0, rel)
    if rel == f"captions/{youtube_id}.it.srt":
        return (1, rel)
    if rel == f"captions/{youtube_id}.srt":
        return (2, rel)
    if rel == f"work/{youtube_id}/final/{youtube_id}.en-it.srt":
        return (3, rel)
    if rel == f"work/{youtube_id}/final/{youtube_id}.it.srt":
        return (4, rel)
    if rel.startswith(f"captions/final/{youtube_id}."):
        return (5, rel)
    if rel.startswith(f"work/{youtube_id}/final/"):
        return (6, rel)
    if rel.startswith("video/done/"):
        return (7, rel)
    return (20, rel)


def choose_path(candidates: list[Path], youtube_id: str, existing: dict[str, str] | None, priority) -> Path | None:
    if not candidates:
        return None

    return sorted(candidates, key=lambda path: priority(path, youtube_id, existing))[0]


def title_for_song(
    youtube_id: str,
    existing: dict[str, str] | None,
    lyric_path: Path | None,
    srt_path: Path | None,
) -> str:
    if existing and existing.get("title"):
        return existing["title"]
    if lyric_path:
        return title_from_path(lyric_path)
    if srt_path:
        return title_from_path(srt_path)
    return youtube_id


def title_path_from_srts(candidates: list[Path]) -> Path | None:
    if not candidates:
        return None

    def priority(path: Path) -> tuple[int, str]:
        rel = relative_display_path(path)
        if rel.startswith("video/done/"):
            return (0, rel)
        if "[" in path.name and "]" in path.name:
            return (1, rel)
        if rel.startswith("work/"):
            return (2, rel)
        return (9, rel)

    return sorted(candidates, key=priority)[0]


def build_song_rows(lyrics_dir: Path, existing_index: Path = BOOK_DIR / "lyric-index.tsv") -> list[SongRow]:
    existing = read_existing_index(existing_index)
    lyrics_by_id = paths_by_id(find_lyric_files(lyrics_dir))
    srts_by_id = paths_by_id(find_srt_files())
    youtube_ids = set(existing) | set(lyrics_by_id) | set(srts_by_id)
    rows: list[SongRow] = []

    for youtube_id in sorted(youtube_ids):
        known = existing.get(youtube_id)
        lyric_path = choose_path(lyrics_by_id.get(youtube_id, []), youtube_id, known, lyric_priority)
        srt_candidates = srts_by_id.get(youtube_id, [])
        srt_path = choose_path(srt_candidates, youtube_id, known, srt_priority)
        title_srt_path = title_path_from_srts(srt_candidates) or srt_path
        title = title_for_song(youtube_id, known, lyric_path, title_srt_path)
        rows.append(
            SongRow(
                title=title,
                youtube_id=youtube_id,
                youtube_url=f"https://www.youtube.com/watch?v={youtube_id}",
                lyrics_file=relative_display_path(lyric_path) if lyric_path else "",
                srt_file=relative_display_path(srt_path) if srt_path else "",
            )
        )

    return sorted(rows, key=lambda row: (row.title.casefold(), row.youtube_id))


def render_tsv(rows: list[SongRow]) -> str:
    lines = ["title\tyoutube_id\tyoutube_url\tlyrics_file\tsrt_file"]
    for row in rows:
        lines.append(
            "\t".join(
                [
                    row.title,
                    row.youtube_id,
                    row.youtube_url,
                    row.lyrics_file,
                    row.srt_file,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_markdown(rows: list[SongRow]) -> str:
    lines = [
        "## Private Song File Inventory",
        "",
        "Generated from unique YouTube IDs found in local lyric and subtitle files.",
        "",
        "| Song | YouTube | Lyrics file | SRT file |",
        "| --- | --- | --- | --- |",
    ]

    for row in rows:
        lyrics = f"`{row.lyrics_file}`" if row.lyrics_file else "_missing_"
        srt = f"`{row.srt_file}`" if row.srt_file else "_missing_"
        lines.append(f"| {row.title} | [watch]({row.youtube_url}) | {lyrics} | {srt} |")

    return "\n".join(lines) + "\n"


def write_song_manifest(lyrics_dir: Path, out_dir: Path = PRIVATE_DIR) -> list[SongRow]:
    rows = build_song_rows(lyrics_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "song-list.tsv").write_text(render_tsv(rows), encoding="utf-8")
    (out_dir / "song-list.md").write_text(render_markdown(rows), encoding="utf-8")
    print(f"Generated {out_dir / 'song-list.tsv'} from {len(rows)} unique YouTube IDs")
    print(f"Generated {out_dir / 'song-list.md'} from {len(rows)} unique YouTube IDs")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the private song file inventory from local YouTube IDs."
    )
    parser.add_argument(
        "--lyrics-dir",
        type=Path,
        default=ROOT / "lyrics",
        help="Directory containing local lyric files. Defaults to lyrics/.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PRIVATE_DIR,
        help="Output directory for song-list.tsv and song-list.md.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_song_manifest(args.lyrics_dir.expanduser().resolve(), args.out_dir.expanduser().resolve())


if __name__ == "__main__":
    main()
