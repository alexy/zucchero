# AGENTS.md

## FirstPair Book Delivery

`FIRSTPAIR.md` is the required contract for this repository's unified book
build and FirstPair library deployment. Read and maintain it before changing or
delivering the book; it owns the catalog slug, shelf, and all source-side
handoff guidance. The shared implementation and authoritative operational rules
live in `~/src/firstpair`. Do not duplicate that deployment procedure here.

Guidance for future Codex runs in this repository.

## Repo Root

- The canonical repo is `/Users/alexy/src/zucchero`.
- Do not use `/Users/alexy/Documents/zucchero`; that was a stale wrong-start path.
- Verify the repo root before edits:

  ```sh
  pwd
  git rev-parse --show-toplevel
  ```

## Captioning Goal

This repo builds local Italian study captions for Zucchero videos. The preferred
finished subtitle format for lyric-aligned songs is:

```text
Italian lyric line
clean English translation line
```

Do not use word-by-word glosses for this lyric-aligned sidecar format unless the
user asks for gloss captions specifically.

When the English line is identical to the Italian line, such as `Yeah`, omit the
duplicate English line. This keeps the SRT from showing the same word twice.

## Copyright Boundary

- Do not paste full song lyrics into chat.
- It is OK to use local lyric files that the user provided to create local SRT
  files in the workspace.
- Keep generated lyric-containing outputs on disk and report paths, not full
  lyric text.

## Tools

Local ASR tools available on this machine:

```sh
/Users/alexy/.local/bin/mlx_whisper
/Users/alexy/.local/bin/parakeet-mlx
```

The local Whisper model lives at:

```text
models/whisper-large-v3-turbo
```

Use `ffprobe` to verify media duration:

```sh
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$MEDIA"
```

## ASR Workflow

Run both recognizers and treat their output as timing evidence, not lyric truth.
The supplied lyric file is the text authority.

Whisper example:

```sh
mkdir -p work/<YT_ID>/whisper-video
/Users/alexy/.local/bin/mlx_whisper "$MEDIA" \
  --model models/whisper-large-v3-turbo \
  --language Italian \
  --word-timestamps True \
  --output-format all \
  --output-name=<YT_ID> \
  --output-dir work/<YT_ID>/whisper-video \
  --verbose False
```

When a local lyric file exists and fresh timing evidence is actually needed,
run an additional prompted Whisper pass before building the final captions. If
only the English translation changed, do not rerun Whisper or Parakeet; rebuild
the SRT from the existing timings. For bilingual lyric files, use only the
Italian lyric lines as the initial prompt. Never include English translation
lines in an ASR prompt for these Italian songs. Disable previous-text
conditioning to reduce repeated-tail hallucinations:

```sh
PROMPT=$(python3 - <<'PY'
from pathlib import Path
lines = [line.strip() for line in Path("lyrics/<track>.<YT_ID>.en-it.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
print(" ".join(lines[1::2] if len(lines) % 2 == 0 else lines))
PY
)
mkdir -p work/<YT_ID>/whisper-prompted
/Users/alexy/.local/bin/mlx_whisper "$MEDIA" \
  --model models/whisper-large-v3-turbo \
  --language Italian \
  --initial-prompt "$PROMPT" \
  --condition-on-previous-text False \
  --word-timestamps True \
  --output-format all \
  --output-name=<YT_ID> \
  --output-dir work/<YT_ID>/whisper-prompted \
  --verbose False
```

Parakeet example:

```sh
mkdir -p work/<YT_ID>/parakeet-video
/Users/alexy/.local/bin/parakeet-mlx "$MEDIA" \
  --output-dir work/<YT_ID>/parakeet-video \
  --output-format all \
  --max-words 8 \
  --max-duration 5 \
  --silence-gap 0.45
```

The current `parakeet-mlx` CLI does not expose an initial-prompt or lyric-prompt
flag. Run it as timing evidence, then align those timings against the local
lyrics rather than treating Parakeet text as authoritative.

Known ASR behavior:

- Whisper usually gives better subtitle timing through the main body.
- Parakeet can catch missing words or phrase starts that Whisper drops.
- Parakeet can also produce unusable giant cues or overlapping cue fragments,
  especially on live/sung material.
- Whisper can hallucinate repeated outro text or filler syllables during long
  instrumental/vocalization sections.
- Use both outputs to place lyric lines, but keep the local `lyrics/*.en-it.txt`
  file as the caption text source.

## Lyric Files

The `.en-it.txt` lyric files are alternating English and Italian nonblank lines:

```text
English translation
Italian lyric

English translation
Italian lyric
```

Parse them as pairs, then render Italian first and English second in the SRT.
If a file is actually Italian-only despite its suffix, render one supplied
Italian lyric line per caption block and do not invent English translations.

Current examples:

- `lyrics/buio.Dz0Okxx9_u8.en-it.txt`
- `lyrics/blue.ke1YZYld0MY.en-it.txt`
- `lyrics/il-suono-della-domenica.qWPy_XDm0FQ.en-it.txt`

## Generated Builders

Track-specific reproducible builders currently exist for the lyric-aligned SRTs:

```sh
python3 tools/build_bilingual_lyrics_srt.py --top-level
python3 tools/build_13_buone_ragioni_en_it_srt.py
python3 tools/build_buio_en_it_srt.py
python3 tools/build_blu_en_it_srt.py
python3 tools/build_diamante_en_it_srt.py
python3 tools/build_amor_en_it_srt.py
python3 tools/build_vedo_en_it_srt.py
python3 tools/build_un_soffio_en_it_srt.py
python3 tools/build_il_suono_srt.py
```

These scripts write:

```text
captions/<YT_ID>.en-it.srt
captions/<YT_ID>.it.srt  # Italian-only lyric files
work/<YT_ID>/final/<YT_ID>.en-it.srt
work/<YT_ID>/final/<YT_ID>.it.srt  # Italian-only lyric files
```

For Blu, the builder also writes the final VLC sidecar directly next to the MP4.

For new batches with local `.en-it.txt` lyric files, prefer
`tools/build_bilingual_lyrics_srt.py --top-level` after the Whisper/Parakeet
timing passes. It compares available Whisper and Parakeet token timings,
chooses the stronger alignment per song, writes `captions/<YT_ID>.en-it.srt`
and `work/<YT_ID>/final/<YT_ID>.en-it.srt`, and validates block counts and
monotonic timings. Keep track-specific builders for older hand-tuned captions.

## Private Book Lyrics Appendix

To generate a private lyrics appendix from a local lyrics directory and rebuild
the local-only book package with First Pair's unified book builder:

```sh
./docs/book/build.sh --config book.private.build.json
```

The private config's prepare hook runs `tools/prepare_private_book.py`, which
writes `docs/book/private/song-list.tsv`,
`docs/book/private/song-list.md`, and
`docs/book/private/lyrics-appendix.md`, then renders the private generated
manuscript consumed by `~/src/firstpair/publishing/scripts/build-library-book.sh`.
The song list is generated from unique YouTube IDs found in local lyric files,
captions, `work/*/final/`, and VLC sidecars, and records title, YouTube URL,
lyric file, and chosen SRT file. The resulting private artifacts stay under
`docs/book/private/`, which is ignored by Git and not for First Pair upload.

## VLC Sidecars

For VLC auto-loading, copy the finished SRT next to the video with the exact same
basename as the MP4:

```text
video/done/Title [YT_ID].mp4
video/done/Title [YT_ID].srt
```

Verify the sidecar copy:

```sh
cmp -s captions/<YT_ID>.en-it.srt "video/done/Title [YT_ID].srt" && echo "sidecar copy identical"
```

Completed examples:

```text
video/done/Zucchero - Spirito Nel Buio [Dz0Okxx9_u8].srt
video/done/Zucchero - Blu (Live Acoustic) - Arena di Verona [ke1YZYld0MY].srt
```

## Validation

Before reporting done, validate:

- expected block count equals the lyric pair count
- timings are monotonic
- no zero-length or negative-length cues
- no duplicate English line remains when English and Italian normalize to the
  same text
- sidecar SRT is byte-identical to the generated caption

Use a quick Python validation script if needed. Report counts and paths, not the
full caption contents.
