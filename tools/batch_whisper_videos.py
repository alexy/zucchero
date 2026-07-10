#!/usr/bin/env python3
"""Batch-transcribe top-level videos with mlx_whisper.

Workflow:
1. Put videos in top-level video/.
2. Run this script with "transcribe".
3. Create final translated captions at work/<YT_ID>/final/<YT_ID>.word-by-word.srt.
4. Run this script with "move-done" to archive completed videos in video/done/
   and place identically named .srt sidecars next to them.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = ROOT / "video"
CAPTIONS_DIR = ROOT / "captions"
WORK_DIR = ROOT / "work"
DEFAULT_MLX = Path.home() / ".local" / "bin" / "mlx_whisper"
DEFAULT_MODEL = ROOT / "models" / "whisper-large-v3-turbo"
VIDEO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".mkv", ".webm"}
YOUTUBE_ID_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\](?:\.[^.]+)?$")


def youtube_id(path: Path) -> str:
    match = YOUTUBE_ID_RE.search(path.name)
    if match:
        return match.group(1)
    return re.sub(r"[^A-Za-z0-9_-]+", "-", path.stem).strip("-")


def top_level_videos() -> list[Path]:
    if not VIDEO_DIR.exists():
        return []
    return sorted(
        path
        for path in VIDEO_DIR.iterdir()
        if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS
    )


def final_caption_for(yt_id: str) -> Path:
    candidates = [
        WORK_DIR / yt_id / "final" / f"{yt_id}.en-it.srt",
        CAPTIONS_DIR / f"{yt_id}.en-it.srt",
        WORK_DIR / yt_id / "final" / f"{yt_id}.word-by-word.srt",
        CAPTIONS_DIR / f"{yt_id}.srt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


def run(command: list[str], dry_run: bool) -> None:
    print(" ".join(quote(part) for part in command))
    if not dry_run:
        subprocess.run(command, check=True)


def quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=,@+-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def transcribe(args: argparse.Namespace) -> None:
    mlx = Path(args.mlx_whisper).expanduser()
    model = Path(args.model).expanduser()
    videos = top_level_videos()
    if not videos:
        print(f"No top-level videos found in {VIDEO_DIR}")
        return

    for video in videos:
        yt_id = youtube_id(video)
        whisper_dir = WORK_DIR / yt_id / "whisper"
        transcript_path = whisper_dir / f"{yt_id}.txt"
        manifest_path = WORK_DIR / yt_id / "manifest.json"

        if transcript_path.exists() and not args.force:
            print(f"Skipping {yt_id}: {transcript_path} already exists")
            continue

        whisper_dir.mkdir(parents=True, exist_ok=True)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "youtube_id": yt_id,
                    "source_video": str(video),
                    "whisper_dir": str(whisper_dir),
                    "final_caption": str(WORK_DIR / yt_id / "final" / f"{yt_id}.word-by-word.srt"),
                    "done_video": str(VIDEO_DIR / "done" / video.name),
                    "done_subtitle": str((VIDEO_DIR / "done" / video.name).with_suffix(".srt")),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        command = [
            str(mlx),
            str(video),
            "--model",
            str(model),
            "--language",
            args.language,
            "--word-timestamps",
            "True",
            "--output-format",
            "all",
            f"--output-name={yt_id}",
            "--output-dir",
            str(whisper_dir),
            "--verbose",
            str(args.verbose),
        ]
        run(command, args.dry_run)


def move_done(args: argparse.Namespace) -> None:
    done_dir = VIDEO_DIR / "done"
    done_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for video in top_level_videos():
        yt_id = youtube_id(video)
        final_caption = final_caption_for(yt_id)
        if not final_caption.exists():
            print(f"Not done {yt_id}: missing {final_caption}")
            continue
        destination = done_dir / video.name
        subtitle_destination = destination.with_suffix(".srt")
        if destination.exists():
            raise SystemExit(f"Refusing to overwrite existing file: {destination}")
        if subtitle_destination.exists():
            raise SystemExit(f"Refusing to overwrite existing file: {subtitle_destination}")
        print(f"Moving {video} -> {destination}")
        print(f"Copying {final_caption} -> {subtitle_destination}")
        if not args.dry_run:
            shutil.move(str(video), str(destination))
            shutil.copy2(str(final_caption), str(subtitle_destination))
        moved += 1
    print(f"Moved {moved} completed video(s)")


def sync_sidecars(args: argparse.Namespace) -> None:
    done_dir = VIDEO_DIR / "done"
    if not done_dir.exists():
        print(f"No done directory: {done_dir}")
        return
    synced = 0
    for video in sorted(path for path in done_dir.iterdir() if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS):
        yt_id = youtube_id(video)
        final_caption = final_caption_for(yt_id)
        if not final_caption.exists():
            print(f"Skipping {yt_id}: missing {final_caption}")
            continue
        subtitle_destination = video.with_suffix(".srt")
        print(f"Copying {final_caption} -> {subtitle_destination}")
        if not args.dry_run:
            shutil.copy2(str(final_caption), str(subtitle_destination))
        synced += 1
    print(f"Synced {synced} sidecar subtitle(s)")


def status(_: argparse.Namespace) -> None:
    for video in top_level_videos():
        yt_id = youtube_id(video)
        transcript = WORK_DIR / yt_id / "whisper" / f"{yt_id}.txt"
        final_caption = final_caption_for(yt_id)
        print(
            f"{yt_id}\t"
            f"video=yes\t"
            f"whisper={'yes' if transcript.exists() else 'no'}\t"
            f"caption={'yes' if final_caption.exists() else 'no'}\t"
            f"{video.name}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(required=True)

    transcribe_parser = subparsers.add_parser("transcribe", help="Run mlx_whisper for top-level videos")
    transcribe_parser.add_argument("--mlx-whisper", default=str(DEFAULT_MLX))
    transcribe_parser.add_argument("--model", default=str(DEFAULT_MODEL))
    transcribe_parser.add_argument("--language", default="Italian")
    transcribe_parser.add_argument("--verbose", default="False")
    transcribe_parser.add_argument("--force", action="store_true", help="Re-run even when transcript exists")
    transcribe_parser.add_argument("--dry-run", action="store_true")
    transcribe_parser.set_defaults(func=transcribe)

    move_parser = subparsers.add_parser("move-done", help="Move videos with captions/<YT_ID>.srt to video/done/")
    move_parser.add_argument("--dry-run", action="store_true")
    move_parser.set_defaults(func=move_done)

    sidecar_parser = subparsers.add_parser("sync-sidecars", help="Copy final captions next to videos in video/done/")
    sidecar_parser.add_argument("--dry-run", action="store_true")
    sidecar_parser.set_defaults(func=sync_sidecars)

    status_parser = subparsers.add_parser("status", help="Show video/transcript/final-caption state")
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
